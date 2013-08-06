"""
File: calculator.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a tools Blueprint. Displays the different tools, as of right now
calculator, t-order, reads the forms, returns the results, etc.
"""
from flask import Blueprint, render_template, request, flash
from flask.views import MethodView
from rankomatic.forms import TableauxForm
from rankomatic import db
from ot.poot import PoOT

tools = Blueprint('tools', __name__,
                       template_folder='templates/calculator')

class CalculatorView(MethodView):
    """
    Displays the calculator form and the place it posts to
    """

    def get(self):
        return render_template('tableaux.html', form=TableauxForm(),
                               active='calculator', t_order=False)

    def post(self):
        form = TableauxForm(request.form)
        data = form.data

        # convert the data into (almost) what is used by the ranking library
        data['candidates'] = []
        for ig in data['input_groups']:
            for c in ig['candidates']:
                c['output'] = c.pop('outp')
                c['input'] = c.pop('inp')
                vvec_dict = {}
                for i in range(len(c['vvector'])):
                    vvec_dict[i + 1] = c['vvector'][i]
                c['vvector'] = vvec_dict
                data['candidates'].append(c)
        data.pop('input_groups')

        # An ugly way to show we have what we want
        #TODO make this pretty
        ret = "dataset:<br>"
        for c in data['candidates']:
            ret += str(c) + "<br>"

        ret += "<br>constraints:<br>"
        for c in data['constraints']:
            ret += c + ", "


        if form.validate():
            mongo_db = getattr(db.connection, db.app.config['MONGODB_SETTINGS']['DB'])
            poot = PoOT(lat_dir=None, mongo_db=mongo_db)
            poot.dset = data['candidates']
            grammars = poot.get_grammars(classical=False)

            # An ugly way to show we have what we want
            #TODO make this pretty
            ret = "grammars:<br>"
            for s in grammars:
                ret += str(list(s)) + "<br>"
            ret += "<br>constraints:<br>"
            for c in data['constraints']:
                ret += c + ", "
            return render_template('grammars.html', data=ret)
        else:
            for e in form.get_errors():
                flash(e)
            return render_template('tableaux.html', form=form, active='calculator')


class TOrderView(MethodView):
    """
    Displays the t-order form and the where it posts to. Identical to
    calculator, except there is no option for optimality.
    """

    def get(self):
        return render_template('tableaux.html', form=TableauxForm(),
                               active='t-order', t_order=True)

    def post(self):
        form = TableauxForm(request.form)
        data = form.data

        # convert the data into (almost) what is used by the ranking library
        data['candidates'] = []
        for ig in data['input_groups']:
            for c in ig['candidates']:
                c['output'] = c.pop('outp')
                c['input'] = c.pop('inp')
                c['optimal'] = True
                vvec_dict = {}
                for i in range(len(c['vvector'])):
                    vvec_dict[i + 1] = c['vvector'][i]
                c['vvector'] = vvec_dict
                data['candidates'].append(c)
        data.pop('input_groups')

        # An ugly way to show we have what we want
        #TODO make this pretty
        ret = "dataset:<br>"
        for c in data['candidates']:
            ret += str(c) + "<br>"

        ret += "<br>constraints:<br>"
        for c in data['constraints']:
            ret += c + ", "


        if form.validate():
            return render_template('grammars.html', data=ret)
        else:
            for e in form.get_errors():
                flash(e)
            return render_template('tableaux.html', form=form, active='t-order')


tools.add_url_rule('/calculator/',
                        view_func=CalculatorView.as_view('calculator'))
tools.add_url_rule('/t-order/', view_func=TOrderView.as_view('t_order'))