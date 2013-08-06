"""
File: __init__.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

This file initiates the app and database connection, defines the configuration,
and imports and attaches the desired blueprints which contain the views.
Instantiates the app as a Python module; everything defined in here is available
for import from the rankomatic module.
"""
#TODO make sure documentation is up to date
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_object('rankomatic.config.default-config')
app.config.from_envvar('APP_CONFIG', silent=True)

db = MongoEngine(app)
toolbar = DebugToolbarExtension(app)



def register_blueprints(app):
    # prevent circular imports
    from rankomatic.users import users
    from rankomatic.tools import tools
    from rankomatic.content import content
    app.register_blueprint(users)
    app.register_blueprint(tools)
    app.register_blueprint(content)

register_blueprints(app)



if __name__ == '__main__':
    app.run()
