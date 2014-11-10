from werkzeug import ImmutableMultiDict
from copy import deepcopy


compatible_poot_grammars = [
    [['c1', 'c3'], ['c1', 'c2']],
    [['c1', 'c3'], ['c4', 'c2']],
    [['c2', 'c3'], ['c1', 'c3'], ['c1', 'c2']],
    [['c1', 'c3'], ['c4', 'c2'], ['c1', 'c2']],
    [['c1', 'c3'], ['c1', 'c4'], ['c1', 'c2']],
    [['c1', 'c3'], ['c3', 'c2'], ['c1', 'c2']],
    [['c1', 'c3'], ['c3', 'c2'], ['c4', 'c2'], ['c1', 'c2']],
    [['c1', 'c4'], ['c1', 'c3'], ['c3', 'c2'], ['c1', 'c2']],
    [['c1', 'c3'], ['c1', 'c4'], ['c4', 'c2'], ['c1', 'c2']],
    [['c2', 'c3'], ['c1', 'c3'], ['c1', 'c4'], ['c1', 'c2']],
    [['c1', 'c4'], ['c1', 'c3'], ['c3', 'c2'], ['c4', 'c2'], ['c1', 'c2']]
]

cot_stats_by_cand = {
    'rasia': [{'output': 'ra-si-a', 'num_cot': 8, 'per_cot': 100.0},
              {'output': 'ra-sii', 'num_cot': 0, 'per_cot': 0.0}],
    'lasi-a': [{'output': 'la-si-a', 'num_cot': 5, 'per_cot': 62.5},
               {'output': 'la-sii', 'num_cot': 3, 'per_cot': 37.5}],
    'idea': [{'output': 'i-de-a', 'num_cot': 8, 'per_cot': 100.0},
             {'output': 'i-dee', 'num_cot': 0, 'per_cot': 0.0}],
    'ovea': [{'output': 'o-ve-a', 'num_cot': 4, 'per_cot': 50.0},
             {'output': 'o-vee', 'num_cot': 4, 'per_cot': 50.0}]
}
global_entailments = {
    'idea, i-dee': ['idea, i-dee', 'ovea, o-vee'],
    'idea, i-de-a': ['idea, i-de-a', 'rasia, ra-si-a'],
    'lasi-a, la-si-a': ['lasi-a, la-si-a', 'rasia, ra-si-a'],
    'lasi-a, la-sii': ['lasi-a, la-sii', 'ovea, o-vee'],
    'ovea, o-vee': ['ovea, o-vee'],
    'ovea, o-ve-a': ['idea, i-de-a', 'lasi-a, la-si-a',
                     'ovea, o-ve-a', 'rasia, ra-si-a'],
    'rasia, ra-si-a': ['rasia, ra-si-a'],
    'rasia, ra-sii': ['idea, i-dee', 'lasi-a, la-sii',
                      'ovea, o-vee', 'rasia, ra-sii']
}

to_flatten = {
    'a': [{'1': 'bad', '2': 'worse'}],
    'b': ['oh no!', [["that didn't work"], ["that also didn't work"]]],
    'c': ("a" for i in range(3))
}

flattened = ["bad", "worse", "oh no!",
             "that didn't work", "that also didn't work",
             'a', 'a', 'a']

base_form_data = {
    'constraints-0': u'a',
    'constraints-1': u'b',
    'constraints-2': u'c',
    'input_groups-0-candidates-0-inp': u'a',
    'input_groups-0-candidates-1-inp': u'a',
    'input_groups-0-candidates-2-inp': u'a',
    'input_groups-0-candidates-0-outp': u'b',
    'input_groups-0-candidates-1-outp': u'c',
    'input_groups-0-candidates-2-outp': u'd',
    'input_groups-0-candidates-0-optimal': u'true',
    'input_groups-0-candidates-0-vvector-0': u'',
    'input_groups-0-candidates-0-vvector-1': u'',
    'input_groups-0-candidates-0-vvector-2': u'',
    'input_groups-0-candidates-1-vvector-0': u'',
    'input_groups-0-candidates-1-vvector-1': u'',
    'input_groups-0-candidates-1-vvector-2': u'',
    'input_groups-0-candidates-2-vvector-0': u'',
    'input_groups-0-candidates-2-vvector-1': u'',
    'input_groups-0-candidates-2-vvector-2': u'',
    'name': u'blank',
    'submit_button': u'All grammars'
}


def change_one_value(key, value):
    ret = deepcopy(base_form_data)
    ret[key] = value
    return ImmutableMultiDict(ret)


valid_form_data = ImmutableMultiDict(base_form_data)

constraints_not_unique = change_one_value('constraints-1', 'a')
inputs_not_same = change_one_value('input_groups-0-candidates-0-inp', 'b')
outputs_not_unique = change_one_value('input_groups-0-candidates-1-outp', 'b')
special_chars = change_one_value('input_groups-0-candidates-0-inp', '$')

none_optimal = deepcopy(base_form_data)
none_optimal.pop('input_groups-0-candidates-0-optimal')
none_optimal = ImmutableMultiDict(none_optimal)


invalid_forms = [
    constraints_not_unique,
    inputs_not_same,
    outputs_not_unique,
    special_chars,
    none_optimal
]

grammar_info = [
    {
        'grammar': "{(C1, C2)}",
        'filename': "grammar0.png",
        'cots_by_cand': {
            'I1': [
                {
                    'output': 'O1',
                    'num_cots': 3,
                    'per_cot': 50.0
                },
                {
                    'output': 'O2',
                    'num_cots': 3,
                    'per_cot': 50.0
                }
            ]
        },
        'input_totals': {
            'I1': {
                'per_sum': 100.0,
                'raw_sum': 6
            }
        }
    },
    {
        'grammar': "{(C2, C3)}",
        'filename': "grammar1.png",
        'cots_by_cand': {
            'I1': [
                {
                    'output': 'O1',
                    'num_cots': 2,
                    'per_cot': 33.3
                },
                {
                    'output': 'O2',
                    'num_cots': 4,
                    'per_cot': 66.7
                }
            ]
        },
        'input_totals': {
            'I1': {
                'per_sum': 100.0,
                'raw_sum': 6
            }
        }
    }
]
