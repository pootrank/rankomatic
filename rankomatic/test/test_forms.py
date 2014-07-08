from .. import app
from .. import forms

import structures


def test_flatten():
    with app.test_request_context():
        t = forms.TableauxForm()
    assert list(t._flatten(structures.to_flatten)) == structures.flattened
