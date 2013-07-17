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
from flask import Flask, render_template, request
from flask.ext.mongoengine import MongoEngine
from models import tableaux_form

#TODO figure out better config system
app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = { 'DB': 'rankomatic' }
app.config['SECRET_KEY'] = 'keepThisSecret'
app.config['DEBUG'] = True

db = MongoEngine(app)


#TODO implement this using separate Blueprints
#@app.route("/")
def table():
    form = tableaux_form(request.form)
    return render_template("table.html", form=form)


def register_blueprints(app):
    # prevent circular imports
    from rankomatic.users import users
    app.register_blueprint(users)

register_blueprints(app)



if __name__ == '__main__':
    app.run()
