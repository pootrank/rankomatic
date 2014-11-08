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
        if self._is_successful_login():
            set_username(username=self.username)
            return self._good_login_html()
        else:
            return self._bad_login_html()

    def _is_successful_login(self):
        self._get_form_data()
        user = self._get_user()
        return user and user.is_password_valid(self.password)

    def _get_form_data(self):
        self.form = LoginForm(request.form)
        self.username = self.form.username.data
        self.password = self.form.password.data

    def _get_user(self):
        try:
            user = User.objects.get(username=self.username)
        except User.DoesNotExist:
            user = None
        return user

    def _bad_login_html(self):
        flash('Incorrect username/password combination')
        return redirect(url_for('.login'))

    def _good_login_html(self):
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
        if self._signup_successful():
            self._create_new_account()
            return self._successful_signup_html()
        else:
            return redirect(url_for('.signup'))

    def _signup_successful(self):
        self._initialize_signup_data()
        return (self._username_is_unique() and
                self._password_meets_criteria())

    def _initialize_signup_data(self):
        self.form = SignupForm(request.form)
        self.username = self.form.username.data
        self.password = self.form.password.data
        self.user = User.objects(username=self.username)

    def _username_is_unique(self):
        if self.user:
            flash('That username has already been chosen.'
                  'Try a different one.')
            return False
        else:
            return True

    def _password_meets_criteria(self):
        return (self._password_matches_confirmation() and
                self._password_is_long_enough())

    def _password_matches_confirmation(self):
        if self.password != self.form.password_conf.data:
            flash("The password confirmation doesn't match.")
            return False
        else:
            return True

    def _password_is_long_enough(self):
        if len(self.password) < 6:
            flash("The password is too short.")
            return False
        else:
            return True

    def _create_new_account(self):
        user = User(username=self.username)
        self._copy_free_datasets(self.username)
        user.set_password(self.password)
        user.save()

    def _successful_signup_html(self):
        flash("Go ahead and log in!")
        return redirect(url_for('.login'))

    def _copy_free_datasets(self, username):
        dset_names = ['CV Syllabification', 'Kiparsky']
        for dset_name in dset_names:
            dset = Dataset.objects.get(user='guest', name=dset_name)
            dset.id = None
            dset.user = username
            dset.save()


class LogoutView(MethodView):

    def get(self):
        set_username()
        flash('You were successfully logged out')
        return redirect(url_for('content.landing'))


class AccountView(MethodView):

    def get(self, username):
        if get_username() != username:
            flash('Log in to view your account')
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
