from flask import Flask, render_template, request
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.wtf import model_form

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = { 'DB': 'rankomatic' }
app.config['SECRET_KEY'] = 'keepThisSecret'
app.config['DEBUG'] = True

db = MongoEngine(app)


class Candidate(db.DynamicEmbeddedDocument):
    inp = db.StringField(required=True, max_length=255, default="")
    outp = db.StringField(required=True, max_length=255, default="")
    optimal = db.BooleanField(required=True)
    vvector = db.ListField(db.IntField(required=True),
                           required=True,
                           default=lambda: [db.IntField(default="") for x in range(3)])

candidate_form = model_form(Candidate)

class Tableaux(db.DynamicDocument):
    constraints = db.ListField(db.StringField(required=True, max_length=255, default=""),
                               required=True,
                               default=lambda: [db.StringField(default="") for x in range(3)])
    candidates = db.ListField(db.EmbeddedDocumentField(Candidate, required=True),
                              required=True,
                              default=lambda: [candidate_form(csrf_enabled=False)])

tableaux_form = model_form(Tableaux)


@app.route("/")
def table():
    form = tableaux_form(request.form)
    return render_template("table.html", form=form)


if __name__ == '__main__':
    app.run()

