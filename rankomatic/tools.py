"""File: calculator.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a tools Blueprint. Displays the different tools, as of right now
calculator, t-order, reads the forms, returns the results, etc.

"""

import random
import string
import urllib
from flask import (Blueprint, render_template, request, Markup,
                   flash, redirect, url_for, session)
from flask.views import MethodView
from rankomatic.forms import TableauxForm
from rankomatic.models import Dataset
from rankomatic.util import get_username, get_dset

tools = Blueprint('tools', __name__,
                  template_folder='templates/calculator')


def _make_random_dset_name():
    chars = string.digits + string.letters
    namelist = [random.choice(chars) for i in xrange(10)]
    return "".join(namelist)


def _get_form_from_dset_name(dset_name):
    dset = get_dset(dset_name)
    form = TableauxForm(from_db=True, **dset.create_form_data())
    return form


def _redirect_to_login(dset_name):
    flash("Log in to edit datasets")
    redirect_url = url_for('.edit', dset_name=dset_name)
    session['redirect_url'] = redirect_url
    return redirect(url_for('users.login'))


def _prepare_to_change_dset_user(dset):
    redirect_url = url_for(".edit", dset_name=urllib.quote(dset.name))
    session['redirect_url'] = redirect_url
    message = '<a href="/login/">Log in</a> to save this dataset'
    flash(Markup(message))
    session['save_new_user'] = True


def _change_dset_user_if_necessary(dset_name):
    try:
        save_new_user = session.pop('save_new_user')
    except KeyError:
        pass
    else:
        if save_new_user:
            dset = get_dset(dset_name)
            dset.user = get_username()
            dset.save()
            message = "Saved %s as %s!" % (dset.name, dset.user)
            flash(message)


class EditView(MethodView):

    def get(self, dset_name):
        if get_username() == "guest":
            return _redirect_to_login(dset_name)
        else:
            _change_dset_user_if_necessary(dset_name)
            return render_template('tableaux.html',
                                   dset_name=dset_name,
                                   form=_get_form_from_dset_name(dset_name),
                                   active='calculator',
                                   t_order=False,
                                   edit=True)

    def post(self, dset_name):
        form = TableauxForm(request.form)
        submit = request.form['submit_button']
        if submit == "Cancel editing":
            flash("Canceled editing %s" % urllib.unquote(dset_name))
            return redirect(url_for("users.account", username=get_username()))
        if not form.validate_for_editing():
            for e in form.get_errors():
                flash(e)
            return render_template('tableaux.html', form=form,
                                   active='calculator', t_order=False,
                                   dset_name=dset_name, edit=True)
        else:
            dset = Dataset(data=form.data, data_is_from_form=True)
            old_dset = get_dset(dset_name)
            dset.user = old_dset.user
            old_dset.delete()
            dset.remove_old_files()
            if submit == "All grammars":
                dset.classical = False
                redirect_url = url_for('grammars.grammars',
                                       dset_name=dset.name, num_rankings=0,
                                       page=0, classical=False)
            else:
                dset.classical = True
                redirect_url = url_for('grammars.grammars',
                                       dset_name=dset.name, num_rankings=0,
                                       page=0, classical=True)
            dset.save()
            return redirect(redirect_url)


class EditCopyView(MethodView):

    def get(self, dset_name):
        if get_username() == "guest":
            return _redirect_to_login(dset_name)
        else:
            dset = get_dset(dset_name)
            dset.name = dset.name + "-copy"
            dset.id = None
            dset.save()
            try:
                get_dset(dset.name)
            except Dataset.MultipleObjectsReturned:
                dset.delete()
                flash("Change the name to make copies.")
                return redirect(url_for('users.account',
                                        username=get_username()))
            else:
                return redirect(url_for('.edit', dset_name=dset.name))


class CalculatorView(MethodView):
    """Displays the calculator form and its POST logic"""

    def get(self):
        return render_template('tableaux.html', form=TableauxForm(),
                               active='calculator', t_order=False)

    def post(self):
        form = TableauxForm(request.form)
        submit = request.form['submit_button']
        if not form.validate():
            for e in form.get_errors():
                flash(e)
            return render_template('tableaux.html', form=form,
                                   active='calculator')
        else:
            dset = Dataset(data=form.data,
                           data_is_from_form=True,
                           user=get_username())
            if not dset.name:
                dset.name = _make_random_dset_name()
            dset.save()
            if submit == "All grammars":
                redirect_url = url_for('grammars.grammars',
                                       dset_name=urllib.quote(dset.name),
                                       num_rankings=0, page=0)
            else:
                redirect_url = url_for('grammars.grammars',
                                       dset_name=urllib.quote(dset.name),
                                       num_rankings=0, page=0, classical=True)

            if get_username() == "guest":
                _prepare_to_change_dset_user(dset)

            return redirect(redirect_url)


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
        # TODO make this pretty
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
            return render_template('tableaux.html', form=form,
                                   active='t-order')


tools.add_url_rule('/calculator/',
                   view_func=CalculatorView.as_view('calculator'))
tools.add_url_rule('/t-order/', view_func=TOrderView.as_view('t_order'))
tools.add_url_rule('/<dset_name>/edit/', view_func=EditView.as_view('edit'))
tools.add_url_rule('/<dset_name>/edit_copy',
                   view_func=EditCopyView.as_view('edit_copy'))
