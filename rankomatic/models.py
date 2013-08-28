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
User: Self-explanatory. A user of the website.
"""
#TODO make sure documentation is up to date.

import hashlib
import os
import gridfs
import tempfile
import pygraphviz as pgv
from rankomatic import db
from ot.poot import PoOT


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


class Dataset(db.EmbeddedDocument):
    """Represents a user's tableaux or dataset. Consists of a list of constraint
    names and a list of Candidates.

    """
    name = db.StringField(max_length=255, required=True)
    constraints = db.ListField(
        db.StringField(max_length=255, required=True),
        default=lambda: ["" for x in range(3)]
    )
    candidates = db.ListField(
        db.EmbeddedDocumentField(Candidate),
        default=lambda: [Candidate(csrf_enabled=False)]
    )
    grammars = db.ListField(  # list of grammars
        db.ListField(  # list of ordered pairs
            db.ListField(db.StringField())  # ordered pairs
        ),
        default=lambda: []
    )

    def process_form_data(self, data):
        """Convert raw form data into a useful form"""
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
        """From ranking library form, set the corresponding fields"""
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

    def calculate_compatible_grammars(self, classical=True):
        """Calculate the compatible grammars for the dataset.

        If any are found, put them in the grammars list.

        """
        mongo_db = db.get_pymongo_db()
        poot = PoOT(lat_dir=None, mongo_db=mongo_db)
        poot.dset = self._candidates
        grammars = poot.get_grammars(classical=classical)
        if grammars:
            converted = []
            for g in grammars:
                new_gram = []
                for rel in g:
                    new_gram.append([self.constraints[rel[0]-1],
                                     self.constraints[rel[1]-1]])
                converted.append(new_gram)
            self.grammars = converted
        else:
            self.grammars = []

    def visualize_and_store_grammars(self):
        """Generate visualization images and store them in GridFS"""
        fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
        for i, gram in enumerate(self.grammars):
            graph = self.make_graph(gram)
            with tempfile.TemporaryFile() as tf:
                graph.draw(tf, format='svg')
                tf.seek(0)
                filename = 'grammar%d.svg' % i
                path = "".join([self.name, '/', filename])
                fs.put(tf, filename=path)

    def make_graph(self, grammar):
        """Create an AGraph version of the given grammar."""
        graph = pgv.AGraph(directed=True)
        for c in self.constraints:
            graph.add_node(c)
        for rel in grammar:
            graph.add_edge(rel[1], rel[0])
        graph.tred()
        graph.layout('dot')
        return graph




class User(db.DynamicDocument):
    """A user of the application, has a name, salted password digest, salt, and a
    list of Datasets belonging to the user.

    """
    username = db.StringField(required=True, max_length=255)
    password_digest = db.StringField(required=True)
    salt = db.StringField(required=True)
    datasets = db.ListField(db.EmbeddedDocumentField(Dataset), default=lambda: [])

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
