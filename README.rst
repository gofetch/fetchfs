fetchfs
=======

P2P filesystem based on FUSE


Installation (Ubuntu)
=====================
First we get FUSE: ::

    sudo apt-get install build-essential libfuse-dev libfuse2 fuse-utils

Fetchfs comes with python bindings for FUSE in the fuse.py file, but it can be found
from here: ::

    https://github.com/terencehonles/fusepy

Install gevent ::

    sudo apt-get install libevent-dev
    pip install gevent

Install the gevent-DHT ::

    pip install gevent-dht

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

Fetchfs comes with python bindings for FUSE in the fuse.py file, but it can be found
from here: ::

    https://github.com/terencehonles/fusepy

Install gevent (Macports suggested for doing this) ::

    sudo port install libevent

We must link to the MacPort libevent library we installed ::
    
    export LDFLAGS='-L/opt/local/lib'
    export CPPFLAGS='-I/opt/local/include'
    export LD_LIBRARY_PATH=/opt/local/lib
    export LD_INCLUDE_PATH=/opt/local/include
    pip install gevent

Install gevent-DHT ::

    pip install gevent-dht

(Optional) Installing UPnP and NAT-PMP libraries for port mapping and nat traversal ::

    wget "http://miniupnp.free.fr/files/download.php?file=miniupnpc-1.7.tar.gz"
    wget "http://miniupnp.free.fr/files/download.php?file=libnatpmp-20110808.tar.gz"

Now just extract and run the following commands for both ::

    make
    sudo make install
    python setup.py install


Tips on keeping a clean Python environment with virtualenv/virtualenvwrapper
============================================================================

install build-essential and python distribute::

  sudo apt-get install build-essential python-dev python-pip python-distribute
  sudo pip install virtualenv
  sudo pip install virtualenvwrapper

create directory which will hold all your virtualenvs::

  mkdir ~/envs

Now, make the virtualenvwrapper available to your session::

  export WORKON_HOME=~/envs
  source $(which virtualenvwrapper.sh)

Make new project for fetchweb::

  mkvirtualenv fetchweb

change current virtualenv to fetchweb::

  workon fetchweb

to quit from the current virtualenv::

  deactivate
