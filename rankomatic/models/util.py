import pygraphviz
import gridfs
import urllib
import tempfile

from collections import OrderedDict, defaultdict
from rankomatic import db


class DatasetConverter():

    @classmethod
    def form_data_to_ot_data(cls, form_data):
        processed = cls._initialize_ot_data_from(form_data)
        for ig in form_data['input_groups']:
            for cand in ig['candidates']:
                processed['candidates'].append(cls._process_candidate(cand))
        return processed

    @classmethod
    def _initialize_ot_data_from(cls, form_data):
        return {
            'name': form_data['name'],
            'constraints': form_data['constraints'],
            'candidates': []}

    @classmethod
    def _process_candidate(cls, form_cand):
        return {
            'output': form_cand['outp'],
            'input': form_cand['inp'],
            'optimal': form_cand['optimal'],
            'vvector': cls._make_violation_vector_dict(form_cand['vvector'])}

    @classmethod
    def _make_violation_vector_dict(cls, list_vvect):
        return dict((i+1, v) for i, v in enumerate(list_vvect))

    @classmethod
    def db_dataset_to_form_data(cls, dset):
        form_data = cls._initialize_form_data(dset)
        inputs = cls._get_all_inputs_from_candidates(dset)
        for inp in inputs:
            input_group = cls._create_input_group_for(inp, dset)
            form_data['input_groups'].append(input_group)
        return form_data

    @classmethod
    def _initialize_form_data(cls, dset):
        return {
            'name': dset.name,
            'constraints': dset.constraints,
            'input_groups': []
        }

    @classmethod
    def _get_all_inputs_from_candidates(cls, dset):
        inputs = [cand.input for cand in dset.candidates]
        unique_inputs = list(OrderedDict.fromkeys(inputs))
        return unique_inputs

    @classmethod
    def _create_input_group_for(cls, inp, dset):
        input_group = {'candidates': []}
        for cand in dset.candidates:
            if cand.input == inp:
                input_group['candidates'].append(cls._make_cand_dict(cand))
        return input_group

    @classmethod
    def _make_cand_dict(self, old_cand):
        return {
            'inp': old_cand.input,
            'outp': old_cand.output,
            'optimal': old_cand.optimal,
            'vvector': old_cand.vvector
        }

    @classmethod
    def create_ot_compatible_candidates(cls, dset):
        return [{
                'input': c.input,
                'output': c.output,
                'optimal': c.optimal,
                'vvector': cls._make_violation_vector_dict(c.vvector)
                } for c in dset.candidates]


class EntailmentGraph(pygraphviz.AGraph):

    def __init__(self, entailments, dset_name):
        super(EntailmentGraph, self).__init__(directed=True)
        self.entailments = entailments
        self.dset_name = dset_name
        self.fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
        self._make_filename()
        if self._is_not_visualized():
            self._make_entailment_graph()

    def _make_filename(self):
        self.filename = "".join([urllib.quote(self.dset_name), "/",
                                 "entailments.png"])

    def _is_not_visualized(self):
        try:
            self.fs.get_last_version(filename=self.filename)
        except gridfs.NoFile:
            return True
        else:
            return False

    def _make_entailment_graph(self):
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

    def visualize_to_gridfs(self):
        if self._is_not_visualized():
            with tempfile.TemporaryFile() as tf:
                self.draw(tf, format='png')
                tf.seek(0)
                self.fs.put(tf, filename=self.filename)
