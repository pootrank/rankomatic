"""
File: models.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines the models for use with the Optimality Theory constraint-ranking
website. They are implemented for MongoDB using MongoEngine. As of now the
models are User, Dataset, and Candidate.

Candidate: A single row from the Dataset, in OT terms an input-outuput pair.
           Also contains whether or not the output is optimal for the input
           and the violation vector for the constraint set of the Dataset.
Dataset: Represents a user's tableaux or dataset. Consists of a list of
          constraint names and a list of Candidates.
User: A user of the website.
"""

import hashlib
import os
import gridfs
import datetime
import tempfile
import urllib
from collections import OrderedDict, defaultdict

import pygraphviz

from rankomatic import db
from ot.poot import OTStats


class Candidate(db.EmbeddedDocument):
    """A single row from the Dataset, in OT terms an input-outuput pair.
    Also contains whether or not the output is optimal for the input
    and the violation vector for the constraint set of the Dataset.

    """
    input = db.StringField(max_length=255, default="")
    output = db.StringField(max_length=255, default="")
    optimal = db.BooleanField()
    vvector = db.ListField(
        db.IntField(),
        default=lambda: [0 for i in xrange(3)],
    )

    def __init__(self, data=None, *args, **kwargs):
        super(Candidate, self).__init__(*args, **kwargs)
        if data:
            self.input = data['input']
            self.output = data['output']
            self.optimal = data['optimal']
            vvec = data['vvector']
            self.vvector = [vvec[k] for k in sorted(vvec.keys())]


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


