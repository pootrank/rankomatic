from nose.tools import raises
from flask import url_for, session
from werkzeug.exceptions import NotFound
from test import OTOrderBaseCase
from rankomatic.models import User, Dataset
from rankomatic.util import get_username, set_username, get_dset, get_url_args


def setup_module():
    john = User(username='john')
    john.set_password('abc')
    john.save()


def teardown_module(self):
    john = User.objects.get(username='john')
    john.delete()


class TestGetUsername(OTOrderBaseCase):

    def test_not_logged_in(self):
        assert get_username() == 'guest'

    def test_logged_in(self):
        with self.client:
            self.client.post(url_for('users.login'), data={'username': 'john',
                                                           'password': 'abc'})
            assert get_username() == 'john'

    def test_login_then_logout(self):
        with self.client:
            self.client.post(url_for('users.login'), data={'username': 'john',
                                                           'password': 'abc'})
            assert get_username() == 'john'
            self.client.get(url_for('users.logout'))
            assert get_username() == 'guest'


class TestSetUsername(OTOrderBaseCase):

    def test_set_no_arguments(self):
        with self.client:
            try:
                session['username']
            except KeyError:
                assert True
            else:
                assert False
            set_username()
            assert session['username'] == 'guest'

    def test_with_argument(self):
        with self.client:
            set_username('john')
            assert session['username'] == 'john'


class TestGetDset(OTOrderBaseCase):

    def setUp(self):
        dset = Dataset(user='john', name='test')
        dset.save()

    def tearDown(self):
        dset = Dataset.objects.get(user='john', name='test')
        dset.delete()

    def test_guest_dset_no_urlquote(self):
        # guest, Kiparsky --> correct dset
        dset = get_dset("Kiparsky")
        assert dset.user == "guest"
        assert dset.name == "Kiparsky"

    def test_guest_dset_url_quoted(self):
        # guest, CV%20Syllabification --> correct dset
        dset = get_dset("CV%20Syllabification")
        assert dset.user == "guest"
        assert dset.name == "CV Syllabification"

    def test_guest_dset_url_unquoted(self):
        # guest, CV Syllabification --> correct dset
        dset = get_dset("CV Syllabification")
        assert dset.user == "guest"
        assert dset.name == "CV Syllabification"

    def test_user_dset_logged_in_dset(self):
        # john, test --> correct dset if logged in
        with self.client:
            self.client.post(url_for('users.login'), data={'username': 'john',
                                                           'password': 'abc'})
            dset = get_dset('test')
            assert dset.name == 'test'
            assert dset.user == 'john'

    @raises(NotFound)
    def test_user_dset_not_logged_in(self):
        # john, test --> 404 if not logged in
        get_dset('test')

    def test_guest_user_logged_in(self):
        # john, Kiparsky --> correct dset
        with self.client:
            self.client.post(url_for('users.login'), data={'username': 'john',
                                                           'password': 'abc'})
            dset = get_dset('Kiparsky')
            assert dset.user == "guest"
            assert dset.name == "Kiparsky"


class TestGetURLArgs(OTOrderBaseCase):

    def test_get_url_args(self):
        with self.app.test_client() as client:
            to_send = (False, 5, "rank_volume")
            client.get(url_for('content.landing', classical=to_send[0],
                               page=to_send[1], sort_by=to_send[2]))
            args = get_url_args()
            assert to_send == args
