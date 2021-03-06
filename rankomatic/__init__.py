"""
File: __init__.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

This file initiates the app and database connection, defines the configuration,
and imports and attaches the desired blueprints which contain the views.
Instantiates the app as a Python module; everything defined in here is
available for import from the rankomatic module.

"""
# TODO make sure documentation is up to date
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from multiprocessing.managers import SyncManager
import config.default_config

app = Flask(__name__, static_url_path='')
app.config.from_object(config.default_config)
app.config.from_envvar('APP_CONFIG', silent=True)


def get_db(self):
    return getattr(
        self.connection, self.app.config['MONGODB_SETTINGS']['DB']
    )


def get_queue():

    class QueueManager(SyncManager):
        pass

    QueueManager.register('control_queue')

    manager = QueueManager(address=app.config['WORKER_ADDRESS'],
                           authkey=app.config['SECRET_KEY'])
    manager.connect()
    return manager.control_queue()


MongoEngine.get_pymongo_db = get_db

db = MongoEngine(app)


def register_blueprints(app):
    # prevent circular imports
    from rankomatic.users import users
    from rankomatic.tools import tools
    from rankomatic.content import content
    from rankomatic.grammars import grammars
    app.register_blueprint(users)
    app.register_blueprint(tools)
    app.register_blueprint(content)
    app.register_blueprint(grammars)


try:
    app.logger.addHandler(app.config['LOG_FILE_HANDLER'])
except KeyError:
    pass


register_blueprints(app)
