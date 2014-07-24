from flask.ext.rq import job
from flask import (render_template, abort, Blueprint,
                   make_response, request, redirect, url_for)
from flask.views import MethodView
from rankomatic import db
from rankomatic.util import get_dset, get_username
import gridfs

grammars = Blueprint('grammars', __name__,
                     template_folder='templates/grammars')
GRAMS_PER_PAGE = 20


@job
def _calculate_entailments(dset_name, username):
    dset = get_dset(dset_name, username=username)
    dset.calculate_global_entailments()
    dset.visualize_and_store_entailments()


def _fork_entailment_calculation(dset_name):
    _calculate_entailments.delay(dset_name, get_username())


@job
def _visualize_and_store_grammars(dset_name, username, indices):
    dset = get_dset(dset_name, username=username)
    dset.visualize_and_store_grammars(indices)


class GrammarView(MethodView):

    def get(self, dset_name, num_rankings):
        if not self._check_params():
            return redirect(url_for('.grammars', dset_name=dset_name,
                                    num_rankings=num_rankings, page=0))
        self._initialize_data_for_get(dset_name, num_rankings)
        self._calculate_global_stats()
        self._calculate_navbar_info(num_rankings)
        if not self.grams:
            new_num_rankings = self.template_args['lengths'][-1]
            return(redirect(url_for('.grammars', dset_name=dset_name,
                                    num_rankings=new_num_rankings, page=0)))
        self._truncate_grams_for_pagination()
        self._fork_grammar_visualization(dset_name)
        return(render_template('grammars.html',
                               page=self.page,
                               num_rankings=num_rankings,
                               dset_name=dset_name,
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
        self.dset = get_dset(dset_name)
        self.grams = self._get_correct_size_grammars(num_rankings)
        self.template_args = {}

    def _get_correct_size_grammars(self, num_rankings):
        raw_grammars = enumerate(self.dset.raw_grammars)
        return [(i, g) for i, g in raw_grammars if len(g) == num_rankings]

    def _calculate_global_stats(self):
        self.template_args.update({
            'num_poots': self.dset.num_compatible_poots(),
            'num_total_poots': self.dset.num_total_poots(),
            'percent_poots': self._make_percent_poots(),
            'num_cots': self.dset.num_compatible_cots(),
            'num_total_cots': self.dset.num_total_cots(),
            'percent_cots': self._make_percent_cots()
        })

    def _make_percent_poots(self):
        return (float(self.dset.num_compatible_poots()) /
                self.dset.num_total_poots()) * 100

    def _make_percent_cots(self):
        return (float(self.dset.num_compatible_cots()) /
                self.dset.num_total_cots()) * 100

    def _calculate_navbar_info(self, num_rankings):
        grammar_lengths = self._get_grammar_lengths()
        if num_rankings not in grammar_lengths and num_rankings != 0:
            abort(404)
        num_rank_grams = len(self.grams)
        navbar_info = self._get_min_max_indices(num_rank_grams)
        navbar_info.update({
            'lengths': grammar_lengths,
            'num_rank_grams': num_rank_grams,
        })
        self.template_args.update(navbar_info)

    def _get_grammar_lengths(self):
        return sorted(set(map(len, self.dset.raw_grammars)), reverse=True)

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

    def _fork_grammar_visualization(self, dset_name):
        if self.grams:
            index_range = self._get_index_range_str()
            self.dset.grammars_stored[index_range] = False
            self.dset.save()
            _visualize_and_store_grammars.delay(dset_name, get_username(),
                                                [x[0] for x in self.grams])

    def _get_index_range_str(self):
        return str(self.grams[0][0]) + '-' + str(self.grams[-1][0])


class GraphView(MethodView):

    def get(self, dset_name, filename):
        fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
        filename = self._make_graph_filename(dset_name, filename)
        try:
            return self._build_image_response(fs, filename)
        except gridfs.NoFile:
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
        _fork_entailment_calculation(dset_name)
        return render_template('entailments.html', dset_name=dset_name)


class EntailmentsCalculatedView(MethodView):

    def get(self, dset_name):
        dset = get_dset(dset_name)
        if dset.entailments_calculated and dset.entailments_visualized:
            return "true"
        else:
            return "false"


class GrammarsStoredView(GrammarView):

    def get(self, dset_name, num_rankings):
        self._initialize_data_for_get(dset_name, num_rankings)
        self._calculate_global_stats()
        self._calculate_navbar_info(num_rankings)
        self._truncate_grams_for_pagination()
        if self.dset.grammars_stored[self._get_index_range_str()]:
            return render_template('display_grammars.html',
                                   dset_name=dset_name,
                                   grammar_info=self._make_grammar_info())
        else:
            return "false"

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


grammars.add_url_rule('/<dset_name>/grammars/<int:num_rankings>',
                      view_func=GrammarView.as_view('grammars'))
grammars.add_url_rule('/graphs/<dset_name>/<filename>',
                      view_func=GraphView.as_view('graph'))
grammars.add_url_rule('/<dset_name>/entailments/',
                      view_func=EntailmentView.as_view('entailments'))
grammars.add_url_rule('/entailments_calculated/<dset_name>/',
                      view_func=EntailmentsCalculatedView.as_view(
                          'entailments_calculated'
                      ))
grammars.add_url_rule('/grammars_stored/<dset_name>/<int:num_rankings>',
                      view_func=GrammarsStoredView.as_view('grammars_stored'))
