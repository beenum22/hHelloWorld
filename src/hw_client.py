#!/usr/bin/env python
from sys import path
path.append("hydra/src/main/python")

import zmq
import sys


def run(argv):
    server_ip = argv[1]
    context = zmq.Context()
    print("Connecting to hello world server at %s" % server_ip)
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://" + server_ip + ":5555")
    for request in range(10):
        if request % 2:
            print("Sending request 'request1'")
            socket.send(b"request1")
        else:
            print("Sending request 'Hello'")
            socket.send(b"Hello")
        message = socket.recv()
        print("Received reply %s [ %s ]" % (request, message))

if __name__ == "__main__":
    run(sys.argv)
