import pygraphviz
import gridfs
import urllib
import tempfile

from collections import defaultdict
from rankomatic import db


class GridFSGraph(pygraphviz.AGraph):

    FILETYPE = 'png'
    FS_COLL = 'tmp'

    def __init__(self, dset_name=None, basename=None, *args, **kwargs):
        super(GridFSGraph, self).__init__(encoding='UTF-8', *args, **kwargs)
        self._check_args(dset_name=dset_name, basename=basename)
        self.dset_name = dset_name
        self.basename = basename
        self.filename = self._make_filename()
        self.fs = gridfs.GridFS(db.get_pymongo_db(), collection=self.FS_COLL)

    def _check_args(self, **kwargs):
        for keyword in kwargs:
            self._check_arg(keyword, kwargs[keyword])

    def _check_arg(self, keyword, value):
        msg = "GridFSGraph.__init__ expects %s to be a non-empty string"
        if not value or type(value) not in [str, unicode]:
            raise TypeError(msg % keyword)

    def visualize(self):
        if not self.is_visualized():
            self.make_graph()
            self.store_graph()

    def store_graph(self):
        with tempfile.TemporaryFile() as tf:
            self.draw(tf, format=GridFSGraph.FILETYPE)
            tf.seek(0)  # reset file object to beginnning
            self.fs.put(tf, filename=self.filename)

    def is_visualized(self):
        try:
            self.fs.get_last_version(filename=self.filename)
        except gridfs.NoFile:
            return False
        else:
            return True

    def _make_filename(self):
        encode_name = urllib.quote(self.dset_name)
        return "".join([
            encode_name, '/', self.basename, '.', GridFSGraph.FILETYPE
        ])

    def make_graph(self):
        raise NotImplementedError("Define this in subclass")


class EntailmentGraph(GridFSGraph):

    def __init__(self, entailments, dset_name, num_cots_by_cand):
        super(EntailmentGraph, self).__init__(dset_name=dset_name,
                                              basename='entailments',
                                              directed=True)
        self.entailments = entailments
        self.num_cots_by_cand = num_cots_by_cand

    def make_graph(self):
        self._add_edges()
        self._collapse_cycles()
        self.node_attr['shape'] = 'rect'
        self._add_annotations()
        self.tred()
        self.layout('dot')

    def _add_annotations(self):
        for k, v in self.num_cots_by_cand.iteritems():
            if k in self.nodes():
                self.get_node(k).attr['label'] = k + self._rank_volume_annotation(v)

    def _rank_volume_annotation(self, value):
        return '<<FONT POINT-SIZE="10">RV: {}</FONT>>'.format(value)

    def _add_edges(self):
        for k, v in self.entailments.iteritems():
            [self.add_edge(k, entailed) for entailed in v]

    def _collapse_cycles(self):
        self._get_equivalent_nodes()
        self._get_cycles_from_equivalent_nodes()
        self._remove_cycles_from_graph()

    def _get_equivalent_nodes(self):
        self.equivalent_nodes = defaultdict(lambda: set([]))
        self._edges = set(self.edges())  # for determining membership later
        [self._add_equiv_nodes(e) for e in self._edges if self._nodes_equiv(e)]

    def _add_equiv_nodes(self, edge):
        self.equivalent_nodes[edge[0]].add(edge[1])
        self.equivalent_nodes[edge[1]].add(edge[0])

    def _nodes_equiv(self, edge):
        reverse_edge = (edge[1], edge[0])
        return reverse_edge in self._edges

    def _get_cycles_from_equivalent_nodes(self):
        cycles = [frozenset(v) for k, v in self.equivalent_nodes.iteritems()]
        self.cycles = set(cycles)

    def _remove_cycles_from_graph(self):
        for cycle in self.cycles:  # collapse the cycles
            self._collapse_single_cycle(cycle)

        for cycle in self.cycles:  # re-iterate in case cycles are connected
            self.delete_nodes_from(cycle)

    def _collapse_single_cycle(self, cycle):
        # make the label for the collapsed node and put it in the graph
        cycle = list(cycle)
        node_label = self._make_node_label(cycle)
        self._add_edges_to_and_from_collapsed_cycle(cycle, node_label)
        self.get_node(node_label).attr['label'] = node_label

    def _make_node_label(self, cycle):
        chunks = list(self._chunks(cycle))
        label = ''.join([self._pretty_chunk_string(chunk) for chunk in chunks])[:-5]
        ann = self.num_cots_by_cand[cycle[0]]
        return '<<FONT POINT-SIZE="14">{}</FONT><BR/><FONT POINT-SIZE="10"><B>RV: {}</B></FONT>>'.format(label, ann)

    def _chunks(self, to_chunk, chunk_size=1):
        for i in xrange(0, len(to_chunk), chunk_size):
            yield to_chunk[i:i+chunk_size]

    def _pretty_chunk_string(self, chunk):
        return "(" + "), (".join(chunk) + ")<BR/>"  # html-like label

    def _add_edges_to_and_from_collapsed_cycle(self, cycle, node_label):
        for edge in self.edges():
            if edge[0] in cycle:
                self.add_edge(node_label, edge[1])
            if edge[1] in cycle:
                self.add_edge(edge[0], node_label)

    def _make_nodes_rectangular(self):
        for node in self.nodes():
            node.attr['shape'] = 'rect'


class GrammarGraph(GridFSGraph):

    def __init__(self, grammar, dset_name, index):
        super(GrammarGraph, self).__init__(dset_name=dset_name,
                                           basename=("grammar%d" % index),
                                           directed=True, rankdir="LR")
        self.grammar = grammar

    def make_graph(self):
        for rel in self.grammar:
            self.add_edge(rel[0], rel[1])
        self.tred()
        self.layout('dot')
