"""
File: models.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Defines the models for use with the Optimality Theory constraint-ranking
website. They are implemented for MongoDB using MongoEngine. As of now the
models are User, Tableaux, and Candidate.

User: Self-explanatory. A user of the website.
Tableaux: Represents an user's tableaux or dataset. Consists of a list of
          constraint names and a list of Candidates.
Candidate: A single row from the Tableaux, in OT terms an input-outuput pair.
           Also contains whether or not the output is optimal for the input
           and the violation vector for the constraint set of the Tableaux.
"""
#TODO make sure documentation is up to date.

from mongoengine import (DynamicDocument, DynamicEmbeddedDocument,
                         EmbeddedDocumentField, StringField,
                         BooleanField, ListField, IntField)
from flask.ext.mongoengine.wtf import model_form


class Candidate(DynamicEmbeddedDocument):
    """
    A single row from the Tableaux, in OT terms an input-outuput pair.
    Also contains whether or not the output is optimal for the input
    and the violation vector for the constraint set of the Tableaux.
    """
    inp = StringField(required=True, max_length=255, default="")
    outp = StringField(required=True, max_length=255, default="")
    optimal = BooleanField(required=True)
    vvector = ListField(
        IntField(required=True),
        required=True,
        default=lambda: [IntField(default="") for x in range(3)]
    )


class Tableaux(DynamicDocument):
    """
    Represents an user's tableaux or dataset. Consists of a list of constraint
    names and a list of Candidates.
    """
    constraints = ListField(
        StringField(required=True, max_length=255, default=""),
        required=True,
        default=lambda: [StringField(default="") for x in range(3)]
    )
    candidates = ListField(
        EmbeddedDocumentField(Candidate, required=True),
        required=True,
        default=lambda: [Candidate(csrf_enabled=False)]
    )

candidate_form = model_form(Candidate)
tableaux_form = model_form(Tableaux)

