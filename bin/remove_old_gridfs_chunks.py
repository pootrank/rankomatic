#! /usr/bin/env python
"""Remove orphaned GridFS chunks from MongoDB"""

import pymongo
import os

uri = os.environ.get('MONGOHQ_URL')
info = pymongo.uri_parser.parse_uri(uri)
cli = pymongo.MongoClient(uri)
db = cli[info['database']]

files = db.tmp.files
chunks = db.tmp.chunks

for doc in chunks.find():
    files_id = doc['files_id']
    if not files.find_one(files_id):
        chunks.remove(doc['_id'])


