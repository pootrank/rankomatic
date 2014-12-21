import os
import logging
from logging.handlers import RotatingFileHandler

max_bytes = 102400
num_backups = 5


def make_file_handler():
    logdir = os.environ.get('LOGDIR')
    filename = logdir + "/flask.log"
    file_handler = RotatingFileHandler(filename, maxBytes=max_bytes,
                                       backupCount=num_backups)
    file_handler.setLevel(logging.WARNING)
    return file_handler


DEBUG = False
TESTING = False
PROPOGATE_EXCEPTIONS = True
LOG_FILE_HANDLER = make_file_handler()
MONGODB_SETTINGS = {'DB': 'otorder'}
