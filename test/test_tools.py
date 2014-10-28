from flask import url_for, session
from test import OTOrderBaseCase
from rankomatic.forms import TableauxForm
from rankomatic.models import Dataset, User


def setup_module():
    john = User(username='john')
    john.set_password('abc')
    john.save()


def teardown_module():
    john = User.objects.get(username='john')
    john.delete()
    delete_bad_datasets()


def delete_bad_datasets():
    dsets = [d for d in Dataset.objects() if is_bad_dset(d)]
    for dset in dsets:
        dset.delete()


def is_bad_dset(dset):
    permanent_names = ['Kiparsky', 'CV Syllabification']
    return dset.user != 'guest' or dset.name not in permanent_names


class TestCalculator(OTOrderBaseCase):

    def test_get(self):
        response = self.client.get(url_for('tools.calculator'))
        self.assert_200(response)
        self.assert_template_used('tableaux.html')

    def test_invalid_form(self):
        # form is empty
        data = self.create_empty_tableaux_data()
        response = self.client.post(url_for('tools.calculator'), data=data)
        print response.status
        print response.headers
        print response.data
        self.assert_200(response)
        self.assert_template_used('tableaux.html')

    def test_valid_empty_dataset(self):
        data = self.create_valid_empty_tableaux_data()
        response = self.client.post(url_for('tools.calculator'), data=data)
        dset = Dataset.objects.get(name='blank')
        self.assert_redirects(response, url_for('grammars.grammars',
                                                dset_name='blank',
                                                sort_value=0, page=0,
                                                classical=False,
                                                sort_by='rank_volume'))
        assert dset.name == 'blank'
        assert dset.user == 'guest'
        dset.delete()

    def test_valid_empty_dataset_gets_random_name(self):
        data = self.create_valid_empty_tableaux_data()
        data.pop("name")
        response = self.client.post(url_for('tools.calculator'), data=data)
        self.assert_status(response, 302)
        dsets = Dataset.objects(user='guest')
        assert len(dsets) == 3
        delete_bad_datasets()

    def test_redirect_to_classical_grammars(self):
        data = self.create_empty_tableaux_data()
        data['input_groups-0-candidates-0-optimal'] = 'true'
        data['submit_button'] = "CLassical grammars"
        with self.client:
            response = self.client.post(url_for('tools.calculator'), data=data)
            dset = Dataset.objects.get(name='blank')
            self.assert_redirects(response, url_for('grammars.grammars',
                                                    dset_name='blank',
                                                    sort_value=0, page=0,
                                                    classical=True,
                                                    sort_by="rank_volume"))
            assert dset.user == "guest"
            assert session['redirect_url']
            dset.delete()

    def test_logged_in_user(self):
        data = self.create_valid_empty_tableaux_data()
        username = 'john'
        with self.client:
            self.client.post(url_for('users.login'),
                             data={'username': username, 'password': 'abc'})
            response = self.client.post(url_for('tools.calculator'), data=data)
            dset = Dataset.objects.get(name='blank')
            self.assert_redirects(response, url_for('grammars.grammars',
                                                    dset_name='blank',
                                                    sort_value=0, page=0,
                                                    classical=False,
                                                    sort_by='rank_volume'))
            assert dset.user == username
            try:
                session['redirect_url']
            except KeyError:
                assert True
            else:
                assert False
            dset.delete()

    def create_valid_empty_tableaux_data(self):
        data = self.create_empty_tableaux_data()
        data['input_groups-0-candidates-0-optimal'] = 'true'
        return data

    def create_empty_tableaux_data(self):
        with self.client:
            to_return = {'submit_button': 'All grammars',
                         'name': 'blank'}
            form = TableauxForm()
            for i, constraint in enumerate(form.constraints):
                to_return[constraint.name] = "C%d" % i
            for ig in form.input_groups:
                for candidate in ig.candidates:
                    to_return[candidate.inp.name] = "I1"
                    to_return[candidate.outp.name] = "O1"
                    for v in candidate.vvector:
                        to_return[v.name] = ""
            return to_return
