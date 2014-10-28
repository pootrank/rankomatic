from rankomatic import models


def test_user_password():
    user = models.User(username='test')
    user.set_password('poopie')
    assert user.is_password_valid('poopie')
    assert not user.is_password_valid('WRONG')
