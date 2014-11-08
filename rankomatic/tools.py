"""File: calculator.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines a tools Blueprint. Displays the different tools, as of right now
calculator, t-order, reads the forms, returns the results, etc.

"""

import random
import string
import urllib
from mongoengine import OperationError as MongoInsertError
from flask import (Blueprint, render_template, request, Markup,
                   flash, redirect, url_for, session)
from flask.views import MethodView
from rankomatic.forms import TableauxForm
from rankomatic.models import Dataset
from rankomatic.util import (get_username, get_dset, is_logged_in,
                             redirect_to_login, get_form_from_dset_name)

tools = Blueprint('tools', __name__,
                  template_folder='templates/calculator')


def requires_login(func):

    def wrapper(*args, **kwargs):
        if get_username() == "guest":
            return redirect_to_login(kwargs['dset_name'])
        else:
            return func(*args, **kwargs)

    return wrapper


def validates_tableaux_form(func):

    def wrapper(*args, **kwargs):

        obj = args[0]
        if obj.form.validate():
            return func(*args, **kwargs)
        else:
            return obj.redisplay_form()

    return wrapper


def init_tableaux_form_on_self(func):
    def wrapper(*args, **kwargs):
        obj = args[0]
        obj.form = TableauxForm(request.form)
        obj.submit = request.form['submit_button']
        return func(*args, **kwargs)
    return wrapper


class CalculatorView(MethodView):
    """Displays the calculator form and its POST logic"""

    def get(self):
        return render_template('tableaux.html', form=TableauxForm(),
                               active='calculator', t_order=False)

    @init_tableaux_form_on_self
    @validates_tableaux_form
    def post(self):
        self._initialize_dset()
        if self.dset_save_is_successful():
            self.prepare_to_change_dset_user()
            return self._successful_post_html()
        else:
            return self._unsuccessful_post_html()

    def _unsuccessful_post_html(self):
        self.form.errors['form'] = "A dataset with that name already exists"
        return self.redisplay_form()

    def _successful_post_html(self):
        redirect_url = self._generate_redirect_url()
        return redirect(redirect_url)

    def prepare_to_change_dset_user(self):
        if not is_logged_in():
            redirect_url = url_for(".edit", dset_name=self.dset.name)
            session['redirect_url'] = redirect_url
            message = '<a href="/login/">Log in</a> to save this dataset'
            flash(Markup(message))
            session['save_new_user'] = True

    def _generate_redirect_url(self):
        if self.is_submitting_to_all_grammars():
            return self._get_all_grammar_url()
        else:
            return self._get_classical_grammar_url()

    def _get_all_grammar_url(self):
        return url_for(
            'grammars.grammars', dset_name=urllib.quote(self.dset.name),
            sort_value=0, page=0, classical=False, sort_by='rank_volume'
        )

    def _get_classical_grammar_url(self):
        return url_for(
            'grammars.grammars', dset_name=self.dset.name, sort_value=0,
            page=0, classical=True, sort_by='rank_volume'
        )

    def is_submitting_to_all_grammars(self):
        return self.submit == "All grammars"

    def get_redisplay_html(self):
        return render_template('tableaux.html', form=self.form,
                               active='calculator')

    def _initialize_dset(self):
        self.dset = Dataset(data=self.form.data, data_is_from_form=True,
                            user=get_username())
        if not self.dset.name:
            self.dset.name = self.make_unique_random_dset_name()

    def make_unique_random_dset_name(self):
        # keep trying until you get something not in the database
        random_name = self._random_name_attempt()
        while Dataset.objects(name=random_name, user=get_username()):
            random_name = self._random_name_attempt()
        return random_name

    def _random_name_attempt(self):
        chars = string.digits + string.letters
        namelist = [random.choice(chars) for i in xrange(10)]
        return "".join(namelist)

    def dset_save_is_successful(self):
        try:
            self.dset.save()
        except MongoInsertError:
            return False
        return True

    def redisplay_form(self):
        for e in self.form.get_errors():
            flash(e)
        return self.get_redisplay_html()


