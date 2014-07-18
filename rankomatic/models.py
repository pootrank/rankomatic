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
# TODO make sure documentation is up to date.

import hashlib
import os
import gridfs
import datetime
import tempfile
import urllib
from collections import OrderedDict

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


class Dataset(db.Document):
    """Represents a user's tableaux or dataset. Consists of a list of
    constraint names and a list of Candidates. Also exports methods for
    interacting with dataset, including wrappers for several functions
    from the ot library.

    """
    upload_date = db.DateTimeField(default=datetime.datetime.utcnow())
    name = db.StringField(max_length=255, required=True)
    constraints = db.ListField(
        db.StringField(max_length=255, required=True),
        default=lambda: ["" for x in range(3)]
    )
    _grammars = db.StringField()
    candidates = db.ListField(db.EmbeddedDocumentField(Candidate))
    entailments = db.DictField()
    entailments_calculated = db.BooleanField(default=False)
    entailments_visualized = db.BooleanField(default=False)
    grammars = db.ListField(  # list of grammars
        db.ListField(  # list of ordered pairs
            db.ListField(db.StringField())  # ordered pairs
        ),
        default=lambda: []
    )
    user = db.StringField(default="guest")

    @property
    def raw_grammars(self):
        if self._grammars is None:
            self.calculate_compatible_grammars(False)
        elif not self.grammars:
            self.grammars = self._get_pretty_grammars()
            self.save()
        return eval(self._grammars)

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
        processed = self._initialize_ot_data_from(form_data)
        for ig in form_data['input_groups']:
            for cand in ig['candidates']:
                processed['candidates'].append(self._process_candidate(cand))
        return processed

    def _initialize_ot_data_from(self, form_data):
        return {
            'name': form_data['name'],
            'constraints': form_data['constraints'],
            'candidates': []}

    def _process_candidate(self, form_cand):
        return {
            'output': form_cand['outp'],
            'input': form_cand['inp'],
            'optimal': form_cand['optimal'],
            'vvector': self._make_violation_vector_dict(form_cand['vvector'])}

    def _make_violation_vector_dict(self, list_vvect):
        return dict((i+1, v) for i, v in enumerate(list_vvect))

    def create_form_data(self):
        """Create a dict which contains the dataset as used by the forms."""
        form_data = self._initialize_form_data()
        inputs = self._get_all_inputs_from_candidates()

        for inp in inputs:
            input_group = self._create_input_group_for(inp)
            form_data['input_groups'].append(input_group)

        return form_data

    def _initialize_form_data(self):
        return {
            'name': self.name,
            'constraints': self.constraints,
            'input_groups': []}

    def _get_all_inputs_from_candidates(self):
        inputs = [cand.input for cand in self.candidates]
        unique_inputs = list(OrderedDict.fromkeys(inputs))
        return unique_inputs

    def _create_input_group_for(self, inp):
        input_group = {'candidates': []}
        for cand in self.candidates:
            if cand.input == inp:
                input_group['candidates'].append(self._make_cand_dict(cand))
        return input_group

    def _make_cand_dict(self, old_cand):
        return {'inp': old_cand.input,
                'outp': old_cand.output,
                'optimal': old_cand.optimal,
                'vvector': old_cand.vvector}

    def set_dset(self, data):
        """From ot library form, set the corresponding fields"""
        self.name = data['name']
        self._ot_candidates = data['candidates']
        self.constraints = data['constraints']
        self.candidates = [Candidate(cand) for cand in data['candidates']]

    def create_ot_compatible_candidates(self):
        return [{
                'input': c.input,
                'output': c.output,
                'optimal': c.optimal,
                'vvector': self._make_violation_vector_dict(c.vvector)
                } for c in self.candidates]

    def build_poot(self):
        """Builds the PoOT object and attaches it to self.poot.

        Relies on self._ot_candidates for the ot-compatible candidates

        """
        mongo_db = db.get_pymongo_db()
        poot = OTStats(lat_dir=None, mongo_db=mongo_db)
        if self._ot_candidates is not None:
            poot.dset = self._ot_candidates
        return poot

    def grammar_to_string(self, g):
        """Convert an ugly grammar into a pretty set-like string"""
        if g:
            l = ['{']
            for rel in g[:-1]:
                l.extend(['(', self.double_to_string(rel), '), '])
            l.extend(['(', self.double_to_string(g[-1]), ')}'])
        else:
            l = ['{', ' }']
        return "".join(l)

    def double_to_string(self, d):
        l = [d[0], ', ', d[1]]
        return "".join(l)

    def calculate_global_entailments(self):
        if not self.entailments_calculated:
            entailments = self.poot.get_entailments(atomic=True)
            if entailments:
                self.entailments = self._process_entailments(entailments)
            else:
                self.entailments = {}

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
        if not self.entailments_visualized:
            fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
            filename = "".join([self.name, "/", 'entailments.svg'])
            try:
                fs.get_last_version(filename=filename)
            except gridfs.NoFile:
                graph = self.make_entailment_graph()
                self._write_graph_to_gridfs(graph, fs, filename)
            self.entailments_visualized = True
            self.save()

    def _write_graph_to_gridfs(self, graph, fs, filename):
        with tempfile.TemporaryFile() as tf:
            graph.draw(tf, format='svg')
            tf.seek(0)
            fs.put(tf, filename=filename)

    def make_entailment_graph(self):
        graph = pygraphviz.AGraph(directed=True)
        for k, v in self.entailments.iteritems():
            for entailed in v:
                graph.add_edge(k, entailed)
        graph.tred()
        graph.layout('dot')
        return graph

    def calculate_compatible_grammars(self, classical=True):
        """Calculate the compatible grammars for the dataset.

        If any are found, put them in the grammars list.

        """
        grammars = sorted(list(self.poot.get_grammars(classical=classical)),
                          key=len)
        self._grammars = str(grammars)
        self.grammars = self._convert_to_pretty_grammars(grammars)

    def _get_pretty_grammars(self):
        grams = eval(self._grammars)
        return self._convert_to_pretty_grammars(grams)

    def _convert_to_pretty_grammars(self, grammars):
        converted = []
        for g in grammars:
            new_gram = []
            for rel in g:
                new_gram.append([self.constraints[rel[1]-1],
                                 self.constraints[rel[0]-1]])
            converted.append(new_gram)
        return converted

    def visualize_and_store_grammars(self, inds):
        """Generate visualization images and store them in GridFS"""
        if inds:
            fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
            encode_name = urllib.quote(self.name)
            fname = "".join([encode_name, '/', ('grammar%d.svg' % inds[0])])
            try:
                fs.get_last_version(filename=fname)
            except gridfs.NoFile:
                for i in inds:
                    graph = self.make_grammar_graph(self.grammars[i])
                    with tempfile.TemporaryFile() as tf:
                        graph.draw(tf, format='svg')
                        tf.seek(0)
                        filename = 'grammar%d.svg' % i
                        path = "".join([encode_name, '/', filename])
                        fs.put(tf, filename=path)

    def make_grammar_graph(self, grammar):
        """Create an AGraph version of the given grammar."""
        graph = pygraphviz.AGraph(directed=True, rankdir="LR")
        for c in self.constraints:
            graph.add_node(c)
        for rel in grammar:
            graph.add_edge(rel[0], rel[1])
        graph.tred()
        graph.layout('dot')
        return graph

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
