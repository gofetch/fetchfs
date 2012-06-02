from streamingserver import StreamingServer
import random
import json
import socket
from utils import *

class Peer:
    ''' a dht peer node. '''
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.id = hash(repr(self))
    def __repr__(self):
        return repr((self.ip, self.port))
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)
    def __ne__(self, other):
        return not self.__eq__(other)
    def astuple(self):
        return (self.ip, self.port)


class PeerList:
    ''' a sorted list of peers based on hash id. '''
    def __init__(self):
        self.list = []
    def __iter__(self):
        return self.list.__iter__()
    def _sort(self):
        sorted(self.list, key= lambda peer: peer.id)
    def add(self, peer):
        assert isinstance(peer, Peer)
        if peer not in self.list:
            print 'adding', peer, self.list
            self.list.append(peer)
            self._sort()
    def remove(self, peer):
        self.list.remove(peer)

class DHT:
    def __init__(self, bootstrap_node, local_ip='localhost', local_port=8000):
        self.selfnode = Peer(local_ip, local_port)
        self.server = StreamingServer(self._handle, local_ip, local_port)
        self.peers = PeerList()
        self.peers.add(self.selfnode)
        self.table = dict()
        self.server.start()
        if bootstrap_node:
            message(bootstrap_node, BOOTSTRAP,
                    {'ip': local_ip, 'port': local_port})
    
    def _handle(self, conn, data):
        resp = json.loads(data)
        
        if resp['msg'] == BOOTSTRAP:
            newpeer = Peer(resp['ip'], resp['port'])
            peertuples = [p.astuple() for p in self.peers]
            message(newpeer.astuple(), PEERS, {'peers': peertuples})
            self.peers.add(newpeer)
        
        elif resp['msg'] == PEERS:
            others = resp['peers']
            for ip, port in others:
                peer = Peer(ip, port)
                self.peers.add(peer)
                message(peer.astuple(), ANNOUNCE,
                        {'ip': self.selfnode.ip, 'port':self.selfnode.port})
        
        elif resp['msg'] == ANNOUNCE:
            peer_ip = resp['ip']
            peer_port = resp['port']
            self.peers.add(Peer(peer_ip, peer_port))
        
        elif resp['msg'] == SET:
           key, value = hash(resp['key']), resp['value']
           self.table[key] = value
        
        elif resp['msg'] == GET:
            key = hash(resp['key'])
            if self.table.has_key(key):
                message(conn, RECV, {'value': self.table[key]})
            else:
                message(conn, RECV, {'value': None})
    
    def __getitem__(self, key):
        for p in self.peers.list:
            resp = message(p.astuple(), GET, {'key':key}, receive=True)
            if resp and resp['msg'] == RECV:
                return resp['value']
    
    def __setitem__(self, key, value):
        peer = random.choice(self.peers.list)
        message(peer.astuple(), SET, {'key': key, 'value':value})
    
    def update(self, d):
        for k in d:
            self[k] = d[k]

import time
if __name__ == '__main__':
    import sys
    bootport = int(sys.argv[1])
    a = DHT(None, local_ip='localhost', local_port=bootport)
    b = DHT(('localhost', bootport), local_ip='localhost', local_port=bootport+1)
    a['/'] = { 'isdir': 1,
                     'ls': ['hello.py']}
    a['/hello.py'] = {'isdir': 0,
                      'ls':[],
                      'st_mtime':0.0,
                      'st_size':0,
                      'hash':'a'}
    time.sleep(1)
    print a.peers.list
    print b.peers.list


