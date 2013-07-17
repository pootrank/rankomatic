"""
File: forms.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

This file defines several WTForms for use with Flask applications, specifically
the Optimality Theory ranking application.
"""
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField


class LoginForm(Form):
    """
    For use with logging in, only two fields
    """
    username = TextField()
    password = PasswordField()


class SignupForm(LoginForm):
    """
    For use with signing up, same as LoginForm except it has a password
    confirmation field
    """
    password_conf = PasswordField()
