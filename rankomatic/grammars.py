import urllib
from flask import (render_template, abort, Blueprint,
                   make_response, request, redirect, url_for)
from flask.views import MethodView
from rankomatic import db
from rankomatic.models import Dataset
import gridfs

grammars = Blueprint('grammars', __name__,
                     template_folder='templates/grammars')
GRAMS_PER_PAGE = 20


class GrammarView(MethodView):

    def get(self, dset_name, num_rankings):
        if not self._check_params():
            return redirect(url_for('.grammars', dset_name=dset_name,
                                    num_rankings=num_rankings, page=0))
        unquoted_name = urllib.unquote_plus(dset_name)
        self._initialize_data_for_get(unquoted_name, num_rankings)
        self._calculate_global_stats()
        self._calculate_navbar_info(num_rankings)
        self._truncate_grams_for_pagination()
        self.dset.visualize_and_store_grammars([x[0] for x in self.grams])
        self.dset.save()
        return(render_template('grammars.html',
                               page=self.page,
                               num_rankings=num_rankings,
                               grammar_info=self._make_grammar_info(),
                               dset_name=unquoted_name,
                               **self.template_args))

    def _check_params(self):
        page = request.args.get('page')
        if page is not None and self._is_int(page) and int(page) >= 0:
            return True
        return False

    def _is_int(self, string):
        try:
            int(string)
        except ValueError:
            return False
        return True

    def _initialize_data_for_get(self, dset_name, num_rankings):
        self.page = int(request.args.get('page'))
        self.dset = Dataset.objects.get_or_404(name=dset_name)
        self.grams = self._get_correct_size_grammars(num_rankings)
        self.template_args = {}

    def _get_correct_size_grammars(self, num_rankings):
        raw_grammars = enumerate(self.dset.raw_grammars)
        return [(i, g) for i, g in raw_grammars if len(g) == num_rankings]

    def _calculate_global_stats(self):
        self.template_args.update({
            'num_poots': self.dset.poot.num_compatible_poots(),
            'num_poots': self.dset.poot.num_compatible_poots(),
            'num_total_poots': self.dset.poot.num_total_poots(),
            'percent_poots': self._make_percent_poots(self.dset.poot),
            'num_cots': self.dset.poot.num_compatible_cots(),
            'num_total_cots': self.dset.poot.num_total_cots(),
            'percent_cots': self._make_percent_cots(self.dset.poot)
        })

    def _make_percent_poots(self, poot):
        return (float(poot.num_compatible_poots()) /
                poot.num_total_poots()) * 100

    def _make_percent_cots(self, poot):
        return (float(poot.num_compatible_cots()) /
                poot.num_total_cots()) * 100

    def _calculate_navbar_info(self, num_rankings):
        grammar_lengths = self._get_grammar_lengths(self.dset)
        if num_rankings not in grammar_lengths and num_rankings != 0:
            abort(404)
        num_rank_grams = len(self.grams)
        navbar_info = self._get_min_max_indices(num_rank_grams)
        navbar_info.update({
            'lengths': grammar_lengths,
            'num_rank_grams': num_rank_grams,
        })
        self.template_args.update(navbar_info)

    def _get_grammar_lengths(self, dset):
        return sorted(set(map(len, dset.raw_grammars)), reverse=True)

    def _get_min_max_indices(self, num_rank_grams):
        min_ind = self.page * GRAMS_PER_PAGE
        max_ind = min_ind + GRAMS_PER_PAGE - 1
        if max_ind > num_rank_grams:
            max_ind = num_rank_grams - 1
        return {'min_ind': min_ind,
                'max_ind': max_ind}

    def _truncate_grams_for_pagination(self):
        min_ind = self.template_args['min_ind']
        max_ind = self.template_args['max_ind']
        self.grams = self.grams[min_ind:max_ind + 1]

    def _make_grammar_info(self):
        grammar_info = []
        for gram in self.grams:
            cot_stats_by_cand = self.dset.get_cot_stats_by_cand(gram[1])
            input_totals = self._sum_all_cot_stats(cot_stats_by_cand)
            grammar_info.append({
                'grammar': self._make_grammar_string(gram[0]),
                'filename': self._make_grammar_filename(gram[0]),
                'cots_by_cand': cot_stats_by_cand,
                'input_totals': input_totals})
        return grammar_info

    def _sum_all_cot_stats(self, cot_stats_by_cand):
        input_totals = {}
        for cand in cot_stats_by_cand:
            cand_stats = cot_stats_by_cand[cand]
            input_totals[cand] = self._sum_cot_stats_for_cand(cand_stats)
        return input_totals

    def _sum_cot_stats_for_cand(self, cot_stats):
        raw_sum = 0
        percent_sum = 0.0
        for cot_stat in cot_stats:
            raw_sum += cot_stat['num_cot']
            percent_sum += cot_stat['per_cot']
        return {
            'raw_sum': raw_sum,
            'per_sum': percent_sum}

    def _make_grammar_string(self, index):
        sorted_grammars = sorted(self.dset.grammars, key=len)
        return self.dset.grammar_to_string(sorted_grammars[index])

    def _make_grammar_filename(self, index):
        return 'grammar%d.svg' % index


class GraphView(MethodView):

    def get(self, dset_name, filename):
        fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
        filename = self._make_graph_filename(dset_name, filename)
        try:
            return self._build_image_response(fs, filename)
        except:
            abort(404)

    def _make_graph_filename(self, dset_name, filename):
        return "".join([dset_name, '/', filename])

    def _build_image_response(self, fs, filename):
        f = fs.get_last_version(filename=filename)
        response = make_response(f.read())
        response.mimetype = 'image/svg+xml'
        return response


class EntailmentView(MethodView):

    def get(self, dset_name):
        dset = Dataset.objects.get_or_404(name=dset_name)
        dset.calculate_global_entailments()
        dset.visualize_and_store_entailments()
        return render_template('entailments.html', dset_name=dset_name)


grammars.add_url_rule('/<dset_name>/grammars/<int:num_rankings>',
                      view_func=GrammarView.as_view('grammars'))
grammars.add_url_rule('/graphs/<dset_name>/<filename>.svg',
                      view_func=GraphView.as_view('graph'))
grammars.add_url_rule('/<dset_name>/entailments/',
                      view_func=EntailmentView.as_view('entailments'))
