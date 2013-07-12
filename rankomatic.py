from flask import Flask, render_template, request
from flask.ext.mongoengine import MongoEngine
from models import tableaux_form

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = { 'DB': 'rankomatic' }
app.config['SECRET_KEY'] = 'keepThisSecret'
app.config['DEBUG'] = True

db = MongoEngine(app)





@app.route("/")
def table():
    form = tableaux_form(request.form)
    return render_template("table.html", form=form)


if __name__ == '__main__':
    app.run()

