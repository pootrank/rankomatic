"""
File: users.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a users Blueprint for use with a Flask app. This was developed for use
with an Optimality Theory constraint-ranking app
(github.com/pootrank/rankomatic), but is intended to be somewhat general.
"""
from flask import (Blueprint, render_template, request,
                   session, flash, url_for, redirect)
from flask.views import MethodView
from rankomatic.forms import LoginForm, SignupForm
from rankomatic.models import User, Dataset
from rankomatic.util import get_username, set_username, get_dset

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
            user = None
        if not user or not user.is_password_valid(password):
            flash('Incorrect username/password combination')
            return redirect(url_for('.login'))
        else:
            set_username(username=username)
            flash('Welcome, %s!' % get_username())
            try:
                redirect_url = session.pop('redirect_url')
            except KeyError:
                redirect_url = url_for('.account', username=get_username())
            return redirect(redirect_url)


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
        if user:
            flash('That username has already been chosen.'
                  'Try a different one.')
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
        set_username()
        flash('You were successfully logged out')
        return redirect(url_for('content.landing'))


class AccountView(MethodView):

    def get(self, username):
        if get_username() != username:
            flash('Only a user who is logged in can view their account')
            return redirect(url_for('users.login'))
        else:
            user = User.objects.get_or_404(username=username)
            dsets = Dataset.objects(user=user.username)
            return render_template('account.html', user=user, dsets=dsets)


class DeleteDatasetView(MethodView):

    def get(self, dset_name):
        d = get_dset(dset_name)
        d.delete()
        return "deletion of %s successful" % d.name



users.add_url_rule('/login/', view_func=LoginView.as_view('login'))
users.add_url_rule('/signup/', view_func=SignupView.as_view('signup'))
users.add_url_rule('/logout/', view_func=LogoutView.as_view('logout'))
users.add_url_rule('/account/<username>/',
                   view_func=AccountView.as_view('account'))
users.add_url_rule('/delete/<dset_name>/',
                  view_func=DeleteDatasetView.as_view('delete_dataset'))
