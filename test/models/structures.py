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
    'rasia': [{'output': 'ra.si.a', 'num_cot': 8, 'per_cot': 100.0},
              {'output': 'ra.sii', 'num_cot': 0, 'per_cot': 0.0}],
    'lasi-a': [{'output': 'la.si.a', 'num_cot': 5, 'per_cot': 62.5},
               {'output': 'la.sii', 'num_cot': 3, 'per_cot': 37.5}],
    'idea': [{'output': 'i.de.a', 'num_cot': 8, 'per_cot': 100.0},
             {'output': 'i.dee', 'num_cot': 0, 'per_cot': 0.0}],
    'ovea': [{'output': 'o.ve.a', 'num_cot': 4, 'per_cot': 50.0},
             {'output': 'o.vee', 'num_cot': 4, 'per_cot': 50.0}]
}
global_entailments = {
    'idea, i.dee': ['idea, i.dee', 'ovea, o.vee'],
    'idea, i.de.a': ['idea, i.de.a', 'rasia, ra.si.a'],
    'lasi-a, la.si.a': ['lasi-a, la.si.a', 'rasia, ra.si.a'],
    'lasi-a, la.sii': ['lasi-a, la.sii', 'ovea, o.vee'],
    'ovea, o.vee': ['ovea, o.vee'],
    'ovea, o.ve.a': ['idea, i.de.a', 'lasi-a, la.si.a',
                     'ovea, o.ve.a', 'rasia, ra.si.a'],
    'rasia, ra.si.a': ['rasia, ra.si.a'],
    'rasia, ra.sii': ['idea, i.dee', 'lasi-a, la.sii',
                      'ovea, o.vee', 'rasia, ra.sii']
}

to_flatten = {
    'a': [{'1': 'bad', '2': 'worse'}],
    'b': ['oh no!', [["that didn't work"], ["that also didn't work"]]]
}

flattened = ["bad", "worse", "oh no!",
             "that didn't work", "that also didn't work"]
