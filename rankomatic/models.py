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
#TODO make sure documentation is up to date.

import hashlib
import os
import gridfs
import datetime
import tempfile
import pygraphviz as pgv
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
    grammars = db.ListField(  # list of grammars
        db.ListField(  # list of ordered pairs
            db.ListField(db.StringField())  # ordered pairs
        ),
        default=lambda: []
    )

    @property
    def raw_grammars(self):
        if self._grammars is None:
            self.calculate_compatible_grammars(False)
        return eval(self._grammars)

    def __init__(self, data=None, data_is_from_form=True, *args, **kwargs):
        super(Dataset, self).__init__(*args, **kwargs)
        self._candidates = None
        if data is not None:
            if data_is_from_form:
                self.process_form_data(data)
            self.set_dset(data)
        if self.candidates and self._candidates is None:
            self._candidates = self.create_raw_candidates()
        self.build_poot()

    def process_form_data(self, data):
        """Convert raw form data into the stuff used by the ot library."""
        self.constraints = data['constraints']
        data['candidates'] = []
        for ig in data['input_groups']:
            for c in ig['candidates']:
                c['output'] = c.pop('outp')
                c['input'] = c.pop('inp')
                vvec_dict = {}
                for i in range(len(c['vvector'])):
                    vvec_dict[i + 1] = c['vvector'][i]
                c['vvector'] = vvec_dict
                data['candidates'].append(c)
        data.pop('input_groups')

    def set_dset(self, data):
        """From ot library form, set the corresponding fields"""
        self._candidates = data['candidates']
        self.constraints = data['constraints']
        self.candidates = []
        for cand_dict in data['candidates']:
            cand = Candidate()
            cand.input = cand_dict['input']
            cand.output = cand_dict['output']
            cand.optimal = cand_dict['optimal']
            vvec = cand_dict['vvector']
            cand.vvector = [vvec[k] for k in sorted(vvec.keys())]
            self.candidates.append(cand)

    def create_raw_candidates(self):
        """Get raw candidates from mongo form, store on object"""
        ret = []
        for c in self.candidates:
            vvec_dict = dict((i+1, v) for i, v in enumerate(c.vvector))
            c_dict = {'input': c.input,
                      'output': c.output,
                      'optimal': c.optimal,
                      'vvector': vvec_dict}
            ret.append(c_dict)
        return ret

    def build_poot(self):
        mongo_db = db.get_pymongo_db()
        self.poot = OTStats(lat_dir=None, mongo_db=mongo_db)
        if self._candidates is not None:
            self.poot.dset = self._candidates

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
        ents = self.poot.get_entailments(atomic=True)
        if ents:
            con = {}
            for k in ents:
                new_key = self.double_to_string(tuple(k)[0])
                ent = ents[k]['up']
                con[new_key] = [self.double_to_string(tuple(e)[0]) for e in ent]
            self.entailments = con
        else:
            self.entailments = {}

    def visualize_and_store_entailments(self):
        if self.entailments:
            fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
            filename = "".join([self.name, "/", 'entailments.svg'])
            try:
                fs.get_last_version(filename=filename)
            except gridfs.NoFile:
                graph = self.make_entailment_graph()
                with tempfile.TemporaryFile() as tf:
                    graph.draw(tf, format='svg')
                    tf.seek(0)
                    fs.put(tf, filename=filename)

    def make_entailment_graph(self):
        graph = pgv.AGraph(directed=True)
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
        grammars = sorted(list(self.poot.get_grammars(classical=classical)), key=len)
        self._grammars = str(grammars)
        if grammars:
            converted = []
            for g in grammars:
                new_gram = []
                for rel in g:
                    new_gram.append([self.constraints[rel[1]-1],
                                     self.constraints[rel[0]-1]])
                converted.append(new_gram)
            self.grammars = converted
        else:
            self.grammars = []

    def visualize_and_store_grammars(self, inds):
        """Generate visualization images and store them in GridFS"""
        if inds:
            fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
            fname = "".join([self.name, '/', ('grammar%d.svg' % inds[0])])
            try:
                fs.get_last_version(filename=fname)
            except gridfs.NoFile:
                for i in inds:
                    graph = self.make_grammar_graph(self.grammars[i])
                    with tempfile.TemporaryFile() as tf:
                        graph.draw(tf, format='svg')
                        tf.seek(0)
                        filename = 'grammar%d.svg' % i
                        path = "".join([self.name, '/', filename])
                        fs.put(tf, filename=path)

    def make_grammar_graph(self, grammar):
        """Create an AGraph version of the given grammar."""
        graph = pgv.AGraph(directed=True, rankdir="LR")
        for c in self.constraints:
            graph.add_node(c)
        for rel in grammar:
            graph.add_edge(rel[0], rel[1])
        graph.tred()
        graph.layout('dot')
        return graph

    def get_cots_by_cand(self, grammar):
        cots_by_cand = self.poot.num_cots_by_cand(grammar=grammar)
        total_cots = self.poot.num_total_cots(grammar=grammar)
        ret = {}
        cands = sorted(cots_by_cand.keys())
        inputs = list(set([cand[0] for cand in cands]))
        for inp in inputs:
            ret[inp] = []
            for cand in cands:
                if cand[0] == inp:
                    num_cots = cots_by_cand[cand]
                    d = {'output': cand[1],
                         'num_cot': num_cots,
                         'per_cot': ((float(num_cots) / total_cots) * 100)}
                    ret[inp].append(d)
        return ret


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
