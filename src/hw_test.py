#!/usr/bin/env python
import time
import sys

from sys import path
path.append("hydra/src/main/python")
from hydra.lib.runtestbase import HydraBase
from ConfigParser import ConfigParser
from hydra.lib.h_analyser import HAnalyser
tout_60s = 60000


class HWSubAnalyser(HAnalyser):
    def __init__(self, server_ip, server_port, task_id):
        HAnalyser.__init__(self, server_ip, server_port, task_id)


class HWPubAnalyser(HAnalyser):
    def __init__(self, server_ip, server_port, task_id):
        HAnalyser.__init__(self, server_ip, server_port, task_id)


class HW(HydraBase):
    def __init__(self, pub_port):
        # Object contains 'configurations' parsed from hydra.ini config file.
        self.config = ConfigParser()
        # Pub/Subs are launched on Hydra slaves. So, you need the packages there. HydraBase will tar your local
        # repositorie's and copy it to the slaves.
        HydraBase.__init__(self, test_name='HelloWorld', options=None, app_dirs=['src', 'hydra'])
        # publisher will send messages to subscribers using this port. Subscribers need to subscribe to this port to
        # receive messages from publisher.
        self.pub_port = pub_port  # data port
        # Name of the apps. In hydra.ini, if you define prefix, then that prefix will be appeneded here. So, ultimate
        # name might be g1/hw-sub.
        self.hw_sub_app_id = self.format_appname("/hw-sub")
        self.hw_pub_app_id = self.format_appname("/hw-pub")
        # Value would be filled in launch_hw_sub() after function launches the sub app.
        self.hw_sub_task_ip = None
        self.hw_pub_task_ip = None
        # control ports. While launching app, you can ask mesos to assign some ports to application by providing a list
        # like ports[0, 0, 0].
        # We use such assigned port for our control traffic. Using these ports, you can send signals to pub/sub for
        # various things like (start_test, get_stats) etc.
        self.hw_sub_cmd_port = None
        self.hw_pub_cmd_port = None
        # HAnalyzers are there to communicate over ZMQ sockets. You can send signals to your pub/subs using this.
        # It uses the control ports as argument.
        self.hwpa = None  # Pub Analyzer
        self.hwsa = None  # Sub Analyzer
        # Add app_ids such that apps can be deleted at end of the test case.
        self.add_appid(self.hw_sub_app_id)
        self.add_appid(self.hw_pub_app_id)

    def run_test(self):
        """
        Function which actually runs
        """
        # Get Mesos/Marathon client
        self.start_init()
        # Launch HelloWorld Pub
        self.launch_hw_pub()
        # Launch HelloWorld Sub
        self.launch_hw_sub()

    def launch_hw_pub(self):
        """
        Function to launch helloWorld pub app.
        """
        print ("Launching the HelloWorld pub app")
        self.create_binary_app(name=self.hw_pub_app_id, app_script='./src/hw_pub.py %s' % self.pub_port,
                               cpus=0.01, mem=32,
                               ports=[0])
        # On application creation, assigned ports for the application is saved in ipport_map data structure. Call
        # the function to get ipm (Ip Port Map). Use the assigned port to create HAnalyzer.
        ipm = self.get_app_ipport_map(self.hw_pub_app_id)
        assert (len(ipm) == 1)
        # ipm dict has keys taskid_PORT_0, taskid_PORT_1 etc. and values as a list having [port, ip]
        self.hw_pub_task_ip = ipm.values()[0][1]
        self.hw_pub_cmd_port = str(ipm.values()[0][0])
        print("[helloworldtest.hw_pub] hw_pub running at [%s:%s]" % (self.hw_pub_task_ip, self.hw_pub_cmd_port))
        # Start helloworld Pub analyzer. You can pass signals to your plublisher. For our example, we will pass sendmsg
        # signal to publisher. You can see the signal handler for this message in hw_pub.
        self.hwpa = HWPubAnalyser(self.hw_pub_task_ip, self.hw_pub_cmd_port, self.hw_pub_app_id)

    def launch_hw_sub(self):
        """
        Function to launch helloWorld pub app.
        """
        print ("Launching the HelloWorld sub app")
        # Use cluster 1 for launching the SUB
        self.create_binary_app(name=self.hw_sub_app_id,
                               app_script='./src/hw_sub.py %s %s' % (self.hw_pub_task_ip, self.pub_port),
                               cpus=0.01, mem=32,
                               ports=[0])
        ipm = self.get_app_ipport_map(self.hw_sub_app_id)
        assert (len(ipm) == 1)
        print ("ipm=%s" % ipm)
        self.hw_sub_task_ip = ipm.values()[0][1]
        self.hw_sub_cmd_port = str(ipm.values()[0][0])
        print("[helloworldtest.hw_sub] hw_sub running at [%s:%s]", self.hw_sub_task_ip,
              self.hw_sub_cmd_port)
        self.hwsa = HWSubAnalyser(self.hw_sub_task_ip, self.hw_sub_cmd_port, self.hw_sub_app_id)


class RunTest(object):
    def __init__(self, argv):
        # ZMQ publisher port
        pub_port = ""
        num_msgs = ""
        if len(argv) > 2:
            pub_port = argv[1]
            num_msgs = int(argv[2])
        if not pub_port:
            pub_port = 1555
        if not num_msgs:
            num_msgs = 10

        r = HW(pub_port)
        # Start appserver. This server is responsible to send your code to Mesos slaves such that Hydra package
        # library becomes accessbile there.
        r.start_appserver()
        # Run actual tests. Launch publisher, subscriber.
        r.run_test()
        # Using publisher analyzer, communicate sendmsg signal to publisher. In signal handler, Publisher will start
        # sending 'arg1' number of messages to subscriber.
        print ("Communicating sendmsg signal to pub")
        r.hwpa.do_req_resp('sendmsg', tout_60s, arg1=num_msgs)
        # Ask subscriber about how many messages publisher had communicated to him? All you need to do is to send
        # getstas signal to subscriber.
        print ("Communicating getstats signal to sub")
        num_retries = 10
        for retry in range(num_retries):
            (status, resp) = r.hwsa.do_req_resp('getstats', tout_60s)
            if num_msgs == int(resp):
                print ("***** PASS: Publisher sent %s messages. subscriber received %s messages. *****"
                       % (num_msgs, resp))
                break
            elif retry == num_retries - 1:
                print ("==> FAILURE: expected %s != returned %s <==" % (num_msgs, resp))
            time.sleep(1)

        # Finally delete all applications pub/sub.
        r.delete_all_launched_apps()
        r.stop_appserver()

if __name__ == "__main__":
    RunTest(sys.argv)
