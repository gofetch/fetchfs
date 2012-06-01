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
            self.list.append(peer)
            self._sort()
    
    def remove(self, peer):
        self.list.remove(peer)

class DHT:
    def __init__(self, bootstrap_node, local_port=5000, local_ip=''):
        self.selfnode = Peer(local_ip, local_port)
        self.server = StreamingServer(self._handle, local_ip, local_port)
        self.peers = PeerList()
        self.peers.add(self.selfnode)
        self.table = dict()
        self.server.start()
        if bootstrap_node:
            message(boostrap_node, BOOTSTRAP,
                    {'ip': local_ip, 'port': local_port})
    
    def _handle(self, conn, data):
        resp = json.loads(data)
        
        if resp['msg'] == BOOTSTRAP:
            newpeer = (resp['ip'], resp['port'])
            message(newpeer, PEERS, {'peers': self.peers})
            self.peers += newpeer
        
        elif resp['msg'] == PEERS:
            others = resp['peers']
            self.peers += [Peer(ip, port) for ip, port in others]
            for peer in others:
                message(peer.astuple(), ANNOUNCE,
                        {'ip': self.ip, 'port':self.port})
        
        elif resp['msg'] == ANNOUNCE:
            peer_ip = resp['data']['ip']
            peer_port = resp['data']['port']
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
        for p in self.peers:
            resp = message(p.astuple(), GET, {'key':key}, receive=True)
            if resp and resp['msg'] == RECV:
                return resp['value']
    
    def __setitem__(self, key, value):
        peer = random.choice(self.peers.list)
        message(peer.astuple(), SET, {'key': key, 'value':value})


import time
if __name__ == '__main__':
    import sys
    bootport = int(sys.argv[1])
    a = DHT(None, local_ip='localhost', local_port=bootport)
    a['/'] = [['.', 1, 0],['file1', 0, 132], ['dir1',1,0]]
    a['/file1'] = [['file1',0, 132]]
    a['/dir1'] = [['.', 1, 0], ['file2', 0, 142]]
    a['/dir1/file2'] = [['file2', 0, 142]]
    print a['/dir1']

