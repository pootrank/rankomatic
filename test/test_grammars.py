from test import OTOrderBaseCase
from flask import url_for
import itertools
from test_tools import delete_bad_datasets
from rankomatic.models import Dataset
from structures import png_filename
import mock
import json
import gridfs
import structures.structures


class MockJob(mock.MagicMock):

    JOB_ID = 0

    def __init__(self, id=JOB_ID, is_finished=False,
                 result=None, *args, **kwargs):
        super(MockJob, self).__init__(*args, **kwargs)
        self.id = id
        self.is_finished = is_finished
        self.result = result


class TestGrammar(OTOrderBaseCase):

    def setUp(self):
        self.bad_classical_values = set(['poop', 1, None])
        self.good_classical_values = set([True, False])
        self.bad_page_values = set([-1, None, "poop"])
        self.good_page_values = set([0, 1])
        self.bad_sort_by_values = set([0, "nope", None])
        self.good_sort_by_values = set(["rank_volume", "size"])

        dset = Dataset(user='guest', name='blank')
        dset.save()

    def tearDown(self):
        delete_bad_datasets()

    def get_grammar_url(self, classical, page, sort_by):
        return url_for('grammars.grammars', dset_name='blank', sort_value=0,
                       classical=classical, page=page, sort_by=sort_by)

    def test_bad_get(self):

        combos = []
        for combo in itertools.product(self.bad_classical_values,
                                       self.good_page_values,
                                       self.good_sort_by_values):
            combos.append(combo)
        for combo in itertools.product(self.good_classical_values,
                                       self.bad_page_values,
                                       self.good_sort_by_values):
            combos.append(combo)
        for combo in itertools.product(self.good_classical_values,
                                       self.good_page_values,
                                       self.bad_sort_by_values):
            combos.append(combo)

        urls = [self.get_grammar_url(*combo) for combo in combos]
        redirect_url = self.get_grammar_url(False, 0, 'rank_volume')
        for url in urls:
            response = self.client.get(url)
            self.assert_redirects(response, redirect_url)

    @mock.patch('rankomatic.worker_jobs.calculate_grammars_and_statistics')
    def test_good_get(self, mock_calculate_grams_and_stats):
        urls = []
        for combo in itertools.product(self.good_classical_values,
                                       self.good_page_values,
                                       self.good_sort_by_values):
            urls.append(self.get_grammar_url(*combo))
        for url in urls:
            response = self.client.get(url)
            self.assert_200(response)
            assert 'blank' in response.data
            assert mock_calculate_grams_and_stats.called


class TestGraph(OTOrderBaseCase):

    def setUp(self):
        self.dset_name = "blank"
        self.filename = "arnold.png"
        path = "/".join([self.dset_name, self.filename])
        self.fs = gridfs.GridFS(self.db.get_pymongo_db(), collection='tmp')
        with open(png_filename, 'rb') as png:
            self.png_id = self.fs.put(png, filename=path)

    def tearDown(self):
        delete_bad_datasets()
        self.fs.delete(self.png_id)

    def test_good_get(self):
        response = self.client.get(url_for('grammars.graph',
                                           dset_name=self.dset_name,
                                           filename=self.filename))
        self.assert_200(response)
        assert response.headers['Content-Type'] == 'image/png'

    def test_bad_gets(self):
        combos = [('NOT_A_DSET_NAME', self.filename),
                  (self.dset_name, 'NOT_A_FILENAME'),
                  ('NOT_A_DSET_NAME', 'NOT_A_FILENAME')]

        for combo in combos:
            response = self.client.get(url_for('grammars.graph',
                                               dset_name=combo[0],
                                               filename=combo[1]))
            self.assert_404(response)


class TestEntailmentsCalculated(OTOrderBaseCase):

    def make_entailment_dset(self, name, calculated, visualized):
        dset = Dataset(name=name, user="guest")
        dset.entailments_calculated = calculated
        dset.entailments_visualized = visualized
        dset.save()

    def setUp(self):
        self.make_entailment_dset('false-false', False, False)
        self.make_entailment_dset('true-false', True, False)
        self.make_entailment_dset('false-true', False, True)
        self.make_entailment_dset('true-true', True, True)

    def tearDown(self):
        delete_bad_datasets()

    def test_get_false_false(self):
        response = self.client.get(url_for('grammars.entailments_calculated',
                                           dset_name='false-false'))
        assert response.data == "false"

    def test_get_true_false(self):
        response = self.client.get(url_for('grammars.entailments_calculated',
                                           dset_name='true-false'))
        assert response.data == "false"

    def test_get_false_true(self):
        response = self.client.get(url_for('grammars.entailments_calculated',
                                           dset_name='false-true'))
        assert response.data == "false"

    def test_get_true_true(self):
        response = self.client.get(url_for('grammars.entailments_calculated',
                                           dset_name='true-true'))
        assert response.data == "true"


