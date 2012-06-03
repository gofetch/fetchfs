from streamingserver import StreamingServer
import random
import json
import socket
import threading
from utils import *
import time

class Peer:
    ''' a dht peer node. '''
    def __init__(self, ip, port):
        self.ip = unicode(ip)
        self.port = port
<<<<<<< HEAD
        self.id = hash(repr(self))
=======
        self.id = int(hash(repr(self)), 16)
>>>>>>> 7c0ba83945268418ce841294f0bdf3bd1a5857b6
    
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
    
    def add(self, peer):
        assert isinstance(peer, Peer)
        if peer not in self.list:
            self.list.append(peer)
    
    def remove(self, peer):
        self.list.remove(peer)

<<<<<<< HEAD


class DHT:
    def __init__(self, bootstrap_node, local_ip='localhost', local_port=8000):
        self.selfnode = Peer(local_ip, local_port)
        self.server = StreamingServer(self._handle, local_ip, local_port)
        self.peers = PeerList()
        self.peers.add(self.selfnode)
=======
class DHT(threading.Thread):
    def __init__(self, bootstrap_node, local_node=Peer(u'localhost', 5000)):
        threading.Thread.__init__(self)
        self.daemon = True
>>>>>>> 7c0ba83945268418ce841294f0bdf3bd1a5857b6
        self.table = dict()
        self.local_node = local_node
        self.predecessor = None
        self.server = StreamingServer(self._handle, self.local_node.ip, self.local_node.port)
        self.server.start()
        self.bootstrap_node = bootstrap_node
        if not bootstrap_node:
            self.successor = self.local_node
        if bootstrap_node:
            successor_response = message(bootstrap_node, GETSUCCESSOR, get_successor_message(self.local_node.id), receive=True)
            self.successor = Peer(*successor_response)
            message(self.successor, NOTIFY, notify_message(self.local_node.astuple()))
    
    def run(self):
        while(True):
            time.sleep(STABILIZE_WAIT)
            self._stabilize()            
    
    def _handle(self, conn, data):
        resp = json.loads(data)
        msg = resp['msg']
        if msg == GETSUCCESSOR:
            key = resp['key']
            successor = None
            if self.local_node == self.successor:
                successor = self.local_node
            else:
                if key == self.local_node.id or within(key, self.local_node.id, self.successor.id):
                    successor = self.successor
                else:
                    g_s_msg = get_successor_message(key)
                    successor_response = message(self.successor, GETSUCCESSOR, g_s_msg, receive=True)
                    successor = Peer(*successor_response)
            if successor:
                # todo: this should really be calling successor_response() to make it into json to transfer over the wire
                conn.send(json.dumps(list(successor.astuple())))
            else:
                conn.close()
        elif msg == NOTIFY:
            possible_pred = Peer(*resp['predecessor'])
            p_pred_id = possible_pred.id
            if possible_pred:
                if not self.predecessor or within(p_pred_id, self.predecessor.id, self.local_node.id):
                    self.predecessor = possible_pred
                    for key in self.table:
                        keyhash = int(hash(key), 16)
                        if not within(keyhash, self.predecessor.id, self.local_node.id):
                            value = self.table[key]
                            message(self.successor, STORE, store_message(key, value))
        elif msg == STORE:
            key = resp['key']
            value = resp['value']
            keyhash = int(hash(key), 16)
            if not self.predecessor or within(keyhash, self.predecessor.id, self.local_node.id):
                self.table[key] = value
            else:
                message(self.successor, STORE, store_message(key, value))
    
        elif msg == GET:
            key = resp['key']
            if key in self.table:
                value = self.table[key]
            else:
                value = None
            g_response = get_response(value)
            conn.send(json.dumps(g_response))
        elif msg == GETPREDECESSOR:
            if self.predecessor:
                p = self.predecessor.astuple()
            else:
                p = None
            p_response = json.dumps(get_predecessor_response(p))
            conn.send(p_response)
        else:
            pass
            
    def _stabilize(self):
        predecessor_response = message(self.successor, GETPREDECESSOR, get_predecessor(), receive=True)
        resp = predecessor_response['predecessor']
        if resp:
            predecessor_node = Peer(*predecessor_response['predecessor'])
            if self.local_node.id == self.successor.id or within(predecessor_node.id, self.local_node.id, self.successor.id):
                self.successor = predecessor_node
        message(self.successor, NOTIFY, notify_message(self.local_node.astuple()))

            
    def __getitem__(self, key):
<<<<<<< HEAD
        for p in self.peers.list:
            resp = message(p.astuple(), GET, {'key':key}, receive=True)
            if resp and resp['value']:
                return resp['value']
=======
        keyhash = int(hash(key), 16)
        successor_response = message(self.local_node, GETSUCCESSOR, get_successor_message(keyhash), receive=True)
        key_successor = Peer(*successor_response)
        get_response = message(key_successor, GET, get_message(key), receive=True)
        value = get_response["value"]
        if value is None:
            raise KeyError("Key not found in DHT")
        return value
>>>>>>> 7c0ba83945268418ce841294f0bdf3bd1a5857b6
    
    def __setitem__(self, key, value):
        message(self.local_node, STORE, store_message(key, value))
        
    def p(self):
        print "Predecessor:", self.predecessor, "Self:", self.local_node, "Successor:", self.successor, "Data Table:", self.table


if __name__ == '__main__':
    import sys
<<<<<<< HEAD
    bootport = int(sys.argv[1])
    a = DHT(None, local_ip='localhost', local_port=bootport)
    while True:
        print a['a']
        time.sleep(1)

=======
    first_port = int(sys.argv[1])
    num_peers = int(sys.argv[2])
    DHT_Nodes = []
    for i in range(num_peers):
        if i == 0:
            bootstrap = None
        else:
            bootstrap = DHT_Nodes[i-1].local_node
        peer = Peer('localhost', first_port + i)
        node = DHT(bootstrap, local_node=peer)
        node.start()
        DHT_Nodes.append(node)
    
    # after we add a peer to the DHT, we must wait up to 1 stabilization period
    # before we are guaranteed that neighbors have stabilized
>>>>>>> 7c0ba83945268418ce841294f0bdf3bd1a5857b6

    DHT_Nodes[4]["key1"] = "value1"
    DHT_Nodes[2]["key3"] = "value2"
    time.sleep(STABILIZE_WAIT)
    DHT_Nodes[1]["key5"] = "value3"
    DHT_Nodes[4]["key4"] = "value4"
    DHT_Nodes[0]["key2"] = "value5"
    time.sleep(STABILIZE_WAIT*2)
    

    print DHT_Nodes[2]["key1"]
    print DHT_Nodes[4]["key2"]
    print DHT_Nodes[2]["key3"]
    print DHT_Nodes[1]["key4"]
    print DHT_Nodes[4]["key5"]
