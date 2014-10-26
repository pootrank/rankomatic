#! /usr/bin/env python
from ..models import Dataset

guest_dset_names = ["Kiparsky", "CV Syllabification"]

def remove_temp_datasets():
    guest_dsets = Dataset.objects(user='guest')
    for dset in guest_dsets:
        if dset.name not in guest_dset_names:
            dset.remove_old_files()
            dset.delete()

if __name__ == "__main__":
    remove_temp_datasets()
