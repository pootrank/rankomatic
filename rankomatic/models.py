"""
File: models.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines the models for use with the Optimality Theory constraint-ranking
website. They are implemented for MongoDB using MongoEngine. As of now the
models are User, Tableaux, and Candidate.

Candidate: A single row from the Tableaux, in OT terms an input-outuput pair.
           Also contains whether or not the output is optimal for the input
           and the violation vector for the constraint set of the Tableaux.
Tableaux: Represents a user's tableaux or dataset. Consists of a list of
          constraint names and a list of Candidates.
User: Self-explanatory. A user of the website.
"""
#TODO make sure documentation is up to date.

from rankomatic import db
import hashlib
import os


class Candidate(db.DynamicEmbeddedDocument):
    """
    A single row from the Tableaux, in OT terms an input-outuput pair.
    Also contains whether or not the output is optimal for the input
    and the violation vector for the constraint set of the Tableaux.
    """
    inp = db.StringField(required=True, max_length=255, default="")
    outp = db.StringField(required=True, max_length=255, default="")
    optimal = db.BooleanField(required=True)
    vvector = db.ListField(
        db.IntField(required=True),
        required=True,
        default=lambda: [db.IntField() for x in range(3)]
    )


class Tableaux(db.DynamicEmbeddedDocument):
    """
    Represents an user's tableaux or dataset. Consists of a list of constraint
    names and a list of Candidates.
    """
    constraints = db.ListField(
        db.StringField(required=True, max_length=255, default=""),
        required=True,
        default=lambda: [db.StringField(default="") for x in range(3)]
    )
    candidates = db.ListField(
        db.EmbeddedDocumentField(Candidate, required=True),
        required=True,
        default=lambda: [Candidate(csrf_enabled=False)]
    )


class User(db.DynamicDocument):
    """
    A user of the application, has a name, salted password digest, salt, and a
    list of Tableaux belonging to the user.
    """
    username = db.StringField(required=True, max_length=255)
    password_digest = db.StringField(required=True)
    salt = db.StringField(required=True)
    datasets = db.ListField(db.EmbeddedDocumentField(Tableaux), default=lambda: [])

    def set_password(self, password):
        """
        Adds a randomly generated salt to the User, then appends it to the
        password before hashing it, then saves the digest.
        """
        self.salt = os.urandom(64).encode('hex')
        h = hashlib.sha512()
        password += self.salt
        h.update(password)
        self.password_digest = h.hexdigest()


    def is_password_valid(self, guess):
        """
        Appends the user's salt to the guess before hashing it, then compares
        it with the stored password digest.
        """
        h = hashlib.sha512()
        guess += self.salt
        h.update(guess)
        return h.hexdigest() == self.password_digest


