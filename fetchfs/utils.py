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
        
def within(x, a, b):
    ''' True if x is within the arc along the circle beginning above a and ending at b'''
    effective_b = b
    if a:
        if a > b:
            b += KEYSPACE_SIZE
        if a > x:
            x += KEYSPACE_SIZE
        return x > a and x < b
    else:
        return x < b
            

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
        s.connect(peer.astuple())
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
        
def get_successor_message(key):
    return {'key': key}
    
def notify_message(predecessor):
    return {'predecessor': predecessor}
    
def store_message(key, value):
    return {'key': key, 'value': value}
    
def get_message(key):
    return {'key': key}

def get_response(value):
    return {'value': value}

def get_predecessor():
    return {}
    
def get_predecessor_response(predecessor):
    return {'predecessor': predecessor}

# message types

GETSUCCESSOR = 0 # get successor to a key
NOTIFY = 1 # notify a node of a predecessor
STORE = 2 # store a key and value at a node
GET = 3 # get a value from a node given a key
GETPREDECESSOR = 4 # get a predecessor from a node

# keyspace size
KEYSPACE_BITS = 160
KEYSPACE_SIZE = 2 ** 160

# stabilization_time
STABILIZE_WAIT = 1