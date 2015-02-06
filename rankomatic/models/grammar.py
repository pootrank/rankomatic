from rankomatic import db
from util import pair_to_string
from graphs import GrammarGraph


class RawGrammar(db.Document):
    grammar = db.StringField(unique=True)
    meta = {'indexes': ['grammar']}


class Grammar(db.EmbeddedDocument):
    _raw_grammar_str = db.ReferenceField(RawGrammar, required=True)
    _dset = db.ReferenceField('Dataset')

    @property
    def dset(self):
        try:
            return self.dset_to_return
        except AttributeError:
            return self._dset

    @dset.setter
    def dset(self, value):
        if value.id is None:
            self.dset_to_return = value
        else:
            self._dset = value
            self.dset_to_return = self._dset

    def __init__(self, frozenset_gram=None, dataset=None,
                 list_gram=None, *args, **kwargs):
        super(Grammar, self).__init__(*args, **kwargs)
        if dataset is not None:  # None when coming from DB
            self.dset = dataset

        if list_gram is not None:
            self.list_grammar = list_gram
            frozenset_gram = self._make_frozenset_gram()

        if frozenset_gram is not None:
            frozenset_gram = frozenset(sorted(list(frozenset_gram)))

            self._raw_grammar_str = RawGrammar.objects.get(
                grammar=str(frozenset_gram)
            )
            self._raw_grammar = frozenset_gram

    def _make_frozenset_gram(self):
        return frozenset([self._tuple_rel(rel) for rel in self.list_grammar])

    def _tuple_rel(self, rel):
        return (  # swap order, get index + 1 to change from 0 to 1 index
            self.dset.constraints.index(rel[1]) + 1,
            self.dset.constraints.index(rel[0]) + 1
        )

    @property
    def raw_grammar(self):
        try:
            return self._raw_grammar
        except AttributeError:
            self._raw_grammar = eval(self._raw_grammar_str.grammar)
        return self._raw_grammar

    @property
    def string(self):
        try:
            return self._string
        except AttributeError:
            self._string = self._make_string()
        return self._string

    @property
    def list_grammar(self):
        try:
            return self._list_grammar
        except AttributeError:
            self._list_grammar = self._make_list_grammar()
        return self._list_grammar

    def _make_list_grammar(self):
        return [self._list_rel(rel) for rel in self.raw_grammar]

    def _list_rel(self, rel):
        return [  # swap order, -1 to change from 1 to 0 index
            self.dset.constraints[rel[1] - 1],
            self.dset.constraints[rel[0] - 1]
        ]

    @list_grammar.setter
    def list_grammar(self, value):
        self._list_grammar = value

    def _make_string(self):
        to_join = ['{']
        inners = [self._inner_pair_str(rel) for rel in self.list_grammar[:-1]]
        inners.extend([self._final_pair_str()])
        to_join.extend(inners)
        return "".join(to_join)

    def _inner_pair_str(self, rel):
        return '(' + pair_to_string(rel) + '), '

    def _final_pair_str(self):
        if self.list_grammar:
            return '(' + pair_to_string(self.list_grammar[-1]) + ')}'
        else:
            return ' }'

    def visualize(self, dset_name, index):
        """Create an AGraph version of the given grammar."""
        graph = GrammarGraph(self.list_grammar, dset_name, index)
        graph.visualize()


class GrammarList(db.Document):
    grammars = db.ListField(db.EmbeddedDocumentField(Grammar, default=None),
                            default=None)
