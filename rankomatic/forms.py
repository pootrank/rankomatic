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
    username = TextField('Username')
    password = PasswordField('Password')

