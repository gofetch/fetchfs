#!/usr/bin/env python 

import select 
import socket 
import sys 
import threading

class StreamingServer(threading.Thread):
    def __init__(self, handle, host='localhost', port=5000, chunksize=1024):
        threading.Thread.__init__(self)
        self.daemon = True
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.bind((host,port)) 
        self.server.listen(5)
        self.chunksize = chunksize
        self.input = [self.server]
        self.handle = handle
        
    def run(self):
        while True:
            inputready,outputready,exceptready = select.select(self.input,[],[])
            for s in inputready:
                if s == self.server:
                    # handle the server socket 
                    client, address = self.server.accept()
                    self.input.append(client)
                else:
                    # handle all other sockets 
                    data = s.recv(self.chunksize)
                    if data:
                        self.handle(s, address)
                    else: 
                        s.close()
                        self.input.remove(s)
        self.server.close()


def echo_handle(conn, data):
    conn.send(data)

if __name__ == '__main__':
    s = StreamingServer(r)
    s.start()
    import time
    time.sleep(1000)

