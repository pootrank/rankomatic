#! /usr/bin/env python
import argparse
import errno
import logging
import os
import socket
import sys
import time

from daemon import daemonize
from logging.handlers import RotatingFileHandler, DEFAULT_TCP_LOGGING_PORT
from multiprocessing import Event, Queue
from multiprocessing.managers import SyncManager


DEFAULT_LOGDIR = os.path.abspath('logs')
DEFAULT_LOGFILE = 'otorderd.log'
DEFAULT_LOGPATH = os.path.join(DEFAULT_LOGDIR, DEFAULT_LOGFILE)
LOGFILE_MAX_BYTES = 102400
BACKUP_COUNT = 5
ADDRESS = ('', DEFAULT_TCP_LOGGING_PORT)
START = 'start'
STOP = 'stop'
RESTART = 'restart'
OPTIONS = [START, STOP, RESTART]
RESTART_TIMEOUT = 30

log_queue = Queue()


class LogQueueManager(SyncManager):
    pass


LogQueueManager.register('log_queue', callable=lambda: log_queue)


def daemon_is_running(address=ADDRESS):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(address)
    sock.close()
    return result == 0


def log_queue_manager():
    return LogQueueManager(address=ADDRESS, authkey='')


def get_formatter():
    return logging.Formatter(
        '%(asctime)s %(name)s '
        '%(levelname)-8s %(message)s'
    )


def log_worker_configurer(log_queue):
    handler = QueueLogHandler(log_queue)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)


def initialize_queue_logger():
    log_manager = log_queue_manager()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(ADDRESS)
        sock.close()
    except socket.error as err:
        if err.errno == errno.ECONNREFUSED:
            msg = "Connection to logger refused at: {}".format(ADDRESS)
            raise socket.error(msg)
        else:
            raise err

    log_manager.connect()
    log_queue = log_manager.log_queue()
    log_worker_configurer(log_queue)


class QueueLogHandler(logging.Handler):

    def __init__(self, log_queue, *args, **kwargs):
        super(QueueLogHandler, self).__init__(*args, **kwargs)
        self.log_queue = log_queue

    def emit(self, record):
        try:
            self.handle_record(record)
        except(KeyboardInterrupt, SystemExit) as err:
            raise err
        except:
            self.handleError(record)

    def handle_record(self, record):
        if record.exc_info:
            self.format(record)  # do nothing with return value
            record.exc_info = None
        self.log_queue.put(record)


class OtorderdLogListener(object):

    def __init__(self, user_args, *args, **kwargs):
        super(OtorderdLogListener, self).__init__(*args, **kwargs)
        self.manager = log_queue_manager()
        self.debug = user_args.debug
        self.exit = Event()
        self.logpath = os.path.abspath(DEFAULT_LOGPATH)

    def run(self):
        self.manager.start()
        self.log_queue = self.manager.log_queue()
        self.configure()
        while not self.exit.is_set():
            try:
                self.log_record()
            except (KeyboardInterrupt, SystemExit) as err:
                raise err
            except:
                self.print_exception()

    def configure(self):
        root = logging.getLogger()
        handler = RotatingFileHandler(self.logpath, maxBytes=LOGFILE_MAX_BYTES,
                                      backupCount=BACKUP_COUNT)
        self.formatter = get_formatter()
        handler.setFormatter(self.formatter)
        root.addHandler(handler)
        if self.debug:
            self.configure_stderr_output()

    def configure_stderr_output(self):
        root = logging.getLogger()
        stderr_handler = logging.StreamHandler()
        stderr_handler.setFormatter(self.formatter)
        root.addHandler(stderr_handler)

    def log_record(self):
        record = self.log_queue.get()
        if record is not None:
            logger = logging.getLogger(record.name)
            logger.handle(record)
        else:
            self.exit.set()

    def print_exception(self):
        import traceback
        print >> sys.stderr, "Error logging:"
        traceback.print_exc(file=sys.stderr)


def get_args():
    parser = argparse.ArgumentParser(
        description="A daemon for otorderd to log to. Listens on a shared "
        "multiprocessing.Queue connected to "
        "logging.handlers.DEFAULT_TCP_LOGGING_PORT "
    )
    parser.add_argument("cmd", choices=OPTIONS,
                        help="start, stop, or restart the log listener daemon")
    parser.add_argument("--debug", action='store_true',
                        help="start listener as non-daemonic process "
                        "and log to STDERR as well")
    parser.add_argument("-f", "--file", help="choose the log file, will "
                        "create if it doesn't exist")
    return parser.parse_args()


class KillListenerTimeout(Exception):

    def __init__(self, address, msg=None, *args, **kwargs):
        if msg is None:
            msg = ("Log listener listening at {} hasn't died after {} "
                   "seconds. Either try again or kill listener "
                   "manually.").format(
                ADDRESS, RESTART_TIMEOUT
            )
        super(KillListenerTimeout, self).__init__(*args, **kwargs)
        self.address = ADDRESS


def wait_for_finish():
    """Wait for the listener to die, raise an exception if it hasn't.

    Run loop RESTART_TIMEOUT times, waiting for 1 second at the bottom
    of each loop. Check for the log listener to die each time through.
    If it hasn't died by the end of the loop, raise an exception that
    displays the port number it is listening on.
    """
    for i in xrange(RESTART_TIMEOUT):
        if daemon_is_running():
            time.sleep(1)
        else:
            return
    raise KillListenerTimeout()


def stop(args):
    if daemon_is_running():
        manager = log_queue_manager()
        manager.connect()
        log_queue = manager.log_queue()
        log_queue.put(None)
        # this is shared with a dead process, needs to be manually removed
        del log_queue
        wait_for_finish()
        print "log listener at {} successfully stopped".format(ADDRESS)
    else:
        raise socket.error("No log listener at {} [Errno {}]".format(
            ADDRESS, errno.ECONNREFUSED
        ))


def start(args):
    if not daemon_is_running():
        if not args.debug:
            print "running log listener as daemon at {}".format(ADDRESS)
            daemonize()
        listener = OtorderdLogListener(args)
        listener.run()
    else:
        msg = "Log listener already running at {}. [Errno {}]".format(
            ADDRESS, errno.EADDRINUSE
        )
        raise socket.error(msg)


def restart(args):
    stop(args)
    start(args)


if __name__ == "__main__":
    args = get_args()
    if args.cmd == STOP:
        stop(args)
    elif args.cmd == RESTART:
        restart(args)
    else:
        start(args)
