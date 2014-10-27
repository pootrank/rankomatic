from flask import url_for
from test import OTOrderBaseCase
from rankomatic.models import User, Dataset


#class TestUsersBlueprint(OTOrderBaseCase):

    #def test_signup(self):
        #assert False

    #def test_logout(self):
        #assert False

    #def test_account(self):
        #assert False

    #def test_delete_dset(self):
        #assert False

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
