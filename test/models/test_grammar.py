import mock
from rankomatic.models import Dataset
from rankomatic.models.grammar import Grammar


grammars = [
    frozenset([]),
    frozenset([(1, 2), (1, 3), (2, 3)]),
    frozenset([(1, 2), (2, 3), (1, 3), (1, 4)]),
    frozenset([(4, 3)])
]

list_grammars = [
    [],
    [[u'ONSET', u'*COMPLEX'], [u'ALIGN-L-WORD', u'*COMPLEX'],
        [u'ALIGN-L-WORD', u'ONSET']],
    [[u'ONSET', u'*COMPLEX'], [u'ALIGN-L-WORD', u'*COMPLEX'],
        [u'ALIGN-L-WORD', u'ONSET'], [u'ALIGN-R-PHRASE', u'*COMPLEX']],
    [[u'ALIGN-L-WORD', u'ALIGN-R-PHRASE']]
]

g_strings = [
    '{ }',
    '{(ONSET, *COMPLEX), (ALIGN-L-WORD, *COMPLEX), (ALIGN-L-WORD, ONSET)}',
    ('{(ONSET, *COMPLEX), (ALIGN-L-WORD, *COMPLEX), '
        '(ALIGN-L-WORD, ONSET), (ALIGN-R-PHRASE, *COMPLEX)}'),
    '{(ALIGN-L-WORD, ALIGN-R-PHRASE)}'
]


def test_empty_grammar_constructor():
    d = Dataset.objects.get(name="Kiparsky")
    g = Grammar(frozenset(), d)
    assert g.raw_grammar is frozenset()
    assert g.list_grammar == []
    assert g.string == "{ }"


def test_frozenset_constructor():
    for i in range(4):
        yield check_frozenset_constructor, i
        yield check_visualize, i


def check_frozenset_constructor(i):
    dset = Dataset.objects.get(name="Kiparsky")
    gram = grammars[i]
    g = Grammar(gram, dset)

    assert g.raw_grammar == gram
    assert g.list_grammar == list_grammars[i]
    assert g.string == g_strings[i]


def test_list_constructor():
    for i in range(4):
        yield check_list_constructor, i
        yield check_visualize, i


def check_list_constructor(i):
    dset = Dataset.objects.get(name="Kiparsky")
    list_gram = list_grammars[i]
    g = Grammar(dataset=dset, list_gram=list_gram)

    assert g.raw_grammar == grammars[i]
    assert g.list_grammar == list_gram
    assert g.string == g_strings[i]


@mock.patch('rankomatic.models.graphs.GridFSGraph.visualize')
def check_visualize(i, mock_visualize):
    dset = Dataset.objects.get(name="Kiparsky")
    gram = Grammar(grammars[i], dset)
    gram.visualize("Kiparsky", i)
    assert mock_visualize.called


def test_raw_grammar_from_db():
    dset = Dataset.objects.get(name="Kiparsky")
    gram = dset.grammars[-1]
    assert gram.raw_grammar == frozenset([(3, 1)])
