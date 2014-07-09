import os
import logging

max_bytes = 102400
num_backups = 5


def make_file_handler():
    logdir = os.environ.get('LOGDIR')
    filename = logdir + "/flask.log"
    file_handler = logging.RotatingFileHandler(filename, maxBytes=max_bytes,
                                               backupCount=num_backups)
    file_handler.setLevel(logging.WARNING)
    return file_handler


DEBUG = False
TESTING = False
PROPOGATE_EXCEPTIONS = True
LOG_FILE_HANDLER = make_file_handler()
mongohq_url = os.environ.get('MONGOHQ_URL')
if mongohq_url:
    MONGODB_SETTINGS = {'HOST': mongohq_url,
                        'DB': os.path.basename(mongohq_url)}
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
