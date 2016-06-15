#!/usr/bin/env python

import time

from hydra.lib.runtestbase import RunTestBase
from ConfigParser import ConfigParser


class HW(RunTestBase):
    def __init__(self):
        self.config = ConfigParser()  # Object contains 'configurations' parsed from hydra.ini config file
        RunTestBase.__init__(self, test_name='HelloWorld', options=None, app_dirs=['src'])
        self.hw_server_app_id = self.format_appname("/hw-server")
        self.hw_client_app_id = self.format_appname("/hw-client")
        self.hw_server_task_ip = None
        self.hw_server_task_port = None
        self.hw_client_task_ip = None
        self.hw_client_task_port = None
        self.add_appid(self.hw_server_app_id)
        self.add_appid(self.hw_client_app_id)

    def run_test(self):
        # Get Mesos/Marathon client
        self.start_init()
        # Launch HelloWorld server
        self.launch_hw_server()
        # Launch HelloWorld client
        self.launch_hw_client()

    def launch_hw_server(self):
        print ("Launching the HelloWorld server app")
        # Use cluster0 for launching the hw_server
        # field: slave_id, operator: CLUSTER, value: slave-set1_0
        self.create_binary_app(name=self.hw_server_app_id, app_script='./src/hw_server.py',
                              cpus=0.01, mem=32,
                              ports=[0])

        ipm = self.get_app_ipport_map(self.hw_server_app_id)
        assert (len(ipm) == 1)

        self.hw_server_task_ip = ipm.values()[0][1]
        self.hw_server_task_port = str(ipm.values()[0][0])
        print("[helloworldtest.hw_server] hw_server running at [%s:%s]", self.hw_server_task_ip,
              self.hw_server_task_port)
        # Get IP port of launched task of hw_server.
        # tasks = self.get_app_tasks(self.hw_server_app_id)
        # task_id = tasks[0].taskid
        # info = ipm[task_id]
        # self.hw_server_task_ip = info[1]
        # self.hw_server_task_port = info[0]

    def launch_hw_client(self):
        print ("Launching the HelloWorld client app")
        # Use cluster 1 for launching the SUB
        self.create_binary_app(name=self.hw_client_app_id,
                               app_script='./src/hw_client.py %s' % (self.hw_server_task_ip),
                               cpus=0.01, mem=32,
                               ports=[0])


class RunTest(object):
    def __init__(self):
        r = HW()
        r.start_appserver()
        r.run_test()
        time.sleep(60)
        print ("Going to delete all launched apps")
        r.delete_all_launched_apps()
        r.stop_appserver()

if __name__ == "__main__":
    RunTest()