"""
File: __init__.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

The main file for the Optimality Theory (OT) constraint-ranking website.
Implemented using Flask, this website is built on a Python implementation of
Alex Djalali's solution to the ranking problem in theoretical OT. For the
details of his solution, see his paper "A constructive solution to the ranking
problem in Partial Order Optimality Theory" (2013) which can be found at
http://stanford.edu/~djalali/publications.html. For the source of his
implementation, refer to https://github.com/alexdjalali/OT.

This file initiates the app and database connection, defines the configuration,
and imports and attaches the desired blueprints which contain the views.
"""
from flask import Flask, render_template, request
from flask.ext.mongoengine import MongoEngine
from models import tableaux_form

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = { 'DB': 'rankomatic' }
app.config['SECRET_KEY'] = 'keepThisSecret'
app.config['DEBUG'] = True

db = MongoEngine(app)



@app.route("/")
def table():
    form = tableaux_form(request.form)
    return render_template("table.html", form=form)


if __name__ == '__main__':
    app.run()

