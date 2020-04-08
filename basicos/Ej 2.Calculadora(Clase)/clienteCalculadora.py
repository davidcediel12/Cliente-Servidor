

#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
for request in range(3):
    print("Sending request %s " % request)

    msg = input()
    socket.send_string(msg)

    #  Get the reply.
    message = socket.recv_string()
    print("Received reply: ", message)