class Dataset(db.Document):
    """Represents a user's tableaux or dataset. Consists of a list of
    constraint names and a list of Candidates. Also exports methods for
    interacting with dataset, including wrappers for several functions
    from the ot library.

    """
    upload_date = db.DateTimeField(default=datetime.datetime.utcnow())
    name = db.StringField(max_length=255, required=True, unique_with='user')
    constraints = db.ListField(db.StringField(max_length=255, required=True),
                               default=lambda: ["" for x in range(3)])
    candidates = db.ListField(db.EmbeddedDocumentField(Candidate))
    entailments = db.DictField()
    classical = db.BooleanField(default=False)
    _sort_by = db.StringField(default="rank_volume")
    grammars = db.ListField(db.EmbeddedDocumentField(Grammar), default=None)
    user = db.StringField(default="guest")

    grammar_navbar = db.DictField()
    global_stats = db.DictField()
    global_stats_calculated = db.BooleanField(default=False)
    grammar_info = db.ListField(db.DictField())

    grammar_stats_calculated = db.BooleanField(default=False)
    entailments_calculated = db.BooleanField(default=False)
    entailments_visualized = db.BooleanField(default=False)

    @property
    def raw_grammars(self):
        if self.grammars is None:
            self.calculate_compatible_grammars()
        return [gram.raw_grammar for gram in self.grammars]

    @property
    def sort_by(self):
        return self._sort_by

    @sort_by.setter
    def sort_by(self, value):
        if value and self._sort_by != value:
            self.grammars = None
            self._sort_by = value

    def __init__(self, data=None, data_is_from_form=True, *args, **kwargs):
        super(Dataset, self).__init__(*args, **kwargs)

        # stores candidates in ot-compatible form
        self._ot_candidates = None

        if data is not None:
            if data_is_from_form:
                data = self.process_form_data(data)
            self.set_dset(data)

        # self.candidates is non-empty if retrieved from DB
        if self.candidates and self._ot_candidates is None:
            self._ot_candidates = self.create_ot_compatible_candidates()
        self.poot = self.build_poot()

    def process_form_data(self, form_data):
        """Convert raw form data into the stuff used by the ot library."""
        return DatasetConverter.form_data_to_ot_data(form_data)

    def create_form_data(self):
        """Create a dict which contains the dataset as used by the forms."""
        return DatasetConverter.db_dataset_to_form_data(self)

    def set_dset(self, data):
        """From ot library form, set the corresponding fields"""
        self.name = data['name']
        self._ot_candidates = data['candidates']
        self.constraints = data['constraints']
        self.candidates = [Candidate(cand) for cand in data['candidates']]

    def create_ot_compatible_candidates(self):
        return DatasetConverter.create_ot_compatible_candidates(self)

    def build_poot(self):
        """Builds the PoOT object and attaches it to self.poot.

        Relies on self._ot_candidates for the ot-compatible candidates

        """
        mongo_db = db.get_pymongo_db()
        poot = OTStats(lat_dir=None, mongo_db=mongo_db)
        if self._ot_candidates is not None:
            poot.dset = self._ot_candidates
        return poot

    def grammar_to_string(self, index):
        """Convert an ugly grammar into a pretty set-like string"""
        return self.grammars[index].string

    def double_to_string(self, d):
        l = [d[0], ', ', d[1]]
        return "".join(l)

    def calculate_global_entailments(self):
        if not self.entailments_calculated:
            print "recalculating entailments"
            entailments = self.poot.get_entailments(atomic=True)
            self.entailments = self._process_entailments(entailments)
            self.entailments_calculated = True
            self.save()

    def _process_entailments(self, entailments):
        processed = {}
        for old in entailments:
            new = self._frozenset_to_string(old)
            entailed = entailments[old]['up']
            processed[new] = sorted(
                [self._frozenset_to_string(e) for e in entailed])
        return processed

    def _frozenset_to_string(self, fset):
        return self.double_to_string(tuple(fset)[0])

    def visualize_and_store_entailments(self):
        graph = EntailmentGraph(self.entailments, self.name)
        graph.visualize_to_gridfs()
        self.entailments_visualized = True
        self.save()

    def calculate_compatible_grammars(self):
        """Calculate the compatible grammars for the dataset.

        If any are found, put them in the grammars list.

        """
        grammars = list(self.poot.get_grammars(classical=self.classical))
        grammars.sort(key=self.get_grammar_sorter())
        self.grammars = [Grammar(gram, self) for gram in grammars]

    def get_grammar_sorter(self):
        if self._sort_by == 'size':
            return len
        else:  # default is 'rank_volume':
            return self.get_rank_volume_sorter()

    def get_rank_volume_sorter(self):
        lattice = self.poot.lattice

        def rank_volume_sorter(grammar):
            return len(lattice[grammar]['max'])

        return rank_volume_sorter

    def visualize_and_store_grammars(self, inds):
        """Generate visualization images and store them in GridFS"""
        if inds:
            for i in inds:
                self.grammars[i].visualize(self.name, i)
        self.save()

    def remove_old_files(self):
        fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
        encode_name = urllib.quote(self.name)
        filenames = [f for f in fs.list() if encode_name in f]
        for filename in filenames:
            last_version = fs.get_last_version(filename)
            file_id = last_version._id
            fs.delete(file_id)

    def get_cot_stats_by_cand(self, grammar):
        """For each input, return a list of dicts with output and COT stats.

        Given a grammar, return a dict from each input to a list. In the list
        is a dict for each output for that input, which contains the numbers
        and percentages of COT grammars that make that candidate optimal.

        """
        self._initialize_stats_for_grammar(grammar)
        inputs = self._get_inputs_for_grammar()
        return {inp: self._make_input_cot_stats(inp) for inp in inputs}

    def _initialize_stats_for_grammar(self, grammar):
        self._cots_by_cand_for_grammar = self.poot.num_cots_by_cand(grammar)
        self._total_cots_for_grammar = self.poot.num_total_cots(grammar)
        self._cands_for_grammar = sorted(self._cots_by_cand_for_grammar.keys())

    def _get_inputs_for_grammar(self):
        unique_inputs = set([cand[0] for cand in self._cands_for_grammar])
        return sorted(list(unique_inputs))

    def _make_input_cot_stats(self, inp):
        input_cot_stats = []
        for cand in (c for c in self._cands_for_grammar if c[0] == inp):
            input_cot_stats.append(self._make_input_cot_stats_for_cand(cand))
        return input_cot_stats

    def _make_input_cot_stats_for_cand(self, cand):
        num_cots = self._cots_by_cand_for_grammar[cand]
        return {
            'output': cand[1],
            'num_cot': num_cots,
            'per_cot': self._get_percent_cots_for_grammar(num_cots)}

    def _get_percent_cots_for_grammar(self, num_cots):
        return ((float(num_cots) / self._total_cots_for_grammar) * 100)

    def num_compatible_poots(self):
        return len(self.raw_grammars)

    def num_total_poots(self):
        return self.poot.num_total_poots()

    def num_compatible_cots(self):
        length_of_cot = sum(range(len(self.constraints)))
        cots = [g for g in self.raw_grammars if len(g) == length_of_cot]
        return len(cots)

    def num_total_cots(self):
        return self.poot.num_total_cots()


class User(db.DynamicDocument):
    """A user of the application, has a name, salted password digest, salt, and a
    list of Datasets belonging to the user.

    """
    username = db.StringField(required=True, max_length=255)
    password_digest = db.StringField(required=True)
    salt = db.StringField(required=True)
    dset_names = db.ListField(db.StringField(), default=lambda: [])

    def set_password(self, password):
        """Adds a randomly generated salt to the User, then appends it to the
        password before hashing it, then saves the digest.

        """
        self.salt = os.urandom(64).encode('hex')
        h = hashlib.sha512()
        password += self.salt
        h.update(password)
        self.password_digest = h.hexdigest()

    def is_password_valid(self, guess):
        """Appends the user's salt to the guess before hashing it, then compares
        it with the stored password digest.

        """
        h = hashlib.sha512()
        guess += self.salt
        h.update(guess)
        return h.hexdigest() == self.password_digest
