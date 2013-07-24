"""
File: calculator.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a calculator Blueprint. Displays the calculator, reads the form,
returns the results, etc.
"""
from flask import Blueprint, render_template, request
from flask.views import MethodView
from rankomatic.forms import TableauxForm

calculator = Blueprint('calculator', __name__,
                       template_folder='templates/calculator')

class CalculatorView(MethodView):
    """
    Displays the calculator form and the place it posts to
    """

    def get(self):
        return render_template('tableaux.html', form=TableauxForm(),
                               active='calculator')

    def post(self):
        form = TableauxForm(request.form)
        data = form.data

        # convert the data into what is used by the ranking library
        for c in data['candidates']:
            c['output'] = c.pop('outp')
            c['input'] = c.pop('inp')
            vvec_dict = {}
            for i in range(len(c['vvector'])):
                vvec_dict[i + 1] = c['vvector'][i]
            c['vvector'] = vvec_dict

        # An ugly way to show we have what we want
        ret = "dataset:<br>"
        for c in data['candidates']:
            ret += str(c) + "<br>"

        ret += "<br>constraints:<br>"
        for c in data['constraints']:
            ret += c + ", "

        # proof-of-concept that validation works
        if form.validate():
            return render_template('grammars.html', data = ret)
        else:
            return render_template('grammars.html', data = form.errors)


calculator.add_url_rule('/calculator/',
                        view_func=CalculatorView.as_view('calculator'))
