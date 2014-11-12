"""
Package: rankomatic.models
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
import dataset
import user

Dataset = dataset.Dataset
User = user.User
