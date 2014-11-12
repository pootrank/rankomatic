from rankomatic import db


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
