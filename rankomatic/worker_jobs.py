from rankomatic import get_job_queue
from rankomatic.util import get_username, get_url_args
import json


def calculate_grammars_and_statistics(dset_name, sort_value):
    classical, page, sort_by = get_url_args()
    get_job_queue().put(json.dumps({
        'func': 'calculate_grammars_and_statistics',
        'args': (dset_name, sort_value, classical,
                 page, get_username(), sort_by)
    }))


def calculate_entailments(dset_name):
    get_job_queue().put(json.dumps({
        'func': 'calculate_entailments',
        'args': (dset_name, get_username())
    }))


def make_grammar_info(dset_name):
    get_job_queue().put(json.dumps({
        'func': 'make_grammar_info',
        'args': (dset_name, get_username())
    }))
