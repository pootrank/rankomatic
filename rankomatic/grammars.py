import urllib
import gridfs
import json

from flask import (render_template, abort, Blueprint,
                   make_response, request, redirect, url_for, jsonify)
from flask.views import MethodView

from rankomatic import db, worker_jobs
from rankomatic.util import get_dset, get_username, get_url_args

grammars = Blueprint('grammars', __name__,
                     template_folder='templates/grammars')


class GrammarView(MethodView):

    def get(self, dset_name, sort_value):
        if not self._check_params():
            return redirect(url_for('.grammars', dset_name=dset_name,
                                    classical=False, sort_value=sort_value,
                                    page=0, sort_by='rank_volume'))
        classical, page, sort_by = get_url_args()
        self._initialize_dset(dset_name)
        worker_jobs.calculate_grammars_and_statistics(dset_name, sort_value)
        return(render_template('grammars.html', page=page,
                               sort_value=sort_value, dset_name=dset_name))

    def _check_params(self):
        return (self._check_page() and
                self._check_classical() and
                self._check_sort_by())

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
            return to_check is True or to_check is False

    def _check_sort_by(self):
        sort_by = request.args.get('sort_by')
        return sort_by in ['rank_volume', 'size']

    def _initialize_dset(self, dset_name):
        self.dset = get_dset(dset_name)
        self.dset.global_stats_calculated = False
        self.dset.grammar_stats_calculated = False
        self.dset.save()


class GraphView(MethodView):

    @property
    def fs(self):
        return gridfs.GridFS(db.get_pymongo_db(), collection='tmp')

    def get(self, dset_name, filename):
        dset_name = urllib.quote(dset_name)
        filename = self._make_graph_filename(dset_name, filename)
        try:
            return self._build_image_response(filename)
        except gridfs.NoFile:
            abort(404)

    def _make_graph_filename(self, dset_name, filename):
        return "".join([dset_name, '/', filename])

    def _build_image_response(self, filename):
        f = self.fs.get_last_version(filename=filename)
        response = make_response(f.read())
        response.mimetype = 'image/png'
        return response


class EntailmentView(MethodView):

    def get(self, dset_name):
        dset = get_dset(dset_name)
        classical = dset.classical
        worker_jobs.calculate_entailments(dset_name)
        return render_template('entailments.html', dset_name=dset_name,
                               apriori=dset.apriori_ranking.string,
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
        self._setup_for_get(dset_name, sort_value)
        if not self.dset.global_stats_calculated:
            self.return_dict['retry'] = True
        else:
            self.return_dict['retry'] = False
            self._determine_values_to_return()
        return jsonify(**self.return_dict)

    def _setup_for_get(self, dset_name, sort_value):
        self.dset = get_dset(dset_name)
        self.dset_name = dset_name
        self.sort_value = sort_value
        self.classical, self.page, self.sort_by = get_url_args()
        self.return_dict = {'finished': False}

    def _determine_values_to_return(self):
        self._get_grams()
        if self._need_redirect():
            self._display_redirect()
        elif self._grammars_selected():
            worker_jobs.make_grammar_info(self.dset_name)
            self._display_global_stats()
        else:
            self._display_no_grammars_exist()

    def _get_grams(self):
        self.grams = eval(self.dset.global_stats['grams'])

    def _need_redirect(self):
        no_classical_sort_value = self.dset.classical and self.sort_value == 0
        return self._grammars_exist() and (no_classical_sort_value or
                                           not self._grammars_selected())

    def _grammars_selected(self):
        return self.grams

    def _grammars_exist(self):
        return self.dset.grammar_navbar['lengths'] != []

    def _display_redirect(self):
        self.return_dict['need_redirect'] = True
        self.return_dict['redirect_url'] = self._redirect_url()

    def _redirect_url(self):
        return url_for(
            '.grammars', dset_name=self.dset_name, classical=self.classical,
            sort_value=self._new_sort_value(), page=0, sort_by=self.sort_by
        )

    def _new_sort_value(self):
        return self.dset.grammar_navbar['lengths'][-1]

    def _display_global_stats(self):
        self.username = get_username()
        self.return_dict.update({
            'need_redirect': False,
            'finished': True,
            'grammars_exist': True,
            'grammar_stat_url': self._grammar_stat_url(),
            'html_str': self._global_stats_html()
        })

    def _grammar_stat_url(self):
        return url_for(
            'grammars.grammar_stats_calculated', dset_name=self.dset_name,
            classical=self.classical, page=self.page, sort_by=self.sort_by,
            sort_value=self.sort_value
        )

    def _global_stats_html(self):
        return render_template(
            'display_global_stats.html', dset_name=self.dset_name,
            classical=self.dset.classical, **self.dset.global_stats
        )

    def _display_no_grammars_exist(self):
        self.return_dict.update({
            'grammars_exist': False,
            'need_redirect': False,
            'finished': True,
            'dset_name': self.dset.name,
            'apriori': ""
        })
        if self.dset.apriori_ranking.string != "{ }":
            self.return_dict['apriori'] = self.dset.apriori_ranking.string


class GrammarStatsCalculated(MethodView):

    def get(self, dset_name, sort_value):
        self._setup_for_get(dset_name, sort_value)
        if not self.dset.grammar_stats_calculated:
            return jsonify(retry=True)
        else:
            return jsonify(retry=False, html_str=self._grammar_stats_html())

    def _setup_for_get(self, dset_name, sort_value):
        self.dset_name = dset_name
        self.dset = get_dset(dset_name)
        self.sort_value = sort_value
        self.classical, self.page, self.sort_by = get_url_args()

    def _grammar_stats_html(self):
        return render_template(
            'display_grammars.html', dset_name=self.dset_name, page=self.page,
            apriori=self.dset.apriori_ranking.string,
            grammar_info=self.dset.grammar_info, sort_by=self.sort_by,
            sort_value=self.sort_value, classical=self.classical,
            **self.dset.grammar_navbar
        )


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
grammars.add_url_rule('/grammar_stats_calculated/<dset_name>/<int:sort_value>',
                      view_func=GrammarStatsCalculated.as_view(
                          'grammar_stats_calculated'
                      ))
grammars.add_url_rule('/<dset_name>/stat_profile',
                      view_func=StatProfileView.as_view('stat_profile'))
