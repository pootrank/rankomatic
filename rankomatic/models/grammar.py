import gridfs
import urllib
import pygraphviz
import tempfile

from rankomatic import db


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

    @property
    def fs(self):
        return gridfs.GridFS(db.get_pymongo_db(), collection='tmp')

    def _make_list_grammar(self, dataset):
        self.list_grammar = [
            [dataset.constraints[rel[1] - 1], dataset.constraints[rel[0] - 1]]
            for rel in self.raw_grammar
        ]

    def _make_string(self, dataset):
        if self.list_grammar:
            to_join = ['{']
            for rel in self.list_grammar[:-1]:
                to_join.extend(['(', self._pair_to_string(rel), '), '])
            to_join.extend(['(',
                            self._pair_to_string(self.list_grammar[-1]),
                            ')}'])
        else:
            to_join = ['{', ' }']
        self.string = "".join(to_join)

    def _pair_to_string(self, p):
        return "".join([p[0], ', ', p[1]])

    def visualize(self, dset_name, index):
        """Create an AGraph version of the given grammar."""
        self._initialize_visualization(dset_name, index)
        if not self._is_already_visualized(dset_name, index):
            self._make_graph()
            self._store_graph(dset_name, index)

    def _initialize_visualization(self, dset_name, index):
        self.dset_name = dset_name
        self.index = index
        self.filename = self._make_grammar_graph_filename()

    def _make_grammar_graph_filename(self):
        encode_name = urllib.quote(self.dset_name)
        return "".join([encode_name, '/', ('grammar%d.png' % self.index)])

    def _is_already_visualized(self, dset_name, index):
        try:
            self.fs.get_last_version(filename=self.filename)
        except gridfs.NoFile:
            return False
        else:
            return True

    def _make_graph(self):
        self.graph = pygraphviz.AGraph(directed=True, rankdir="LR")
        for rel in self.list_grammar:
            self.graph.add_edge(rel[0], rel[1])
        self.graph.tred()
        self.graph.layout('dot')

    def _store_graph(self, dset_name, index):
        with tempfile.TemporaryFile() as tf:
            self.graph.draw(tf, format='png')
            tf.seek(0)
            self.fs.put(tf, filename=self.filename)
