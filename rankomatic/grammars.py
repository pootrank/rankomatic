
from flask import render_template, abort, Blueprint, make_response
from flask.views import MethodView
from rankomatic import db
import gridfs

grammars = Blueprint('grammars', __name__, template_folder='templates/grammars')

class StatsView(MethodView):

    def get(self, dirname):
        pass



class GrammarView(MethodView):

    def get(self, dirname):
        files = db.get_pymongo_db().tmp.files
        num_img = files.find({'filename': {'$regex': ('^'+dirname)}}).count()
        if num_img == 0 and dirname != 'emptyset':
            abort(404)
        else:
            return render_template('grammars.html', dirname=dirname,
                                num_img=num_img)


class GraphView(MethodView):

    def get(self, dirname, n):
        fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
        try:
            fname = '%s/grammar%s.svg' % (dirname, n)
            f = fs.get_last_version(filename=fname)
            response = make_response(f.read())
            response.mimetype = 'image/svg+xml'
            return response
        except gridfs.errors.NoFile:
            abort(404)



grammars.add_url_rule('/graphs/<dirname>/grammar<n>.svg',
                   view_func=GraphView.as_view('graph'))
grammars.add_url_rule('/grammars/<dirname>/',
                   view_func=GrammarView.as_view('grammars'))
grammars.add_url_rule('/stats/<dirname>/', view_func=StatsView.as_view('stats'))
