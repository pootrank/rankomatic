from flask.ext.rq import job
from rq import Queue
from rq.job import Job
from redis import Redis
from flask import (render_template, abort, Blueprint,
                   make_response, request, redirect, url_for, jsonify)
from flask.views import MethodView
from rankomatic import db
from rankomatic.util import get_dset, get_username, get_url_args
from rankomatic.models import Dataset
import urllib
import gridfs
import json

grammars = Blueprint('grammars', __name__,
                     template_folder='templates/grammars')
GRAMS_PER_PAGE = 20
redis_conn = Redis()
q = Queue(connection=redis_conn)


def _calculate_grammars_and_statistics(dset_name, sort_value,
                                       classical, page, username, sort_by):
    gc = GrammarCalculator(dset_name, sort_value, classical, page, username, sort_by)
    gc._get_initial_data()
    gc._calculate_global_stats()
    gc._calculate_navbar_info()
    gc._truncate_grams_for_pagination()
    gc.dset.global_stats_calculated = True
    gc.dset.save()


@job
def _calculate_entailments(dset_name, username):
    dset = get_dset(dset_name, username=username)
    dset.calculate_global_entailments()
    dset.visualize_and_store_entailments()


def _fork_entailment_calculation(dset_name):
    _calculate_entailments.delay(dset_name, get_username())


@job
def _visualize_and_store_grammars(dset_name, username, indices):
    dset = Dataset.objects.get(name=urllib.unquote(dset_name), user=username)
    dset.visualize_and_store_grammars(indices)


