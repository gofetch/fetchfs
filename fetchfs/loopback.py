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

a = DHT(('localhost',7004), local_ip='localhost', local_port=8002)

def get_dir(path):
    ret = a[path]
    if ret:
        return [f[0] for f in ret]
    else:
        return []


class FetchFS(LoggingMixIn, Operations):
    def __init__(self, root):
        self.realroot = realpath(root)
        self.rwlock = Lock()
        self.rootls = a['/']



    def __call__(self, op, path, *args):
        return super(Loopback, self).__call__(op, self.realroot + path, *args)


    def getattr(self, path, fh=None):
        relpath = '/' + os.path.relpath(path, self.realroot)
        if path == '/.':
            path = '/'
        basename = os.path.basename(path)
        notallowed = ['Backups.backupdb', 'private', 'mach_kernel']
        try:
            if os.path.exists(path):
                st = os.lstat(path)
                return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                                'st_gid', 'st_mode',
                                                                'st_mtime', 'st_nlink',
                                                                'st_size', 'st_uid'))
            elif basename.startswith('.') or basename in notallowed:
                raise FuseOSError(ENOENT)
            elif path == '/':
                st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
            
            
            print 'getattr', path
            # look outside
            extern = a[relpath]
            if len(extern) == 1 and extern[0][1] == 0:
                st = dict(st_mode =(S_IFREG | 0444), st_size=extern[0][2])
            else:
                st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)                
            st['st_ctime'] = st['st_mtime'] = st['st_atime'] = 0.0
        except:
            raise FuseOSError(ENOENT)
        return st

    def readdir(self, path, fh):
        path = '/' + os.path.relpath(path, self.realroot)
        if path == '/.':
            path = '/'
        ret = ['.', '..']
        if os.path.exists(self.realroot + path):
            realdir = os.listdir(self.realroot + path)
            ret += realdir
        for i in ret:
            yield i
        for i in get_dir(path):
            yield i
    
    def statfs(self, path):
        if os.path.exists(path):
            stv = os.statvfs(path)
            return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
                                                             'f_blocks', 'f_bsize',
                                                             'f_favail', 'f_ffree',
                                                             'f_files', 'f_flag',
                                                             'f_frsize', 'f_namemax'))
        else:
            return {}
    
    def release(self, path, fh):
        return os.close(fh)
    
    def rename(self, old, new):
        return os.rename(old, self.realroot + new)
    
    mkdir = os.mkdir
    rmdir = os.rmdir
    mknod = None
    open = None
    listxattr = None
    getxattr = None
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
    if len(argv) != 3:
        print('usage: %s <root> <mountpoint>' % argv[0])
        exit(1)
    fuse = FUSE(Loopback(argv[1]), argv[2], foreground=True, fsname="FetchFS",
                volname="FetchFS")


