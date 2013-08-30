
from flask import render_template, abort, Blueprint, make_response
from flask.views import MethodView
from rankomatic import db
from rankomatic.models import Dataset
import gridfs

grammars = Blueprint('grammars', __name__, template_folder='templates/grammars')

class StatsView(MethodView):

    def get(self, dset_name):
        dset = Dataset.objects.get_or_404(name=dset_name)
        dset.calculate_compatible_grammars(classical=False)
        num_poots = dset.poot.num_compatible_poots()
        num_total_poots = dset.poot.num_total_poots()
        per_poots = (float(num_poots) / num_total_poots) * 100
        num_cots = dset.poot.num_compatible_cots()
        num_total_cots = dset.poot.num_total_cots()
        per_cots = (float(num_cots) / num_total_cots) * 100
        cots_by_cand = dset.get_cots_by_cand()
        input_totals = {}
        for k in cots_by_cand:
            raw_sum = 0
            per_sum = 0.0
            for c in cots_by_cand[k]:
                raw_sum += c['num_cot']
                per_sum += c['per_cot']
            input_totals[k] = {'raw_sum': raw_sum, 'per_sum': per_sum}
        dset.save()
        return(render_template('stats.html',
                               num_poots=num_poots,
                               num_total_poots=num_total_poots,
                               percent_poots=per_poots,
                               num_cots=num_cots,
                               num_total_cots=num_total_cots,
                               percent_cots=per_cots,
                               cots_by_cand=cots_by_cand,
                               input_totals=input_totals,
                               dset_name=dset_name))


class GrammarView(MethodView):

    def get(self, dset_name):
        dset = Dataset.objects.get_or_404(name=dset_name)
        dset.visualize_and_store_grammars()
        num_img = len(dset.grammars)
        return render_template('grammars.html', dset_name=dset_name,
                               num_img=num_img)


class GraphView(MethodView):

    def get(self, dset_name, filename):
        filename = "".join([dset_name, '/', filename])
        fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
        try:
            f = fs.get_last_version(filename=filename)
            response = make_response(f.read())
            response.mimetype = 'image/svg+xml'
            return response
        except:
            abort(404)

class EntailmentView(MethodView):

    def get(self, dset_name):
        dset = Dataset.objects.get_or_404(name=dset_name)
        dset.calculate_global_entailments()
        dset.visualize_and_store_entailments()
        return render_template('entailments.html', dset_name=dset_name)



grammars.add_url_rule('/graphs/<dset_name>/<filename>.svg',
                   view_func=GraphView.as_view('graph'))
grammars.add_url_rule('/<dset_name>/grammars/',
                   view_func=GrammarView.as_view('grammars'))
grammars.add_url_rule('/<dset_name>/entailments/',
                      view_func=EntailmentView.as_view('entailments'))
grammars.add_url_rule('/<dset_name>/stats/', view_func=StatsView.as_view('stats'))
