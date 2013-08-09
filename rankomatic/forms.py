"""
File: forms.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

This file defines several WTForms for use with Flask applications, specifically
the Optimality Theory ranking application.
"""
import itertools
from flask.ext.wtf import Form
from wtforms import (TextField, PasswordField, FieldList, FormField,
                     BooleanField, IntegerField, validators)
from wtforms.validators import ValidationError


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
                    raise ValueError("Violation vectors must consist of non-negative integers")
                    #TODO refactor this so the error can be handled someplace else


class CandidateForm(Form):
    """
    This form creates the candidate rows in the Tableaux, as well as handles
    all their validation.
    """

    inp = TextField(default="",
                    validators=[validators.Length(min=1, max=255,
                                    message="Input names must be between " +
                                            "1 and 255 characters in length")]
    )
    outp = TextField(default="",
                     validators=[validators.Length(min=1, max=255,
                                    message="Output names must be between "+
                                            "1 and 255 characters in length")]
    )
    optimal = BooleanField(validators=[validators.AnyOf([True, False],
                    message="Checkboxes must be either checked (true) or " +
                            "unchecked (false)")]
    )
    vvector = FieldList(
        ZeroIntegerField(validators=[
            validators.NumberRange(min=0, message="Violation vectors must consist of non-negative integers")]),
        default=[ZeroIntegerField(default=0) for x in range(3)],
        validators=[validators.Length(min=2, max=5, message="There must be between 2 and 5 constraints")]
    )


class MembersUnique(object):
    """Checks to make sure its members are unique."""

    def __init__(self, message=None):
        if not message:
            message = "Each element of the list must be unique"
        self.message = message

    def __call__(self, form, field):
        if len(field.data) > len(set(field.data)):
            raise ValidationError(self.message)


class InputsSame(object):
    """Raise an error if the inputs differ in the input group."""

    def __init__(self, message=None):
        if not message:
            message = "The inputs in an input group must be identical to one another"
        self.message = message

    def __call__(self, form, field):
        inps = [c['inp'] for c in field.data]
        if len(set(inps)) > 1:
            raise ValidationError(self.message)


class OutputsUnique(object):
    """Raise an error if the outputs are not unique."""

    def __init__(self, message=None):
        if not message:
            message = "Each output in an input group must be unique"
        self.message = message

    def __call__(self, form, field):
        outps = [c['outp'] for c in field.data]
        if len(outps) > len(set(outps)):
            raise ValidationError(self.message)


class InputGroupForm(Form):
    """Represents a group of outputs for one input."""
    candidates = FieldList(FormField(CandidateForm),
                           default=[FormField(CandidateForm, csrf_enabled=False)],
                           validators=[InputsSame(), OutputsUnique()])


class AtLeastOneOptimal(object):
    """Make sure there is at least one optimal candidate."""

    def __init__(self, message=None):
        if not message:
            message = "There must be at least one optimal candidate."
        self.message = message

    def __call__(self, form, field):
        cands = [c['candidates'] for c in field.data]
        cands = list(itertools.chain(*cands))
        opts = [c['optimal'] for c in cands]
        if not any(opts):
            raise ValidationError(self.message)


class TableauxForm(Form):
    """Creates the Tableaux, displayed as the main calculator."""
    msg = "Constraint names must be between 1 and 255 characters in length"
    len_validator = validators.Length(min=1, max=255, message=msg)

    constraints = FieldList(
        TextField(validators=[len_validator]),
        default=[TextField(default="",
                           validators=[len_validator]) for x in range(3)],
        validators=[MembersUnique("Constraints must be unique"),
                    validators.Length(min=2, max=5, message="There must be between 2 and 5 constraints")]
    )

    input_groups = FieldList(FormField(InputGroupForm),
                             default=[FormField(InputGroupForm, csrf_enabled=False)],
                             validators=[AtLeastOneOptimal()]
    )

    def _flatten(self, d):
        """Flattens a dict into a single list, throwing away keys.
        if d looks like this:
            {'a': [{'1': 'bad', '2': 'worse' }]
             'b': ['oh no!', [['that didn't work'], ['that didn't work']]]}
        the return value is (although not necessarily sorted):
            ['bad', 'worse', 'oh no!', 'that didn't work', 'that didn't work']
        Code based on intuited's SO response: http://stackoverflow.com/a/3835478

        """
        try:
            for v in d.itervalues():
                for nested_v in self._flatten(v):
                    yield nested_v
        except AttributeError:
            if type(d) is list:
                for list_v in d:
                    for nested_in_list in self._flatten(list_v):
                        yield nested_in_list
            elif type(d) is str or type(d) is unicode:
                yield d
            else:
                for list_v in d:
                    yield list_v

    def get_errors(self):
        """return the errors in a uniq'd list."""
        return list(set([e for e in self._flatten(self.errors)]))

