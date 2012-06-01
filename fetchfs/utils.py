from __future__ import print_function
from threading import Lock
import socket
import json
import hashlib

def hash(i):
    return hashlib.sha1(i).hexdigest()

print_lock = Lock()
def save_print(*args, **kwargs):
    with print_lock:
        print (*args, **kwargs)


def message(peer, msg, data, receive=False, wait=0.0):
    ''' sends a message to a peer
        a peer can either be a tuple: (ip, port) or
        a socket connection. if a socket is passed,
        handling closing the socket is not our responsibility
    '''
    if isinstance(peer, socket.socket):
        s = peer
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(peer)
    msgsend = {"msg":msg}
    msgsend.update(data)
    sent = s.send(json.dumps(msgsend))
    if sent == 0:
        raise RuntimeError("socket connection broken")
    if receive:
        response = s.recv(1024)
        if response == '':
            raise RuntimeError("socket connection broken")
        return json.loads(response)
    if isinstance(peer, tuple):
        s.close()



# message types

BOOTSTRAP = 0 # request to be boostrapped
PEERS = 1 # return list of peers you know
ANNOUNCE = 2 # announce to peers of your existence
SET = 3 # set a value for a key
GET = 4 # get a value for a key
RECV = 5 # return the value of the key
NAK = 6 # response is null or unkown
ACK = 7 # request is accepted by peer
