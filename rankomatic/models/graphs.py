import pygraphviz
import gridfs
import urllib
import tempfile

from collections import defaultdict
from rankomatic import db


class GridFSGraph(pygraphviz.AGraph):

    FILETYPE = 'png'

    def __init__(self, dset_name=None, basename=None, *args, **kwargs):
        super(GridFSGraph, self).__init__(*args, **kwargs)
        self._check_args(dset_name=dset_name, basename=basename)
        self.dset_name = dset_name
        self.basename = basename
        self.filename = self._make_filename()
        self.fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')

    def _check_args(self, **kwargs):
        for keyword in kwargs:
            self._check_arg(keyword, kwargs[keyword])

    def _check_arg(self, keyword, value):
        msg = "GridFSGraph.__init__ expects %s to be a non-empty string"
        if not value or type(value) is not str:
            raise TypeError(msg % keyword)

    def visualize(self):
        if not self.is_visualized():
            self.make_graph()
            self.store_graph()

    def store_graph(self):
        with tempfile.TemporaryFile() as tf:
            self.draw(tf, format=GridFSGraph.FILETYPE)
            tf.seek(0)
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
        return "".join([encode_name, '/', self.basename,
                        '.', GridFSGraph.FILETYPE])

    def make_graph(self):
        raise NotImplementedError("Define this in subclass")


class EntailmentGraph(GridFSGraph):

    def __init__(self, entailments, dset_name):
        super(EntailmentGraph, self).__init__(dset_name=dset_name,
                                              basename='entailments',
                                              directed=True)
        self.entailments = entailments

    def make_graph(self):
        self._add_edges()
        self._collapse_cycles()
        self._make_nodes_rectangular()
        self.tred()
        self.layout('dot')

    def _add_edges(self):
        for k, v in self.entailments.iteritems():
            for entailed in v:
                self.add_edge(k, entailed)

    def _collapse_cycles(self):
        self._get_equivalent_nodes()
        self._get_cycles_from_equivalent_nodes()
        self._remove_cycles_from_graph()

    def _get_equivalent_nodes(self):
        self.equivalent_nodes = defaultdict(lambda: set([]))
        edges = set(self.edges())  # for determining membership later
        for edge in edges:
            endpoints_are_same = edge[0] == edge[1]
            reverse_edge = (edge[1], edge[0])
            if reverse_edge in edges and not endpoints_are_same:
                self._add_equivalent_node_for_both_endpoints(edge)

    def _add_equivalent_node_for_both_endpoints(self, edge):
        self.equivalent_nodes[edge[0]].add(edge[1])
        self.equivalent_nodes[edge[1]].add(edge[0])

    def _get_cycles_from_equivalent_nodes(self):
        self.cycles = set([])
        for node, equivalent in self.equivalent_nodes.iteritems():
            equivalent.add(node)
            self.cycles.add(frozenset(equivalent))

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

    def _make_node_label(self, cycle):
        chunks = list(self._chunk_list(cycle))
        return ''.join([self._pretty_chunk_string(chunk) for chunk in chunks])

    def _chunk_list(self, to_chunk, size_of_chunks=1):
        for i in xrange(0, len(to_chunk), size_of_chunks):
            yield to_chunk[i:i+size_of_chunks]

    def _pretty_chunk_string(self, chunk):
        return "(" + "), (".join(chunk) + ")\n"

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
