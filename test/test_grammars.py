from test import OTOrderBaseCase
from flask import url_for
import itertools
from test_tools import delete_bad_datasets
from rankomatic.models import Dataset
from structures import png_filename
import mock
import json
import gridfs


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

    @mock.patch('rq.Queue.enqueue')
    def test_good_get(self, mock_enqueue):
        urls = []
        for combo in itertools.product(self.good_classical_values,
                                       self.good_page_values,
                                       self.good_sort_by_values):
            urls.append(self.get_grammar_url(*combo))
        for url in urls:
            response = self.client.get(url)
            self.assert_200(response)
            assert 'blank' in response.data
            assert mock_enqueue.called


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
                                           dset_name='blank', sort_value=0))
        data = json.loads(response.data)
        self.assert_200(response)
        assert data['retry']
        assert not data['finished']

    def test_redirect_because_classical(self):
        dset = Dataset(name='blank', user='guest')
        dset.global_stats_calculated = True
        dset.classical = True
        dset.grammar_navbar['lengths'] = [6]
        dset.global_stats['grams'] = str([frozenset([(1,2), (1,3), (1,4),
                                                     (2,3), (2,4), (3,4)])])
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

    @mock.patch('rankomatic.grammars.GlobalStatsCalculatedView._fork_grammar_visualization')
    def test_need_redirect_no_lengths(self, mock_fork_grammar_visualization):
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

        response = self.client.get(url_for('grammars.global_stats_calculated',
                                           dset_name='blank', sort_value=0,
                                           classical=False, page=0,
                                           sort_by='size'))
        self.assert_200(response)
        data = json.loads(response.data)
        assert not data['need_redirect']
        assert data['finished']
        assert not data['retry']
        assert mock_fork_grammar_visualization.called

    @mock.patch('rankomatic.grammars.GlobalStatsCalculatedView._fork_grammar_visualization')
    def test_no_redirect_html_response(self, mock_fork_grammar_visualization):
        dset = Dataset(name='blank', user='guest')
        dset.global_stats_calculated = True
        dset.classical = False
        dset.grammar_navbar['lengths'] = [1,3,6]
        dset.global_stats = {
            'grams': "[frozenset([(1,2)]), frozenset([2,3])]",
            'num_poots': 5,
            'num_total_poots': 19,
            'percent_poots': 5.0/19,
            'num_cots': 2,
            'num_total_cots': 6,
            'percent_cots': 2.0/6
        }
        dset.save()

        response = self.client.get(url_for('grammars.global_stats_calculated',
                                           dset_name='blank', sort_value=6,
                                           classical=False, page=0,
                                           sort_by='size'))
        self.assert_200(response)
        data = json.loads(response.data)
        assert not data['need_redirect']
        assert data['finished']
        assert not data['retry']
        assert mock_fork_grammar_visualization.called


class TestGrammarsStored(OTOrderBaseCase):

    def setUp(self):
        pass

    def tearDown(self):
        delete_bad_datasets()

    class MockJob():

        JOB_ID = 0

        def __init__(self, id=JOB_ID):
            self.id = id

    @mock.patch('rq.Queue.enqueue', return_value=MockJob())
    def test_no_grammars_found(self, mock_enqueue):
        # no compatible grammars
        dset = Dataset(name='blank', user='guest')
        dset.global_stats['grams'] = ""
        dset.grammar_navbar['lengths'] = []
        dset.save()
        response = self.client.get(url_for('grammars.grammars_stored',
                                           dset_name='blank',
                                           sort_value=0,
                                           page=0, sort_by='rank_volume',
                                           classical=False))
        self.assert_200(response)
        data = json.loads(response.data)
        assert not data['retry']
        assert not data['grammars_exist']
        assert not mock_enqueue.called

    @mock.patch('rq.Queue.enqueue', return_value=MockJob())
    def test_no_grammars_stored(self, mock_enqueue):
        # grammars found but not stored yet
        dset = Dataset(name='blank', user='guest')
        dset.global_stats['grams'] = "[(0, frozenset([(1, 2)]))]"
        dset.grammar_navbar['lengths'] = [1]
        dset.save()
        response = self.client.get(url_for('grammars.grammars_stored',
                                           dset_name='blank',
                                           sort_value=1,
                                           page=0, sort_by='size',
                                           classical=False))
        self.assert_200(response)
        data = json.loads(response.data)
        assert data['retry']
        assert len(data) == 1
        assert not mock_enqueue.called

    @mock.patch('rq.Queue.enqueue', return_value=MockJob())
    def test_grammars_stored(self, mock_enqueue):
        dset_name = 'blank'
        username = 'guest'
        page_value = 0
        classical = False
        dset = Dataset(name=dset_name, user=username)
        dset.global_stats['grams'] = "[(0, frozenset([(1, 2)]))]"
        dset.grammar_navbar['lengths'] = [1]
        dset.grammars_stored['0-0'] = True
        dset.save()
        response = self.client.get(url_for('grammars.grammars_stored',
                                           dset_name='blank',
                                           sort_value=1,
                                           page=page_value,
                                           sort_by='size',
                                           classical=classical))
        self.assert_200(response)
        assert mock_enqueue.called
        data = json.loads(response.data)
        assert data['job_id'] == self.MockJob.JOB_ID
        assert data['dset_name'] == dset_name
        assert data['classical'] is classical
        assert data['page'] == page_value
        assert not data['retry']
        assert data['grammars_exist']
        assert len(data) == 6