class TestGlobalStatsCalculated(OTOrderBaseCase):

    def setUp(self):
        pass

    def tearDown(self):
        delete_bad_datasets()

    def test_retry_and_not_finished(self):
        dset = Dataset(name='blank', user='guest')
        dset.global_stats_calculated = False
        dset.save()
        response = self.client.get(url_for('grammars.global_stats_calculated',
                                           dset_name='blank', sort_value=0,
                                           sort_by='size', page=0, classical=False))
        data = json.loads(response.data)
        self.assert_200(response)
        assert data['retry']
        assert not data['finished']

    def test_redirect_because_classical(self):
        dset = Dataset(name='blank', user='guest')
        dset.global_stats_calculated = True
        dset.classical = True
        dset.grammar_navbar['lengths'] = [6]
        dset.global_stats['grams'] = str([frozenset([(1, 2), (1, 3), (1, 4),
                                                     (2, 3), (2, 4), (3, 4)])])
        dset.save()

        response = self.client.get(url_for('grammars.global_stats_calculated',
                                           dset_name='blank', sort_value=0,
                                           classical=True, page=0,
                                           sort_by='size'))
        self.assert_200(response)
        data = json.loads(response.data)
        assert not data['finished']
        assert not data['retry']
        assert data['need_redirect']
        assert "/6?" in data['redirect_url']

    def test_redirect_because_no_grams(self):
        dset = Dataset(name='blank', user='guest')
        dset.global_stats_calculated = True
        dset.classical = False
        dset.grammar_navbar['lengths'] = [1, 3, 6]
        dset.global_stats['grams'] = "[]"
        dset.save()

        response = self.client.get(url_for('grammars.global_stats_calculated',
                                           dset_name='blank', sort_value=0,
                                           classical=False, page=0,
                                           sort_by='size'))
        self.assert_200(response)
        data = json.loads(response.data)
        assert not data['finished']
        assert not data['retry']
        assert data['need_redirect']
        assert "/6?" in data['redirect_url']

    @mock.patch('rankomatic.worker_jobs.make_grammar_info')
    def test_no_grammars_exist(self, mock_make_grammar_info):
        dset = Dataset(name='blank', user='guest')
        dset.global_stats_calculated = True
        dset.classical = False
        dset.grammar_navbar['lengths'] = []
        dset.global_stats = {
            'grams': "[]",
            'num_poots': 0,
            'num_total_poots': 19,
            'percent_poots': 0.0,
            'num_cots': 0,
            'num_total_cots': 6,
            'percent_cots': 0.0
        }
        dset.save()

        response = self.client.get(url_for(
            'grammars.global_stats_calculated', dset_name='blank',
            sort_value=0, classical=False, page=0, sort_by='size'
        ))
        print(response.data)
        self.assert_200(response)
        data = json.loads(response.data)
        assert not data['need_redirect']
        assert data['finished']
        assert not data['retry']
        assert not data['grammars_exist']
        assert not mock_make_grammar_info.called

    @mock.patch('rankomatic.worker_jobs.make_grammar_info')
    def test_no_redirect_html_response(self, mock_make_grammar_info):
        dset = Dataset(name='blank', user='guest')
        dset.global_stats_calculated = True
        dset.classical = False
        dset.grammar_navbar['lengths'] = [1, 3, 6]
        dset.global_stats = {
            'grams': "[frozenset([(1, 2)]), frozenset([2, 3])]",
            'num_poots': 5,
            'num_total_poots': 19,
            'percent_poots': 5.0/19,
            'num_cots': 2,
            'num_total_cots': 6,
            'percent_cots': 2.0/6
        }
        dset.save()

        response = self.client.get(url_for(
            'grammars.global_stats_calculated', dset_name='blank',
            sort_value=6, classical=False, page=0, sort_by='size'
        ))
        self.assert_200(response)
        print response.data
        data = json.loads(response.data)
        assert not data['need_redirect']
        assert data['finished']
        assert not data['retry']
        assert data['html_str']
        assert data['grammar_stat_url']
        mock_make_grammar_info.assert_called_with('blank')


class TestGrammarStatsCalculated(OTOrderBaseCase):

    def setUp(self):
        pass

    def tearDown(self):
        delete_bad_datasets()

    def test_not_finished(self):
        dset = Dataset(name='blank', username='guest')
        dset.grammar_stats_calculated = False
        dset.save()
        response = self.client.get(url_for(
            'grammars.grammar_stats_calculated', dset_name='blank',
            sort_value=0
        ))
        self.assert_200(response)
        data = json.loads(response.data)
        assert data['retry']
        assert len(data) == 1

    def test_finished(self):
        classical = False
        page = 0
        sort_by = 'size'
        sort_value = 1
        dset_name = 'blank'
        username = 'guest'
        dset = Dataset(name=dset_name, user=username)
        dset.grammar_navbar = {
            'min_ind': 0,
            'max_ind': 1,
            'lengths': [1, 3, 6],
            'num_rank_grams': 2
        }
        dset.grammar_stats_calculated = True
        dset.grammar_info = structures.structures.grammar_info
        dset.save()

        #mock_job = MockJob(is_finished=True,
                           #result=structures.structures.grammar_info)
        response = self.client.get(url_for(
            'grammars.grammar_stats_calculated',
            job_id=MockJob.JOB_ID, classical=classical, page=page,
            sort_value=sort_value, dset_name=dset_name,
            sort_by=sort_by
        ))
        self.assert_200(response)
        data = json.loads(response.data)
        assert not data['retry']
        assert "(C1, C2)" in data['html_str']
        assert len(data) == 2
        self.assert_template_used('display_grammars.html')


class TestEntailment(OTOrderBaseCase):

    @mock.patch('rankomatic.worker_jobs.calculate_entailments')
    def test_get(self, mock_calculate_entailments):
        dset_name = 'blank'
        dset = Dataset(name=dset_name, user='guest')
        dset.classical = False
        dset.save()

        response = self.client.get(url_for('grammars.entailments',
                                           dset_name=dset_name))
        self.assert_200(response)
        assert "Global Entailments" in response.data
        mock_calculate_entailments.assert_called_with(dset_name)
        self.assert_template_used('entailments.html')


class TestStatProfile(OTOrderBaseCase):

    def test_get(self):
        response = self.client.get(url_for('grammars.stat_profile',
                                           dset_name='blank'))
        self.assert_200(response)
