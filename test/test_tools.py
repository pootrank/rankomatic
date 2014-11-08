from flask import url_for, session
from test import OTOrderBaseCase
from rankomatic.forms import TableauxForm
from rankomatic.models import Dataset, User
import mock
from rankomatic.tools import CalculatorView


login_data = {'username': 'john', 'password': 'abc'}


def login(client):
    client.post(url_for('users.login'), data=login_data)


def setup_module():
    john = User(username=login_data['username'])
    john.set_password(login_data['password'])
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


def create_valid_empty_tableaux_data(test_case):
    data = create_empty_tableaux_data(test_case)
    data['input_groups-0-candidates-0-optimal'] = 'true'
    return data


def create_empty_tableaux_data(test_case):
    with test_case.client:
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


class MockChooser():

    attempts = 0

    @classmethod
    def choose(self, itr):
        to_return = itr[MockChooser.attempts / 10]
        MockChooser.attempts += 1
        return to_return


class TestCalculator(OTOrderBaseCase):

    def setUp(self):
        pass

    def tearDown(self):
        delete_bad_datasets()

    def test_get(self):
        response = self.client.get(url_for('tools.calculator'))
        self.assert_200(response)
        self.assert_template_used('tableaux.html')

    def test_invalid_form(self):
        # form is empty
        data = create_empty_tableaux_data(self)
        response = self.client.post(url_for('tools.calculator'), data=data)
        self.assert_200(response)
        self.assert_template_used('tableaux.html')

    def test_duplicate_dset(self):
        dset = Dataset(name='blank', user='guest')
        dset.save()
        data = create_valid_empty_tableaux_data(self)
        response = self.client.post(url_for('tools.calculator'), data=data)
        self.assert_200(response)
        self.assert_template_used('tableaux.html')
        assert "name already exists" in response.data

    def test_valid_empty_dataset(self):
        data = create_valid_empty_tableaux_data(self)
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
        data = create_valid_empty_tableaux_data(self)
        data.pop("name")
        response = self.client.post(url_for('tools.calculator'), data=data)
        self.assert_status(response, 302)
        dsets = Dataset.objects(user='guest')
        assert len(dsets) == 3
        delete_bad_datasets()

    def test_redirect_to_classical_grammars(self):
        data = create_empty_tableaux_data(self)
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
        data = create_valid_empty_tableaux_data(self)
        with self.client:
            login(self.client)
            response = self.client.post(url_for('tools.calculator'), data=data)
            dset = Dataset.objects.get(name='blank')
            self.assert_redirects(response, url_for('grammars.grammars',
                                                    dset_name='blank',
                                                    sort_value=0, page=0,
                                                    classical=False,
                                                    sort_by='rank_volume'))
            assert dset.user == login_data['username']
            try:
                session['redirect_url']
            except KeyError:
                assert True
            else:
                assert False
            dset.delete()

    @mock.patch('random.choice', MockChooser.choose)
    def test_make_unique_random_dset_name(self):
        dset = Dataset(user='guest', name='0000000000')
        dset.save()
        with self.app.test_request_context():
            name = CalculatorView().make_unique_random_dset_name()
            assert name == "1111111111"


class MockStringMaker():

    num_to_use = 0

    @classmethod
    def make_string(cls):
        string = str(cls.num_to_use)
        cls.num_to_use += 1
        return string


class TestExampleEdit(OTOrderBaseCase):

    def setUp(self):
        pass

    def tearDown(self):
        delete_bad_datasets()

    def test_unlogged_in_get(self):
        response = self.client.get(url_for('tools.example_edit'))
        self.assert_200(response)
        assert "saved by logging in" in response.data

    def test_logged_in_get(self):
        with self.client:
            login(self.client)
            response = self.client.get(url_for('tools.example_edit'))
            self.assert_200(response)
            assert "saved to your account" in response.data

    def test_unlogged_in_valid_post(self):
        data = create_valid_empty_tableaux_data(self)
        with self.client:
            response = self.client.post(url_for('tools.example_edit'),
                                        data=data)
            self.assert_status(response, 302)
            guest_dsets = Dataset.objects(user='guest')
            assert len(guest_dsets) == 3
            try:
                session['redirect_url']
            except KeyError:
                assert False
            else:
                assert True

    def test_logged_in_valid_post(self):
        data = create_valid_empty_tableaux_data(self)
        with self.client:
            login(self.client)
            response = self.client.post(url_for('tools.example_edit'),
                                        data=data)
            self.assert_status(response, 302)
            assert "classical=False" in response.location
            guest_dsets = Dataset.objects(user='guest')
            user_dsets = Dataset.objects(user=login_data['username'])
            assert len(guest_dsets) == 2
            assert len(user_dsets) == 1

    @mock.patch('rankomatic.tools.CalculatorView.make_unique_random_dset_name',
                MockStringMaker.make_string)
    def test_duplicate_save_name(self):
        # should keep getting strings until it finds a unique one
        dset_name = "Kiparsky-tmp-0"
        dset = Dataset(user=login_data['username'], name=dset_name)
        dset.save()
        data = create_valid_empty_tableaux_data(self)
        data['name'] = "Kiparsky"
        with self.client:
            login(self.client)
            response = self.client.post(url_for('tools.example_edit'),
                                        data=data)
            self.assert_status(response, 302)
            assert "Kiparsky-tmp-1" in response.location

    def test_invalid_post(self):
        data = create_empty_tableaux_data(self)
        response = self.client.post(url_for('tools.example_edit'), data=data)
        self.assert_200(response)
        self.assert_template_used('tableaux.html')
        assert "at least one optimal" in response.data

    def test_redirect_to_classical(self):
        data = create_valid_empty_tableaux_data(self)
        data['submit_button'] = "Classical grammars"
        with self.app.test_client() as client:
            response = client.post(url_for('tools.example_edit'),
                                   data=data)
            assert "classical=True" in response.location


