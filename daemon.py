# This module adapted from pydaemonize 0.1, published with the following
# notice:
#
# Copyright 2011 Frederick J. Ross.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Also included elements from Chad J. Schroeder's "Creating a daemon
# the Python Way": <http://code.activestate.com/recipes/278731>
"""Disk And Execution MONitor (Daemon)

Configurable daemon behaviors:

    1.) The current working directory set to the "/" directory.
    2.) The current file creation mode mask set to 0.
    3.) Close all open files (1024).
    4.) Redirect standard I/O streams to "/dev/null".

A failed call to fork() now raises an exception.

References:
    1) Advanced Programming in the Unix Environment: W. Richard Stevens
    2) Unix Programming Frequently Asked Questions:
        http://www.erlenstar.demon.co.uk/unix/faq_toc.html
"""

import os
import sys

UMASK = 0
WORKDIR = "/"
MAXFD = 1024

if hasattr(os, "devnull"):
    REDIRECT_TO = os.devnull
else:
    REDIRECT_TO = "/dev/null"


def continue_as_forked_child():
    if os.fork() != 0:
        os._exit(0)


def pipe_standard_files_to_devnull():
    """Attach stdin, stdout, and stderr to /dev/null"""
    f = open(os.devnull, 'w')
    sys.stdin = f
    sys.stdout = f
    sys.stderr = f


def fork():
    try:
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))
    return pid


def daemonize():
    """Turn the current process into a daemon.
    Turning a process into a daemon involves a fixed set of operations
    on unix systems, described in section 13.3 of Stevens and Rago,
    "Advanced Programming in the Unix Environment."  Since they are
    fixed, they can be written as a single function, ``daemonize``.

    Briefly, ``daemonize`` sets the file creation mask to 0, forks
    twice, changed the working directory to ``/``, closes all open
    file descriptors, sets stdin, stdout, and stderr to ``/dev/null``,
    and blocks 'sigHUP'. The actual behavior of the daemon is
    performed after the call to daemonize.

    ``daemonize`` makes no attempt to do clever error handling,
    restarting, or signal handling. All that is to be handled by
    whatever is called after ``daemonize``.
    """
    pid = fork()
    if pid == 0:  # first child
        os.setsid()  # detach from terminal by creating new session

        pid = fork()
        if pid == 0:  # second child
            os.chdir(WORKDIR)  # new working directory
            os.umask(UMASK)  # new file permission
        else:
            os._exit(0)  # kill first child
    else:
        os._exit(0)  # kill parent process
    pipe_standard_files_to_devnull()
