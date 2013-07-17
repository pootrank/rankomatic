"""
File: users.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a users Blueprint for use with a Flask app. This was developed for use
with an Optimality Theory constraint-ranking app
(github.com/pootrank/rankomatic), but is intended to be somewhat general.
"""
from flask import ( Blueprint, render_template, request, session, flash,
                    url_for, redirect )
from flask.views import MethodView
from rankomatic.forms import LoginForm
from rankomatic.models import User

users = Blueprint('users', __name__, template_folder='templates')

class LoginView(MethodView):

    def get(self):
        return render_template('login.html', form=LoginForm())

    def post(self):
        form = LoginForm(request.form)
        username = form.username.data
        password = form.password.data
        user = User.objects(username=username)
        if user and user.is_password_valid(password):
            session['username'] = username
            flash('You logged in successfully')
            return('this is bad maybe?')
            #TODO redirect to table
        else:
            flash('Incorrect username/password combination')
            flash('Poop')
            return redirect(url_for('.login'))


class SignupView(MethodView):

    def get(self):
        return render_template('signup.html')

    def post(self):
        pass
        #TODO create and validate new User
        #TODO redirect appropriately


users.add_url_rule('/', view_func=LoginView.as_view('login'))
