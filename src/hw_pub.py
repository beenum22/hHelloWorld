#!/usr/bin/env python
import zmq
import os
import logging
import sys
import time

from sys import path

path.append("hydra/src/main/python")
from hydra.lib import util
from hydra.lib.hdaemon import HDaemonRepSrv

l = util.createlogger('HWPub', logging.INFO)


class HDHelloWorldPub(HDaemonRepSrv):
    def __init__(self, port):
        HDaemonRepSrv.__init__(self, port)
        soc = None
        self.register_fn('sendmsg', self.send_msg)

    def send_msg(self, arg1):
        """
        Function to handle the 'sendmsg' signal by test.
        It will start sending 'arg1' number of messages to subscribers.
        :param arg1: Number of messages to send to the subscriber.
        :return:
        """
        l.info("send_msg has been called with argument %s" % arg1)
        for i in range(int(arg1)):
            self.soc.send("%d msgggg" % i)

        return 'ok', None


def run(argv):
    """
    This function would be called when hw_test launches hw_pub app.
    :param argv: Function will take publisher_port as argument. A ZMQ publisher socket will be opened with this port.
    :return:
    """
    pub_port = argv[1]
    # Open ZMQ publisher data socket.
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    print("ZMQ HWM is set to : %s" % socket.get_hwm())
    print ("pub_port=%s" % (pub_port))
    socket.bind("tcp://*:%s" % pub_port)

    # Use PORT0 (this is the port which Mesos assigns to the applicaiton), as control port. HAnalyzer will send all
    # signals to this port.
    pub_rep_port = os.environ.get('PORT0')
    print ("Starting HelloWorld pub at port [%s]", pub_rep_port)
    hd = HDHelloWorldPub(pub_rep_port)
    hd.soc = socket
    hd.run()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    run(sys.argv)