class EditView(CalculatorView):

    @requires_login
    def get(self, dset_name):
        self.dset_name = dset_name
        if self._need_to_change_dset_user():
            self._change_dset_user()
        return render_template(
            'tableaux.html', dset_name=dset_name,
            form=get_form_from_dset_name(dset_name), active='calculator',
            t_order=False, edit=True
        )

    def _need_to_change_dset_user(self):
        try:
            return session.pop('save_new_user')
        except KeyError:
            return False

    def _change_dset_user(self):
            dset = get_dset(self.dset_name)
            dset.user = get_username()
            dset.save()
            flash("Saved %s as %s!" % (dset.name, dset.user))

    @init_tableaux_form_on_self
    @validates_tableaux_form
    def post(self, dset_name):
        self.dset_name = dset_name
        if self._is_cancelling_edit():
            return self._cancel_edit_html()
        else:
            return self._successful_edit_html()

    def _is_cancelling_edit(self):
        return self.submit == "Cancel editing"

    def _cancel_edit_html(self):
        flash("Canceled editing %s" % self.dset_name)
        return redirect(url_for("users.account", username=get_username()))

    def _successful_edit_html(self):
        self._delete_old_version()
        self._save_new_version()
        return self._generate_redirect()

    def _delete_old_version(self):
        self.dset = Dataset(data=self.form.data, data_is_from_form=True)
        old_dset = get_dset(self.dset_name)
        self.dset.user = old_dset.user
        old_dset.delete()
        self.dset.remove_old_files()

    def _save_new_version(self):
        self.dset.classical = not self.is_submitting_to_all_grammars()
        self.dset.save()

    def _generate_redirect(self):
        return redirect(url_for(
            'grammars.grammars', dset_name=self.dset.name, sort_value=0,
            page=0, classical=self.dset.classical, sort_by='rank_volume'
        ))

    def get_redisplay_html(self):
        return render_template(
            'tableaux.html', form=self.form, active='calculator',
            t_order=False, dset_name=self.form.name, edit=True
        )


class EditCopyView(CalculatorView):

    @requires_login
    def get(self, dset_name):
        self._initialize_copy_of_dset(dset_name)
        if self.dset_save_is_successful():
            return self._successful_copy_html()
        else:
            return self._unsuccessful_copy_html()

    def _initialize_copy_of_dset(self, dset_name):
        self.dset_name = dset_name
        self._create_copy_of_dset()

    def _create_copy_of_dset(self):
        self.dset = get_dset(self.dset_name)
        self.dset.name = self.dset.name + "-copy"
        self.dset.id = None

    def _successful_copy_html(self):
        return redirect(url_for('.edit', dset_name=self.dset.name))

    def _unsuccessful_copy_html(self):
        flash("Change the name to make copies.")
        return redirect(url_for('users.account', username=get_username()))


class ExampleEditView(CalculatorView):

    def get(self):
        return render_template(
            'tableaux.html', dset_name="Kiparsky",
            form=get_form_from_dset_name("Kiparsky"), active='calculator',
            edit=False, example=True, js_includes=['example_edit.js']
        )

    @init_tableaux_form_on_self
    @validates_tableaux_form
    def post(self):
        self._create_dset_for_editing()
        self.prepare_to_change_dset_user()
        return redirect(self._generate_redirect_url())

    def _create_dset_for_editing(self):
        self.dset = Dataset(data=self.form.data, data_is_from_form=True)
        self.dset.remove_old_files()
        self.dset.user = get_username()
        self.dset.name = self._create_temporary_dset_name()
        self.dset.id = None  # to get a new id when saved
        self.dset.classical = not self.is_submitting_to_all_grammars()
        self.dset.save()

    def _generate_redirect_url(self):
        return url_for(
            'grammars.grammars', dset_name=self.dset.name, sort_value=0,
            page=0, classical=self.dset.classical, sort_by='rank_volume'
        )

    def _create_temporary_dset_name(self):
        # keep trying strings until you get a unique one
        temp_name = self._get_temp_name_attempt()
        while Dataset.objects(name=temp_name, user=get_username()):
            temp_name = self._get_temp_name_attempt()
        return temp_name

    def _get_temp_name_attempt(self):
        return self.dset.name + '-tmp-' + self.make_unique_random_dset_name()

    def get_redisplay_html(self):
        return render_template(
            'tableaux.html', form=self.form, active='calculator',
            dset_name="Kiparsky", edit=True
        )


tools.add_url_rule('/calculator/',
                   view_func=CalculatorView.as_view('calculator'))
tools.add_url_rule('/<dset_name>/edit/', view_func=EditView.as_view('edit'))
tools.add_url_rule('/<dset_name>/edit_copy',
                   view_func=EditCopyView.as_view('edit_copy'))
tools.add_url_rule('/example_edit/',
                   view_func=ExampleEditView.as_view('example_edit'))
