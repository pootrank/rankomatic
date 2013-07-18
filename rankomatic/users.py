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
from rankomatic.forms import LoginForm, SignupForm
from rankomatic.models import User

users = Blueprint('users', __name__, template_folder='templates/users')

class LoginView(MethodView):

    def get(self):
        return render_template('login.html', form=LoginForm(),
                               bodyclass='simple-form')

    def post(self):
        form = LoginForm(request.form)
        username = form.username.data
        password = form.password.data
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            flash("User didn't exist")
            user = None
        if user and user.is_password_valid(password):
            session['username'] = username
            flash('Welcome, %s!' % session['username'])
            return redirect(url_for('calculator.calculator'))
            #TODO redirect to table
        else:
            flash('Incorrect username/password combination')
            return redirect(url_for('.login'))


class SignupView(MethodView):

    def get(self):
        return render_template('signup.html', form=SignupForm(),
                               bodyclass='simple-form')

    def post(self):
        form = SignupForm(request.form)
        username = form.username.data
        password = form.password.data

        cancel_create = False  # track errors in creation
        user = User.objects(username=username)
        if user or username == 'about':
            flash('That username has already been chosen. Try a different one.')
            cancel_create = True
        if password != form.password_conf.data:
            flash("The password confirmation doesn't match.")
            cancel_create = True
        if len(password) < 6:
            flash("The password is too short.")
            cancel_create = True
        if cancel_create:
            return redirect(url_for('.signup'))
        user = User(username=username)
        user.set_password(password)
        user.save()
        flash("Go ahead and log in!")
        return redirect(url_for('.login'))


class LogoutView(MethodView):

    def get(self):
        session['username'] = None
        flash('You were successfully logged out')
        return redirect(url_for('content.landing'))


class AccountView(MethodView):

    def get(self, username):
        if session['username'] == username:
            return render_template('account.html',
                                user=User.objects.get_or_404(username=username))
        else:
            flash('Only a user who is logged in can view their account')
            return redirect(url_for('users.login'))


class AboutAccountView(MethodView):

    def get(self):
        return render_template('about_account.html')


users.add_url_rule('/login/', view_func=LoginView.as_view('login'))
users.add_url_rule('/signup/', view_func=SignupView.as_view('signup'))
users.add_url_rule('/logout/', view_func=LogoutView.as_view('logout'))
users.add_url_rule('/account/<username>/', view_func=AccountView.as_view('account'))
users.add_url_rule('/account/about/', view_func=AboutAccountView.as_view('about_account'))
