from rankomatic import app, forms
from rankomatic.models import Dataset
from werkzeug import ImmutableMultiDict
from flask.ext.wtf import Form, FieldList, TextField, FormField, BooleanField
from flask import request
from structures.structures import to_flatten, flattened
import structures.structures as structures
from test_tools import delete_bad_datasets
from nose.tools import with_setup


def add_dset():
    dset = Dataset(name='blank', user='guest')
    dset.save()


def test_flatten():
    with app.test_request_context():
        t = forms.TableauxForm()
    flat = sorted(list(t._flatten(to_flatten)))
    assert flat == sorted(flattened)


class ZeroForm(Form):
    zero = forms.ZeroIntegerField()


def test_zero_integer_field_valid():
    valid_inputs = [("", 0), ("0", 0), ("1", 1),
                    ("100", 100), ("27", 27), (None, 0)]
    for valid_input in valid_inputs:
        yield check_valid_zero_input, valid_input


def check_valid_zero_input(valid_input):
    with app.test_request_context():
        f = ZeroForm(ImmutableMultiDict({'zero': valid_input[0]}))
        assert f.validate()
        assert f.zero.data == valid_input[1]


def test_zero_integer_field_invalid():
    invalid_inputs = ["-1", "-100", "a", "-27"]
    for invalid_input in invalid_inputs:
        yield check_invalid_zero_input, invalid_input


def check_invalid_zero_input(invalid_input):
    with app.test_request_context():
        f = ZeroForm(ImmutableMultiDict({'zero': invalid_input}))
        assert not f.validate()


class CandForm(Form):
    inp = TextField(default="")
    outp = TextField(default="")
    optimal = BooleanField(default="")
    vvector = FieldList(forms.ZeroIntegerField())


class IGForm(Form):
    candidates = FieldList(
        FormField(CandForm),
        validators=[
            forms.InputsSame("inputs differ"),
            forms.OutputsUnique("outputs same"),
            forms.NoSpecialChars("special chars"),
        ]
    )


class ValidatorForm(Form):
    constraints = FieldList(TextField(), validators=[forms.MembersUnique()])
    msg = "none optimal"
    input_groups = FieldList(FormField(IGForm),
                             validators=[forms.AtLeastOneOptimal(msg)])


def test_all_validators_true():
    with app.test_request_context():
        f = ValidatorForm(structures.valid_form_data)
        assert f.validate() is True


def test_all_validators_false():
    for invalid_data in structures.invalid_forms:
        yield check_validator_false, invalid_data


def check_validator_false(invalid_data):
    with app.test_request_context():
        f = ValidatorForm(invalid_data)
        assert f.validate() is False
        assert len(f.errors) == 1


def test_get_errors():
    with app.test_request_context(method="POST",
                                  data=structures.invalid_forms[0]):
        f = forms.TableauxForm(request.form)
        assert not f.validate()
        assert len(f.get_errors()) == 1


@with_setup(add_dset, delete_bad_datasets)
def test_not_unique():
    with app.test_request_context(method="POST",
                                  data=structures.valid_form_data):
        f = forms.TableauxForm(request.form)
        assert not f.validate()
        assert len(f.get_errors()) == 1


@with_setup(add_dset, delete_bad_datasets)
def test_edit_validate():
    # should validate with duplicate
    with app.test_request_context(method="POST",
                                  data=structures.valid_form_data):
        f = forms.TableauxForm(request.form)
        assert f.validate_for_editing()
