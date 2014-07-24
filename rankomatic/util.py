import urllib
from rankomatic.models import Dataset
from flask import session


def get_username():
    try:
        return session['username']
    except KeyError:
        set_username()
        return session['username']


def set_username(username="guest"):
    session['username'] = username


def get_dset(name_to_find, username=None):
    name_to_find = urllib.unquote(name_to_find)
    if username is None:
        username = get_username()
    try:
        dset = Dataset.objects.get(name=name_to_find, user=username)
    except Dataset.DoesNotExist:
        dset = Dataset.objects.get_or_404(name=name_to_find, user="guest")
    return dset
