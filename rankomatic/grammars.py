from flask import (render_template, abort, Blueprint,
                   make_response, request, redirect, url_for, jsonify)
from flask.views import MethodView
from rankomatic import db, worker_jobs
from rankomatic.util import get_dset, get_username, get_url_args
import urllib
import gridfs
import json

grammars = Blueprint('grammars', __name__,
                     template_folder='templates/grammars')


class GrammarView(MethodView):

    def get(self, dset_name, sort_value):
        if not self._check_params():
            return redirect(url_for('.grammars', dset_name=dset_name,
                                    classical=False, sort_value=sort_value,
                                    page=0, sort_by='rank_volume'))

        classical, page, sort_by = get_url_args()
        dset = get_dset(dset_name)
        dset.global_stats_calculated = False
        dset.grammar_stats_calculated = False
        dset.save()
        worker_jobs.calculate_grammars_and_statistics(dset_name, sort_value)
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
        worker_jobs.calculate_entailments(dset_name)
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
        self.dset_name = dset_name
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
                worker_jobs.make_grammar_info(dset_name)
                #job = q.enqueue(info_maker.make_grammar_info)
                to_return.update({
                    'need_redirect': False,
                    'finished': True,
                    'grammars_exist': True,
                    'grammar_stat_url': url_for(
                        'grammars.grammar_stats_calculated',
                        dset_name=dset_name, classical=classical, page=page,
                        sort_by=sort_by, sort_value=sort_value
                    ),
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


class GrammarStatsCalculated(MethodView):

    def get(self, dset_name, sort_value):
        dset = get_dset(dset_name)
        if not dset.grammar_stats_calculated:
            return jsonify(retry=True)
        else:
            classical, page, sort_by = get_url_args()
            dset = get_dset(dset_name)
            grammar_info = dset.grammar_info
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
grammars.add_url_rule('/grammar_stats_calculated/<dset_name>/<int:sort_value>',
                      view_func=GrammarStatsCalculated.as_view(
                          'grammar_stats_calculated'
                      ))
grammars.add_url_rule('/<dset_name>/stat_profile',
                      view_func=StatProfileView.as_view('stat_profile'))
