#!/usr/bin/env python
import zmq
import sys
import logging
import os

from sys import path
path.append("hydra/src/main/python")
from hydra.lib import util
from hydra.lib.hdaemon import HDaemonRepSrv

l = util.createlogger('HWSrv', logging.INFO)


class HDHelloWorldSub(HDaemonRepSrv):
    def __init__(self, port, stats):
        HDaemonRepSrv.__init__(self, port)
        self.stats = stats
        self.register_fn('getstats', self.get_stats)

    # Handler for 'getstas' signal.
    def get_stats(self):
        l.info("stats counter %s" % self.stats.counter)
        return 'ok', self.stats.counter


class Stats(object):
    def __init__(self):
        self.counter = 0


def run(argv):
    """
    This function would be called when hw_test launches hw_sub app.
    :param argv: Function will take publisher_ip and publisher_port as arguments.
    A ZMQ subscriber socket will be opened with provided publisher_ip and publisher_port.
    :return:
    """
    pub_port = ""
    pub_ip = ""
    if len(argv) > 2:
        pub_ip = argv[1]
        pub_port = argv[2]
        int(pub_port)
    if not pub_ip or (not pub_port):
        raise Exception("hw-sub needs a pub server to subscribe to, pub_ip/pub_port"
                        " can not be empty pub_ip[%s], pub_port[%s]" % (pub_ip, pub_port))

    # Initialize HDaemonRepSrv. Use PORT0 (this is the port which Mesos assigns to the applicaiton), as control port.
    # HAnalyzer will send all signals (like 'getstats') to this port.
    sub_rep_port = os.environ.get('PORT0')
    stats = Stats()
    hd = HDHelloWorldSub(sub_rep_port, stats)
    hd.run()

    # Open ZMQ subscriber data socket. Note, we are giving empty topicfilter, as we are interested in ALL messages.
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    topicfilter = ""
    l.info("SUB connecting to PUB server at [%s:%s]" % (pub_ip, pub_port))
    socket.connect("tcp://%s:%s" % (pub_ip, pub_port))
    l.info("SUB successfully connected to PUB server at [%s:%s]" % (pub_ip, pub_port))
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

    # Recieve all messages sent by publisher here.
    while True:
        string = socket.recv()
        l.info("Received message %s" % string)
        stats.counter += 1

if __name__ == "__main__":
    run(sys.argv)
