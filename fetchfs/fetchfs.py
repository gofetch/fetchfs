#!/usr/bin/env python

from __future__ import with_statement

from errno import EACCES, ENOENT
from os.path import realpath
from sys import argv, exit
from threading import Lock

import os

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context
from stat import S_IFDIR, S_IFREG

from dht import DHT

import utils
import time

class FetchFS(LoggingMixIn, Operations):
    def __init__(self, root, bootstrap_node, local_ip='localhost',
                 local_port=8000):
        self.realroot = realpath(root)
        self.rwlock = Lock()
        self.dht = DHT(bootstrap_node, local_ip, local_port)
        time.sleep(3)
        # walk dir and update dht
        files = utils.rgetdir(self.realroot)
        for path, newval in files.iteritems():
            newold = self.dht[path]
            if newold:
                utils.rdict_update(newold, newval)
                self.dht[path] = newold
            else:
                self.dht[path] = newval
        print "done mounting"
    
    def __call__(self, op, path, *args):
        return super(FetchFS, self).__call__(op, self.realroot + path, *args)
    
    def _relpath(self, path):
        relpath = '/' + os.path.relpath(path, self.realroot)
        return '/' if relpath == '/.' else relpath
    
    def getattr(self, path, fh=None):
        relpath = self._relpath(path)
        basename = os.path.basename(path)
        notallowed = ['Backups.backupdb', 'private', 'mach_kernel']
        if os.path.exists(path):
            st = os.lstat(path)
            return dict((key, getattr(st, key)) for key in ('st_atime',
                                                            'st_ctime',
                                                            'st_gid',
                                                            'st_mode',
                                                            'st_mtime',
                                                            'st_nlink',
                                                            'st_size',
                                                            'st_uid'))
        elif relpath == '/':
            st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
        
        elif basename.startswith('.') or basename in notallowed:
            raise FuseOSError(ENOENT)
        
        # look outside in the DHT
        externfile = self.dht[relpath]
        if not externfile:
            raise FuseOSError(ENOENT)
        if externfile['isdir']:
            st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)        
        else:
            st = dict(st_mode =(S_IFREG | 0444), st_size=externfile['st_size'])
        
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = externfile['st_mtime']
        return st
    
    def readdir(self, path, fh):
        relpath = self._relpath(path)
        realdir = ['.', '..']
        if os.path.exists(path):
            realdir += os.listdir(path)
        externfile = self.dht[relpath]
        externdir = externfile['ls'] if externfile else []
        return list(set(realdir) | set(externdir) )
    
    def statfs(self, path):
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail',
                                                         'f_bfree',
                                                         'f_blocks',
                                                         'f_bsize',
                                                         'f_favail',
                                                         'f_ffree',
                                                         'f_files',
                                                         'f_flag',
                                                         'f_frsize',
                                                         'f_namemax'))
    
    def mkdir(self, path, mode):
        relpath = self._relpath(path)
        folder_name = os.path.basename(relpath)
        os.mkdir(path, mode)
        self.dht[relpath] = utils.path_stat(path)
        # update ls of parent
        dirname = os.path.dirname(relpath)
        par = self.dht[dirname]
        utils.rdict_update(par, {'ls':[folder_name]})
        self.dht[dirname] = par
    
    
    rename = None
    rmdir = os.rmdir
    mknod = None
    open = None
    read = None
    readlink = None
    access = None
    flush = None
    chmod = None
    chown = None
    symlink = None
    truncate = None
    unlink = None
    utimens = None
    write = None


if __name__ == '__main__':
    if len(argv) != 5 and len(argv) != 7:
        print('usage: %s <root> <mountpoint> <local_ip> <local_port> ' \
                  '[<boot_ip> <boot_port>]'% argv[0])
        exit(1)
    if len(argv) == 5:
        fetchfs = FetchFS(argv[1], None, argv[3], int(argv[4]))
    elif len(argv) == 7:
        fetchfs = FetchFS(argv[1], (argv[5], int(argv[6])),
                          argv[3], int(argv[4]))
    fuse = FUSE(fetchfs, argv[2], foreground=True,
                fsname="FetchFS", volname="FetchFS", nothreads=True)


