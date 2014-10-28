#! /usr/bin/env python
from rankomatic.models import Dataset


def delete_bad_dsets():
    bad_dsets = [d for d in Dataset.objects() if is_bad_dset(d)]
    for bad in bad_dsets:
        bad.delete()

def is_bad_dset(dset):
    permanenent_names = ['Kiparsky', 'CV Syllabification']
    return dset.user != 'guest' or dset.name not in permanenent_names


if __name__ == '__main__':
    desired_db_str = 'otorder_test'
    actual_db_str = str(Dataset._get_db())
    if desired_db_str in actual_db_str:
        delete_bad_dsets()
    else:
        print "Wrong database: %s" % actual_db_str
