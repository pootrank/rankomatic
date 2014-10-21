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


class AboutView(MethodView):

    def get(self):
        return render_template('about.html', active='about')


content.add_url_rule('/', view_func=LandingView.as_view('landing'))
content.add_url_rule('/about/', view_func=AboutView.as_view('about'))
