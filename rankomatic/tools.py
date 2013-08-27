"""File: calculator.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a tools Blueprint. Displays the different tools, as of right now
calculator, t-order, reads the forms, returns the results, etc.

"""

import gridfs
import pygraphviz as pgv
import random
import string
import tempfile
from flask import (Blueprint, render_template, request, flash, redirect,
                   url_for, session)
from flask.views import MethodView
from rankomatic.forms import TableauxForm
from rankomatic import db
from ot.poot import PoOT

tools = Blueprint('tools', __name__,
                       template_folder='templates/calculator')

class CalculatorView(MethodView):
    """Displays the calculator form and its POST logic"""

    def get(self):
        return render_template('tableaux.html', form=TableauxForm(),
                               active='calculator', t_order=False)

    def post(self):
        form = TableauxForm(request.form)
        data = form.data
        self.process_form(data)

        if not form.validate():
            for e in form.get_errors():
                flash(e)
            return render_template('tableaux.html', form=form,
                                   active='calculator')
        else:
            # generate grammars
            mongo_db = db.get_pymongo_db()
            poot = PoOT(lat_dir=None, mongo_db=mongo_db)
            poot.dset = data['candidates']
            grammars = poot.get_grammars(classical=False)

            # visualize grammars
            if grammars:
                chars = string.digits + string.letters
                dirlist = [random.choice(chars) for i in xrange(10)]
                dirname = "".join(dirlist)
            else:
                dirname = 'emptyset'
            self.visualize_and_store_grammars(grammars, data['constraints'],
                                              mongo_db, dirname)
            session['num_constraints'] = len(data['constraints'])
            return redirect(url_for('grammars.stats', dirname=dirname))

    def process_form(self, data):
        """Convert raw form data into a useful form"""
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

    def visualize_and_store_grammars(self, grammars, constraints,
                                     mongo_db, dirname):
        """Generate visualization images and store them in GridFS"""
        fs = gridfs.GridFS(mongo_db, collection='tmp')
        cons = dict((i+1, v) for i, v in enumerate(constraints))
        for i, gram in enumerate(grammars):
            graph = self.make_graph(gram, cons)
            with tempfile.TemporaryFile() as tf:
                graph.draw(tf, format='svg')
                tf.seek(0)
                filename = 'grammar%d.svg' % i
                path = "".join([dirname, '/', filename])
                fs.put(tf, filename=path)

    def make_graph(self, grammar, constraints):
        """Create an AGraph version of the given grammar."""
        graph = pgv.AGraph(directed=True)
        for k in constraints:
            graph.add_node(constraints[k])
        for e in grammar:
            graph.add_edge(constraints[e[1]], constraints[e[0]])
        graph.tred()
        graph.layout('dot')
        return graph


class TOrderView(MethodView):
    """Displays the t-order form and the where it posts to. Identical to
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



