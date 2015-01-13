#! /usr/bin/env python
from rankomatic.models import Dataset

DB_STR = 'otorder_test'

def delete_bad_dsets():
    bad_dsets = filter(is_bad_dset, Dataset.objects())
    for bad in bad_dsets:
        bad.delete()


def is_bad_dset(dset):
    permanenent_names = ['Kiparsky', 'CV Syllabification']
    return dset.user != 'guest' or dset.name not in permanenent_names


if __name__ == '__main__':
    actual_db_str = str(Dataset._get_db())
    if DB_STR in actual_db_str:
        delete_bad_dsets()
    else:
        print "Wrong database: %s" % actual_db_str
