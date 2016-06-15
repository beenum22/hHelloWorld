#!/usr/bin/env python

import time
import zmq


def run():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    print("Starting the server.")
    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: %s" % message)

        time.sleep(1)
        #  Send reply back to client
        if message == "Hello":
            socket.send_string("World")
        elif message == "request1":
            socket.send_string("response1")

if __name__ == "__main__":
    run()