class EditCase(OTOrderBaseCase):

    __test__ = False

    def setUp(self):
        dset = Dataset(user='john', name='blank')
        self.url = None
        dset.save()

    def tearDown(self):
        delete_bad_datasets()

    def test_not_logged_in(self):
        with self.client:
            response = self.client.get(self.url)
            self.assert_redirects(response, url_for('users.login'))
            try:
                session['redirect_url']
            except KeyError:
                assert False
            else:
                assert True


class TestEditCopy(EditCase):

    __test__ = True

    def setUp(self):
        super(TestEditCopy, self).setUp()
        self.url = url_for('tools.edit_copy', dset_name='blank')

    def test_logged_in(self):
        with self.client:
            login(self.client)
            response = self.client.get(self.url)
            self.assert_redirects(response, url_for('tools.edit',
                                                    dset_name='blank-copy'))
            user_dsets = Dataset.objects(user=login_data['username'])
            assert len(user_dsets) == 2

    def test_duplicate_name(self):
        dset = Dataset(user=login_data['username'], name='blank-copy')
        dset.save()
        with self.client:
            login(self.client)
            response = self.client.get(self.url)
            self.assert_redirects(response,
                                  url_for('users.account',
                                          username=login_data['username']))


class TestEdit(EditCase):

    __test__ = True

    def setUp(self):
        super(TestEdit, self).setUp()
        self.url = url_for('tools.edit', dset_name='blank')

    def test_get_logged_in(self):
        with self.client:
            login(self.client)
            response = self.client.get(url_for('tools.edit',
                                               dset_name='blank'))
            self.assert_200(response)
            assert "blank" in response.data

    def test_change_dset_user(self):
        data = create_valid_empty_tableaux_data(self)
        data['name'] = 'blank2'
        with self.client:
            self.client.post(url_for('tools.calculator'), data=data)
            login(self.client)
            self.client.get(url_for('tools.edit', dset_name='blank2'))
            dset = Dataset.objects.get(name='blank2')
            assert dset.user == login_data['username']

    def test_cancel_post_logged_in(self):
        data = create_valid_empty_tableaux_data(self)
        data['submit_button'] = "Cancel editing"
        with self.client:
            login(self.client)
            response = self.client.post(self.url, data=data)
            self.assert_redirects(response, url_for(
                'users.account',
                username=login_data['username']
            ))

    def test_invalid_form(self):
        data = create_empty_tableaux_data(self)
        with self.client:
            login(self.client)
            response = self.client.post(self.url, data=data)
            self.assert_200(response)
            self.assert_template_used('tableaux.html')
            assert "Editing" in response.data

    def test_valid_post(self, classical=False, data=None):
        if data is None:
            data = create_valid_empty_tableaux_data(self)
        dset = Dataset.objects.get(name='blank')
        assert dset.constraints[0] == ""
        with self.client:
            login(self.client)
            response = self.client.post(self.url, data=data)
        edited_dset = Dataset.objects.get(name='blank')
        self.assert_redirects(response, url_for(
            'grammars.grammars', dset_name='blank', sort_value=0,
            page=0, classical=classical, sort_by='rank_volume'
        ))
        assert edited_dset.id != dset.id
        assert edited_dset.constraints[0] == "C0"

    def test_classical_post(self):
        data = create_valid_empty_tableaux_data(self)
        data['submit_button'] = "Classical grammars"
        self.test_valid_post(classical=True, data=data)
