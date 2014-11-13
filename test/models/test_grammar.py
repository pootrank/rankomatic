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


def test_grammar_constructor():
    for i in range(4):
        yield check_grammar_constructor, i
        yield check_visualize, i


def check_grammar_constructor(i):
    d = Dataset.objects.get(name="Kiparsky")
    gram = grammars[i]
    g = Grammar(gram, d)

    assert g.raw_grammar == gram
    assert g.list_grammar == list_grammars[i]
    assert g.string == g_strings[i]


@mock.patch('rankomatic.models.graphs.GridFSGraph.visualize')
def check_visualize(i, mock_visualize):
    d = Dataset.objects.get(name="Kiparsky")
    gram = Grammar(grammars[i], d)
    gram.visualize("Kiparsky", i)
    assert mock_visualize.called


def test_raw_grammar_from_db():
    d = Dataset.objects.get(name="Kiparsky")
    gram = d.grammars[-1]
    assert gram.raw_grammar == frozenset([(3, 1)])
