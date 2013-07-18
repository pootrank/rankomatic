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
from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine
from rankomatic.config import ProductionConfig, TestingConfig, DevelopmentConfig

app = Flask(__name__)
#app.config.from_object(DevelopmentConfig)
app.config.from_object(ProductionConfig)
#app.config.from_object(TestingConfig)

db = MongoEngine(app)


def register_blueprints(app):
    # prevent circular imports
    from rankomatic.users import users
    from rankomatic.calculator import calculator
    from rankomatic.content import content
    app.register_blueprint(users)
    app.register_blueprint(calculator)
    app.register_blueprint(content)

register_blueprints(app)



if __name__ == '__main__':
    app.run()
