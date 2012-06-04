fetchfs
=======

P2P filesystem based on FUSE

TODO
====

1. Figure out consistency
2. make chord DHT
3. set up file server using streamingserver
4. lots of other stuff

Installation (Ubuntu)
=====================
First we get FUSE: ::

    sudo apt-get install build-essential libfuse-dev libfuse2 fuse-utils

Fetchfs comes with python bindings for FUSE in the fuse.py file, but it can be found
from here: ::

    https://github.com/terencehonles/fusepy

(Optional) Installing UPnP and NAT-PMP libraries for port mapping and nat traversal ::

    wget "http://miniupnp.free.fr/files/download.php?file=miniupnpc-1.7.tar.gz"
    wget "http://miniupnp.free.fr/files/download.php?file=libnatpmp-20110808.tar.gz"

Now just extract and run the following commands for both ::

    make
    sudo make install
    python setup.py install

Installation (Mac OS X [Lion])
==============================
get fuse: ::

    https://github.com/downloads/fuse4x/fuse4x/Fuse4X-0.9.0.dmg

