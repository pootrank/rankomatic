"""
File: forms.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

This file defines several WTForms for use with Flask applications, specifically
the Optimality Theory ranking application.
"""
from flask.ext.wtf import Form
from wtforms import (TextField, PasswordField, FieldList, FormField,
                     BooleanField, IntegerField, validators)


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


class ZeroIntegerField(IntegerField):
    """
    Based on the IntegerField in wtforms, this field type converts a blank
    form entry into the integer 0, and allows for the value to be 0.
    """
    #TODO for reuse, put this in wtforms and replace the error message with
    #     something more generic

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] is None or len(valuelist[0]) == 0:
                self.data = 0
            else:
                try:
                    self.data = int(valuelist[0])
                except ValueError:
                    self.data = None
                    raise ValueError("Violation vectors " +
                                     "must consist only of integers")


class CandidateForm(Form):
    """
    This form creates the candidate rows in the Tableaux, as well as handles
    all their validation.
    """

    inp = TextField(default="",
                    validators=[validators.Length(min=1, max=255,
                                    message="All input names must be between " +
                                            "1 and 255 characters in length")]
    )
    outp = TextField(default="",
                     validators=[validators.Length(min=1, max=255,
                                    message="All output names must be between " +
                                            "1 and 255 characters in length")]
    )
    optimal = BooleanField(validators=[validators.AnyOf([True, False],
                    message="The checkboxes must be either checked or " +
                            "unchecked, no other values will be accepted")]
    )
    vvector = FieldList(
        ZeroIntegerField(),
        default=[ZeroIntegerField(default=0) for x in range(3)]
    )


class TableauxForm(Form):
    """
    This form creats the Tableaux, displayed as the main calculator.
    """

    msg = "All constraint names must be between 1 and 255 characters in length"
    len_validator = validators.Length(min=1, max=255, message=msg)
    constraints = FieldList(
        TextField(validators=[len_validator]),
        default=[TextField(default="",
                           validators=[len_validator]) for x in range(3)],
    )
    candidates = FieldList(FormField(CandidateForm),
        default=[CandidateForm(csrf_enabled=False)],
    )

