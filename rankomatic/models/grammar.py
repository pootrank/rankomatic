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
            self._raw_grammar = frozenset_gram
            self._make_list_grammar(dataset)
            self._make_string(dataset)

    @property
    def raw_grammar(self):
        try:
            return self._raw_grammar
        except AttributeError:
            self._raw_grammar = eval(self._raw_grammar_str.grammar)
        return self._raw_grammar

    def _make_list_grammar(self, dataset):
        self.list_grammar = [
            [dataset.constraints[rel[1] - 1], dataset.constraints[rel[0] - 1]]
            for rel in self.raw_grammar
        ]

    def _make_string(self, dataset):
        if self.list_grammar:
            to_join = ['{']
            for rel in self.list_grammar[:-1]:
                to_join.extend(['(', pair_to_string(rel), '), '])
            to_join.extend(['(',
                            pair_to_string(self.list_grammar[-1]),
                            ')}'])
        else:
            to_join = ['{', ' }']
        self.string = "".join(to_join)

    def visualize(self, dset_name, index):
        """Create an AGraph version of the given grammar."""
        graph = GrammarGraph(self.list_grammar, dset_name, index)
        graph.visualize()
