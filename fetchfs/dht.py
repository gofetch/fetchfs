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
                # make connection to peer
                s = socket.socket()
                s.connect((resp['data']['ip'], resp['data']['port']))
                s.send(json.dumps({'msg':'PEERS', 'data':self.peers}))
                s.close()
            
            if resp['msg'] == 'PEERS':
                others = resp['data']
                self.peers += [tuple(p) for p in others]
                for peer in others:
                    s = socket.socket()
                    s.connect(tuple(peer))
                    s.send(json.dumps({'msg':'ANNOUNCE', 'data':{'ip':self.ip, 'port':self.port}}))
                    s.close()
            
            if resp['msg'] == 'ANNOUNCE':
                save_print("ANNOUN")
                peer_ip = resp['data']['ip']
                peer_port = resp['data']['port']
                self.peers += [(peer_ip, peer_port)]
            
            if resp['msg'] == 'SET':
                data = resp['data']
                self.table[data['key']] = data['value']
            
            if resp['msg'] == 'GET':
                save_print('get')
                lookup = resp['data']['key']
                save_print('lookingup', lookup, self.port, self.table)
                if self.table.has_key(lookup):
                    save_print('found', self.port)
                    conn.send(json.dumps({'msg':'RECV','data':self.table[lookup]}))
                else:
                    #conn.close()
                    pass
            
        except:
            pass
    
    def _bootstrap(self, bootstrap_node):
        s = socket.socket()
        s.connect(bootstrap_node)
        s.send(json.dumps({'msg':'BOOTSTRAP', 'data':{'ip':self.ip, 'port':self.port}}))
        s.close()
    
    def __getitem__(self, key):
        for p in self.peers:
            s = socket.socket()
            s.connect(p)
            s.send(json.dumps({'msg':'GET', 'data':{'key':key}}))
            try:
                s.settimeout(1)
                resp = s.recv(1024)
                if resp:
                    resp = json.loads(resp)
                    return(resp['data'])
            except:
                pass
            s.close()
    
    def __setitem__(self, key, value):
        peer = random.choice(self.peers)
        s = socket.socket()
        s.connect(peer)
        s.send(json.dumps({'msg':'SET','data':{'key':key, 'value':value}}))
        s.close()

import time
if __name__ == '__main__':
    import sys
    bootport = int(sys.argv[1])
    a = DHT(None, local_ip='localhost', local_port=bootport)
    a['/'] = [['.', 1, 0],['file1', 0, 132], ['dir1',1,0]]
    a['/file1'] = [['file1',0, 132]]
    a['/dir1'] = [['.', 1, 0], ['file2', 0, 142]]
    a['/dir1/file2'] = [['file2', 0, 142]]
    time.sleep(1000)

