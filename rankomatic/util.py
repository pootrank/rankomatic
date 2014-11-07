import urllib
import json
from flask import session, request

from rankomatic.models import Dataset


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


def get_url_args():
    classical = json.loads(request.args.get('classical').lower())
    page = int(request.args.get('page'))
    sort_by = request.args.get('sort_by')
    return (classical, page, sort_by)
