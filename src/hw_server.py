#!/usr/bin/env python
from sys import path
path.append("hydra/src/main/python")

import time
import zmq
import os
import logging
from hydra.lib import util
l = util.createlogger('HWSrv', logging.INFO)

from hydra.lib.hdaemon import HDaemonRepSrv


class HDHelloWorldSrv(HDaemonRepSrv):
    def __init__(self, port, run_data):
        HDaemonRepSrv.__init__(self, port)
        self.run_data = run_data
        self.register_fn('teststart', self.test_start)
        self.register_fn('helloworld', self.test_helloworld)
        self.register_fn('teststatus', self.test_status)

    def test_start(self):
        self.run_data['start'] = True
        self.run_data['test_status'] = 'running'
        l.info ("I have started the test. Life is good :)")
        return 'ok', None

    def test_helloworld(selfs, arg1):
        l.info ("Hello World has been called with argument %s" % arg1)
        return 'ok', None

    def test_status(self):
        return 'ok', self.run_data['test_status']


def run():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    print("ZMQ HWM is set to : %s" % socket.get_hwm())
    socket.bind("tcp://*:5555")

    server_rep_port = os.environ.get('PORT0')
    print ("Starting HelloWorld server at port [%s]", server_rep_port)

    run_data = {'start': False,
                'test_status': 'stopped'}
    hd = HDHelloWorldSrv(server_rep_port, run_data)
    hd.run()



if __name__ == "__main__":
    run()
