from __future__ import print_function
from streamingserver import StreamingServer
from hashlib import sha1 as hash
import random
import json
import socket

from threading import Lock

print_lock = Lock()
def save_print(*args, **kwargs):
  with print_lock:
    print (*args, **kwargs)

class DHT:
    def __init__(self, bootstrap_node, local_port=5000, local_ip=''):
        self.node = (local_ip, local_port)
        self.ip = local_ip
        self.port = local_port
        self.nodeid = hash(str(random.random())).hexdigest()
        self.server = StreamingServer(self._handle, local_ip, local_port)
        self.peers = [self.node]
        self.table = dict()
        self.server.start()
        if bootstrap_node:
            self._bootstrap(bootstrap_node)
    
    def _handle(self, conn, data):
        try:
            resp = json.loads(data)
            if resp['msg'] == 'BOOTSTRAP':
                save_print("BOOT")
                # make connection to peer
                s = socket.socket()
                s.connect((resp['data']['ip'], resp['data']['port']))
                s.send(json.dumps({'msg':'PEERS', 'data':self.peers}))
                s.close()
            if resp['msg'] == 'PEERS':
                save_print("PEERS")
                self.peers += resp['data']
        except:
            pass
    
    def _bootstrap(self, bootstrap_node):
        s = socket.socket()
        s.connect(bootstrap_node)
        s.settimeout(1)
        s.send(json.dumps({'msg':'BOOTSTRAP', 'data':{'ip':self.ip, 'port':self.port}}))
        s.close()
    
    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass



if __name__ == '__main__':
    import sys
    bootport = int(sys.argv[1])
    a = DHT(None, local_ip='localhost', local_port=bootport)
    b = DHT(('localhost', bootport), local_ip='localhost', local_port=4002)
    import time
    time.sleep(3)
    print(b.peers)