class GrammarCalculator():

    def __init__(self, dset_name, sort_value, classical,
                 page, username, sort_by='rank_volume'):
        self.dset_name = dset_name
        self.sort_value = sort_value
        self.classical = classical
        self.page = page
        self.username = username
        self.sort_by = sort_by

    def _get_initial_data(self):
        self.dset = get_dset(self.dset_name, self.username)
        self.dset.classical = self.classical
        if self.classical:
            self.sort_value = sum(range(len(self.dset.constraints)))
        self.grams = self._get_correct_grammars()
        self.dset.global_stats = {}

    def _get_correct_grammars(self):
        if self.classical:
            self.sort_value = self._classical_grammar_length()
        self.dset.sort_by(self.sort_by)
        self.dset.calculate_compatible_grammars(self.classical)

        raw_grammars = enumerate(self.dset.raw_grammars)
        sorter = self.dset.get_grammar_sorter()
        return [(i, g) for i, g in raw_grammars if sorter(g) == self.sort_value]

    def _classical_grammar_length(self):
        return sum(range(len(self.dset.constraints)))

    def _calculate_global_stats(self):
        if not self.classical:
            self.dset.global_stats.update({
                'num_poots': self.dset.num_compatible_poots(),
                'num_total_poots': self.dset.num_total_poots(),
                'percent_poots': self._make_percent_poots()
            })

        self.dset.global_stats.update({
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

    def _calculate_navbar_info(self):
        grammar_lengths = self._get_grammar_lengths()
        if self.classical:
            self.sort_value = self._classical_grammar_length()
        elif self.sort_value not in grammar_lengths and self.sort_value != 0:
            abort(404)
        num_rank_grams = len(self.grams)
        self.dset.grammar_navbar = self._get_min_max_indices(num_rank_grams)
        self.dset.grammar_navbar.update({
            'lengths': grammar_lengths,
            'num_rank_grams': num_rank_grams,
        })

    def _get_grammar_lengths(self):
        if self.sort_by == 'size':
            reverse = True
        elif self.sort_by == 'rank_volume':
            reverse = False
        return sorted(set(map(self.dset.get_grammar_sorter(), self.dset.raw_grammars)), reverse=reverse)

    def _get_min_max_indices(self, num_rank_grams):
        min_ind = self.page * GRAMS_PER_PAGE
        max_ind = min_ind + GRAMS_PER_PAGE - 1
        if max_ind > num_rank_grams:
            max_ind = num_rank_grams - 1
        return {'min_ind': min_ind,
                'max_ind': max_ind}

    def _truncate_grams_for_pagination(self):
        min_ind = self.dset.grammar_navbar['min_ind']
        max_ind = self.dset.grammar_navbar['max_ind']
        self.grams = self.grams[min_ind:max_ind + 1]
        self.dset.global_stats['grams'] = str(self.grams)


class GrammarView(MethodView):

    def get(self, dset_name, sort_value):
        if not self._check_params():
            return redirect(url_for('.grammars', dset_name=dset_name,
                                    classical=False, sort_value=sort_value,
                                    page=0, sort_by='rank_volume'))

        classical, page, sort_by = get_url_args()
        dset = get_dset(dset_name)
        dset.global_stats_calculated = False
        dset.save()
        q.enqueue(_calculate_grammars_and_statistics, args=(dset_name, sort_value, classical,
                                                            page, get_username(), sort_by), timeout=500)
        return(render_template('grammars.html', page=page,
                               sort_value=sort_value, dset_name=dset_name))

    def _check_params(self):
        return self._check_page() and self._check_classical() and self._check_sort_by()

    def _check_page(self):
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

    def _check_classical(self):
        classical = request.args.get('classical')
        return self._is_bool(classical)

    def _is_bool(self, string):
        try:
            to_check = json.loads(string.lower())
        except (ValueError, AttributeError):
            return False
        else:
            if to_check is True or to_check is False:
                return True
            else:
                return False

    def _check_sort_by(self):
        sort_by = request.args.get('sort_by')
        return sort_by in ['rank_volume', 'size']


class GraphView(MethodView):

    def get(self, dset_name, filename):
        dset_name = urllib.quote(dset_name)
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
        response.mimetype = 'image/png'
        return response


class EntailmentView(MethodView):

    def get(self, dset_name):
        classical = get_dset(dset_name).classical
        _fork_entailment_calculation(dset_name)
        return render_template('entailments.html', dset_name=dset_name,
                               classical=classical)


class EntailmentsCalculatedView(MethodView):

    def get(self, dset_name):
        dset = get_dset(dset_name)
        if dset.entailments_calculated and dset.entailments_visualized:
            return "true"
        else:
            return "false"


class GlobalStatsCalculatedView(MethodView):

    def get(self, dset_name, sort_value):
        self.dset = get_dset(dset_name)
        classical, page, sort_by = get_url_args()
        to_return = {'finished': False}
        if not self.dset.global_stats_calculated:
            to_return['retry'] = True
        else:
            to_return['retry'] = False
            self.grams = eval(self.dset.global_stats['grams'])

            need_redirect = (self.dset.classical and sort_value == 0) or not self.grams
            if need_redirect and self.dset.grammar_navbar['lengths']:
                to_return['need_redirect'] = True
                new_sort_value = self.dset.grammar_navbar['lengths'][-1]
                to_return['redirect_url'] = url_for(
                    '.grammars', dset_name=dset_name, classical=self.dset.classical,
                    sort_value=new_sort_value, page=0, sort_by=get_url_args()[2]
                )
            elif self.grams and self.dset.grammar_navbar['lengths']:
                self.username = get_username()
                job = q.enqueue(self._make_grammar_info)
                to_return.update({
                    'need_redirect': False,
                    'finished': True,
                    'job_id': job.id,
                    'dset_name': dset_name,
                    'classical': self.dset.classical,
                    'page': page,
                    'grammars_exist': True,
                    'html_str': render_template('display_global_stats.html',
                                                dset_name=dset_name,
                                                classical=self.dset.classical,
                                                **self.dset.global_stats)
                })
            else:
                to_return.update({
                    'grammars_exist': False,
                    'need_redirect': False,
                    'finished': True
                })

        return jsonify(**to_return)

    def _make_grammar_info(self):
        self.dset = get_dset(self.dset.name, self.username)
        self.dset.visualize_and_store_grammars([x[0] for x in self.grams])
        self.dset.save()
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
        #sorted_grammars = sorted(self.dset.grammars, key=self.dset.get_grammar_sorter())
        return self.dset.grammar_to_string(index)

    def _make_grammar_filename(self, index):
        return 'grammar%d.png' % index

    def _fork_grammar_visualization(self, dset_name):
        if self.grams:
            index_range = self._get_index_range_str()
            self.dset.grammars_stored[index_range] = False
            self.dset.save()
            _visualize_and_store_grammars.delay(dset_name, get_username(),
                                                [x[0] for x in self.grams])

    def _get_index_range_str(self):
        return str(self.grams[0][0]) + '-' + str(self.grams[-1][0])


class GrammarStatsCalculated(MethodView):

    def get(self, dset_name, sort_value):
        job_id = request.args.get('job_id')
        job = Job.fetch(job_id, connection=redis_conn)
        if not job.is_finished:
            return jsonify(retry=True)
        else:
            classical, page, sort_by = get_url_args()
            dset = get_dset(dset_name)
            grammar_info = job.result
            html_str = render_template('display_grammars.html',
                                       dset_name=dset_name,
                                       grammar_info=grammar_info,
                                       classical=classical, page=page,
                                       sort_by=sort_by,
                                       sort_value=sort_value,
                                       **dset.grammar_navbar)
            return jsonify(retry=False, html_str=html_str)


class StatProfileView(MethodView):

    def get(self, dset_name):
        return render_template('under_construction.html')



grammars.add_url_rule('/<dset_name>/grammars/<int:sort_value>',
                      view_func=GrammarView.as_view('grammars'))
grammars.add_url_rule('/graphs/<dset_name>/<filename>',
                      view_func=GraphView.as_view('graph'))
grammars.add_url_rule('/<dset_name>/entailments/',
                      view_func=EntailmentView.as_view('entailments'))
grammars.add_url_rule('/entailments_calculated/<dset_name>/',
                      view_func=EntailmentsCalculatedView.as_view(
                          'entailments_calculated'
                      ))
grammars.add_url_rule('/global_stats_calculated/<dset_name>/<int:sort_value>',
                      view_func=GlobalStatsCalculatedView.as_view(
                          'global_stats_calculated'
                      ))
grammars.add_url_rule('/<dset_name>/stat_profile',
                      view_func=StatProfileView.as_view('stat_profile'))
grammars.add_url_rule('/grammar_stats_calculated/<dset_name>/<int:sort_value>',
                      view_func=GrammarStatsCalculated.as_view(
                          'grammar_stats_calculated'
                      ))
