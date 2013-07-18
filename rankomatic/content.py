"""
File: content.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a Blueprint for the basically static content pages of the OT ranking
site. Each view simply renders the page asked for.
"""
from flask import Blueprint, render_template
from flask.views import MethodView
from rankomatic.forms import LoginForm

content = Blueprint('content', __name__, template_folder='templates/content')


class LandingView(MethodView):

    def get(self):
        return render_template('landing.html', form=LoginForm(),
                               active='landing')


class GlossaryView(MethodView):

    def get(self):
        return render_template('glossary.html', active='glossary')


class AboutView(MethodView):

    def get(self):
        return render_template('about.html', active='about')


class ContactView(MethodView):

    def get(self):
        return render_template('contact.html', active='contact')


class CiteView(MethodView):

    def get(self):
        return render_template('cite.html', active='cite')


content.add_url_rule('/', view_func=LandingView.as_view('landing'))
content.add_url_rule('/glossary/', view_func=GlossaryView.as_view('glossary'))
content.add_url_rule('/about/', view_func=AboutView.as_view('about'))
content.add_url_rule('/contact/', view_func=ContactView.as_view('contact'))
content.add_url_rule('/cite/', view_func=CiteView.as_view('cite'))
