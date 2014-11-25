from rankomatic import db
from util import pair_to_string
from graphs import GrammarGraph


class RawGrammar(db.Document):
    grammar = db.StringField(unique=True)
    meta = {'indexes': ['grammar']}


class Grammar(db.EmbeddedDocument):
    _raw_grammar_str = db.ReferenceField(RawGrammar, required=True)
    string = db.StringField(required=True)
    list_grammar = db.ListField(db.ListField(db.StringField()))
    stats = db.DictField()

    def __init__(self, frozenset_gram=None, dataset=None, *args, **kwargs):
        super(Grammar, self).__init__(*args, **kwargs)
        if frozenset_gram is not None and dataset is not None:
            frozenset_gram = frozenset(sorted(list(frozenset_gram)))
            self._raw_grammar_str = RawGrammar.objects.get(
                grammar=str(frozenset_gram)
            )
            self.dset = dataset
            self._raw_grammar = frozenset_gram
            self._make_list_grammar()
            self._make_string()

    @property
    def raw_grammar(self):
        try:
            return self._raw_grammar
        except AttributeError:
            self._raw_grammar = eval(self._raw_grammar_str.grammar)
        return self._raw_grammar

    def _make_list_grammar(self):
        self.list_grammar = [self._list_rel(rel) for rel in self.raw_grammar]

    def _list_rel(self, rel):
        return [  # swap order, -1 to change from 1 to 0 index
            self.dset.constraints[rel[1] - 1],
            self.dset.constraints[rel[0] - 1]
        ]

    def _make_string(self):
        to_join = ['{']
        inners = [self._inner_pair_str(rel) for rel in self.list_grammar[:-1]]
        inners.extend([self._final_pair_str()])
        to_join.extend(inners)
        self.string = "".join(to_join)

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
