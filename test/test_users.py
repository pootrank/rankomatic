from flask import url_for
from test import OTOrderBaseCase
from rankomatic.models import User, Dataset


def setup_module():
    john = User(username='john')
    john.set_password('abc')
    john.save()


def teardown_module(self):
    john = User.objects.get(username='john')
    john.delete()


class TestLogin(OTOrderBaseCase):

    def test_get(self):
        response = self.client.get(url_for('users.login'))
        self.assert_status(response, 200)
        self.assert_template_used('login.html')

    def test_password_username_combos(self):
        possible_combinations = [
            ('john', 'abc', url_for('users.account', username='john')),
            ('john', '123', url_for('users.login')),
            ('NOT A USER', 'abc', url_for('users.login')),
            ('NOT A USER', 'NOT A PASSWORD', url_for('users.login'))
        ]

        for combo in possible_combinations:
            response = self.client.post(url_for('users.login'),
                                        data={'username': combo[0],
                                              'password': combo[1]})
            self.assert_redirects(response, combo[2])


class TestSignup(OTOrderBaseCase):

    def test_get(self):
        response = self.client.get(url_for('users.signup'))
        self.assert_status(response, 200)
        self.assert_template_used('signup.html')

    def test_successful_signup(self):
        response = self.client.post(url_for('users.signup'),
                                    data={'username': 'jane',
                                          'password': 'password',
                                          'password_conf': 'password'})
        self.assert_redirects(response, url_for('users.login'))
        user = User.objects.get(username='jane')
        dsets = Dataset.objects(user=user.username)

        assert user.username == 'jane'
        assert user.is_password_valid('password')
        assert len(dsets) == 2

        for dset in dsets:
            dset.delete()

        user.delete()

    def test_unsuccessful_signups(self):
        attempts = [
            {
                'username': 'john',  # name in use
                'password': 'password',
                'password_conf': 'password'
            },
            {
                'username': 'jane',
                'password': 'password',
                'password_conf': 'PASSWORD'  # confirmation doesn't match
            },
            {
                'username': 'jane',
                'password': 'abc',  # password too short
                'password_conf': 'abc'
            }
        ]

        for attempt in attempts:
            response = self.client.post(url_for('users.signup'), data=attempt)
            self.assert_redirects(response, url_for('users.signup'))


class TestLogout(OTOrderBaseCase):

    def test_logout(self):
        with self.client:
            login_response = self.client.post(url_for('users.login'),
                                              data={'username': 'john',
                                                    'password': 'abc'})
            account_response = self.client.get(url_for('users.account',
                                                       username='john'))
            logout_response = self.client.get(url_for('users.logout'))
            logged_out_account_response = self.client.get(
                url_for('users.account', username='john')
            )
            self.assert_redirects(login_response, url_for('users.account',
                                                          username='john'))
            self.assert_status(account_response, 200)
            self.assert_redirects(logout_response, url_for('content.landing'))
            self.assert_redirects(logged_out_account_response,
                                  url_for('users.login'))


class TestAccount(OTOrderBaseCase):

    def test_not_logged_in(self):
        response = self.client.get(url_for('users.account', username='john'))
        self.assert_redirects(response, url_for('users.login'))

    def test_logged_in_as_someone_else(self):
        with self.client:
            self.client.post(url_for('users.login', data={'username': 'john',
                                                          'password': 'abc'}))
            response = self.client.get(url_for('users.account',
                                               username='jane'))
            self.assert_redirects(response, url_for('users.login'))

    def test_logged_in(self):
        with self.client:
            self.client.post(url_for('users.login'), data={'username': 'john',
                                                           'password': 'abc'})
            response = self.client.get(url_for('users.account',
                                               username='john'))
            self.assert_status(response, 200)
            assert 'john' in response.data


class TestDeleteDataset(OTOrderBaseCase):

    def setUp(self):
        dset = Dataset(user='john', name='test')
        dset.save()

    def tearDown(self):
        try:
            dset = Dataset.objects.get(user='john', name='test')
        except Dataset.DoesNotExist:
            pass
        else:
            dset.delete()

    def test_not_logged_in(self):
        response = self.client.get(url_for('users.delete_dataset',
                                           dset_name='test'))
        self.assert_status(response, 404)

    def test_logged_in(self):
        with self.client:
            self.client.post(url_for('users.login'), data={'username': 'john',
                                                           'password': 'abc'})
            response = self.client.get(url_for('users.delete_dataset',
                                               dset_name='test'))

            expected_response = "deletion of test successful"
            self.assert_status(response, 200)
            assert response.data == expected_response
