import datetime
import gridfs
import urllib

from candidate import Candidate
from grammar import Grammar
from rankomatic import db
from ot.poot import OTStats
from util import DatasetConverter, pair_to_string
from graphs import EntailmentGraph


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
            self.remove_old_files()
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
        return pair_to_string(tuple(fset)[0])

    def visualize_and_store_entailments(self):
        graph = EntailmentGraph(self.entailments, self.name)
        graph.visualize()
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
