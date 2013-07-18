"""
File: calculator.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a calculator Blueprint. Displays the calculator, reads the form,
returns the results, etc.
"""
from flask import Blueprint, render_template
from flask.views import MethodView
from rankomatic.forms import TableauxForm

calculator = Blueprint('calculator', __name__, template_folder='templates')

class CalculatorView(MethodView):
    """
    Displays the calculator form and the place it posts to
    """

    def get(self):
        return render_template('tableaux.html', form=TableauxForm(),
                               active='calculator')


calculator.add_url_rule('/calculator/',
                        view_func=CalculatorView.as_view('calculator'))
