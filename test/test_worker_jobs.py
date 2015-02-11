import mock
import ot.data
import json
from Queue import Queue

from nose import with_setup
from test import OTOrderBaseCase
from test_tools import delete_bad_datasets
from rankomatic import worker_jobs
from rankomatic.models import Dataset
from rankomatic.worker_jobs import (calculate_grammars_and_statistics,
                                    calculate_entailments, make_grammar_info,
                                    _calculate_entailments,
                                    _calculate_grammars_and_statistics,
                                    GrammarInfoMaker)


mod = {}
cv_grammars = set([
    frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 1), (2, 4)]),
    frozenset([(3, 2), (3, 1), (2, 1), (4, 3), (4, 2), (4, 1)]),
    frozenset([(1, 2), (3, 2), (3, 1), (4, 3), (4, 2), (4, 1)]),
    frozenset([(1, 2), (3, 2), (1, 3), (4, 3), (4, 2), (4, 1)]),
    frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 2), (4, 1)]),
    frozenset([(1, 2), (3, 2), (3, 4), (3, 1), (4, 2), (4, 1)])
])
voweldset_grammars = set([
    frozenset([(3, 1), (2, 3), (2, 4), (2, 1)]),
    frozenset([(3, 2), (3, 1), (2, 1)]), frozenset([(3, 1), (2, 4), (2, 1)]),
    frozenset([(2, 3), (3, 1), (4, 1), (2, 1)]), frozenset([(3, 1), (2, 1)]),
    frozenset([(3, 1), (4, 1), (2, 1)]), frozenset([(3, 1), (2, 4)]),
    frozenset([(3, 1), (2, 3), (2, 1)]),
    frozenset([(3, 1), (4, 1), (2, 4), (2, 1)]),
    frozenset([(2, 3), (3, 1), (4, 1), (2, 4), (2, 1)]),
    frozenset([(3, 2), (3, 1), (4, 1), (2, 1)])
])


def make_voweldset():
    data = {
        'constraints': ['c1', 'c2', 'c3', 'c4'],
        'candidates': ot.data.voweldset,
        'name': 'voweldset'
    }
    dset = Dataset(data=data, data_is_from_form=False)
    dset.save()
    mod['dset'] = dset
    mod['data'] = data


def make_cv_dset():
    data = ot.data.cv_dset
    data['name'] = 'cv_dset'
    dset = Dataset(data=data, data_is_from_form=False)
    dset.save()
    mod['dset'] = dset
    mod['data'] = data['candidates']


def blank_guest_dset():
    Dataset(name='blank', user='guest').save()


@with_setup(make_voweldset, delete_bad_datasets)
@mock.patch('ot.poot.PoOT.get_grammars', return_value=voweldset_grammars)
def test_calculate_global_stats(mock_get_grammars):
    dset = mod['dset']
    assert not dset.global_stats
    global_stats = {
        u'num_total_poots': 219,
        u'num_total_cots': 24,
        u'grams': u'[(10, frozenset([(3, 1), (2, 1)]))]',
        u'percent_cots': 0.0,
        u'num_poots': 11,
        u'num_cots': 0,
        u'percent_poots': 5.0228310502283104
    }
    _calculate_grammars_and_statistics('voweldset', 8, False,
                                       0, 'guest', 'rank_volume')
    assert mock_get_grammars.called_with(False)
    dset = Dataset.objects.get(name='voweldset')
    assert dset.global_stats == global_stats


@with_setup(make_cv_dset, delete_bad_datasets)
@mock.patch('ot.poot.PoOT.get_grammars', return_value=cv_grammars)
def test_calculate_global_stats_classical(mock_get_grammars):
    dset = mod['dset']
    assert not dset.global_stats
    global_stats = {
        u'num_total_cots': 24,
        u'num_cots': 6,
        u'grams':
        (u'['
         '(0, frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 1), (2, 4)])), '
         '(1, frozenset([(3, 2), (3, 1), (2, 1), (4, 3), (4, 2), (4, 1)])), '
         '(2, frozenset([(1, 2), (3, 2), (3, 1), (4, 3), (4, 2), (4, 1)])), '
         '(3, frozenset([(1, 2), (3, 2), (1, 3), (4, 3), (4, 2), (4, 1)])), '
         '(4, frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 2), (4, 1)])), '
         '(5, frozenset([(1, 2), (3, 2), (3, 4), (3, 1), (4, 2), (4, 1)]))]'),
        u'percent_cots': 25.0
    }
    _calculate_grammars_and_statistics('cv_dset', 1, True, 0, 'guest',
                                       'rank_volume')
    assert mock_get_grammars.called_with(True)
    dset = Dataset.objects.get(name='cv_dset')
    assert dset.global_stats == global_stats


@with_setup(make_cv_dset, delete_bad_datasets)
@mock.patch('ot.poot.PoOT.get_grammars', return_value=cv_grammars)
def test_calculate_global_stats_classical_sort_by_size(mock_get_grammars):
    dset = mod['dset']
    assert not dset.global_stats
    global_stats = {
        u'num_total_cots': 24,
        u'num_cots': 6,
        u'grams':
        (u'['
         '(0, frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 1), (2, 4)])), '
         '(1, frozenset([(3, 2), (3, 1), (2, 1), (4, 3), (4, 2), (4, 1)])), '
         '(2, frozenset([(1, 2), (3, 2), (3, 1), (4, 3), (4, 2), (4, 1)])), '
         '(3, frozenset([(1, 2), (3, 2), (1, 3), (4, 3), (4, 2), (4, 1)])), '
         '(4, frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 2), (4, 1)])), '
         '(5, frozenset([(1, 2), (3, 2), (3, 4), (3, 1), (4, 2), (4, 1)]))]'),
        u'percent_cots': 25.0
    }
    _calculate_grammars_and_statistics('cv_dset', 6, True, 0, 'guest', 'size')
    assert mock_get_grammars.called_with(True)
    dset = Dataset.objects.get(name='cv_dset')
    assert dset.global_stats == global_stats


@with_setup(make_cv_dset, delete_bad_datasets)
@mock.patch('ot.poot.PoOT.get_grammars', return_value=cv_grammars)
def test_calculate_global_stats_adjust_grams_per_page(mock_get_grammars):
    dset = mod['dset']
    assert not dset.global_stats
    grams_per_page = worker_jobs.GRAMS_PER_PAGE
    worker_jobs.GRAMS_PER_PAGE = 5
    _calculate_grammars_and_statistics('cv_dset', 1, True, 0, 'guest',
                                       'rank_volume')
    assert mock_get_grammars.called_with(True)
    worker_jobs.GRAMS_PER_PAGE = grams_per_page
    dset = Dataset.objects.get(name='cv_dset')
    assert len(eval(dset.global_stats['grams'])) == 5


@with_setup(blank_guest_dset, delete_bad_datasets)
@mock.patch('rankomatic.models.Dataset.visualize_and_store_entailments')
@mock.patch('rankomatic.models.Dataset.calculate_entailments')
def test_enqueued_calculate_entailments(mock_calculate, mock_visualize):
    username = 'guest'
    dset_name = 'blank'
    _calculate_entailments(dset_name, username)
    assert mock_calculate.called
    assert mock_visualize.called


@with_setup(make_voweldset, delete_bad_datasets)
@mock.patch('ot.poot.PoOT.get_grammars', return_value=voweldset_grammars)
def test_make_grammar_info(mock_get_grammars):
    grammar_info = [
        {
            u'cots_by_cand': {
                u'lasi-a': [
                    {u'output': u'la-si-a', u'num_cot': 5, u'per_cot': 62.5},
                    {u'output': u'la-sii', u'num_cot': 3, u'per_cot': 37.5}
                ],
                u'ovea': [
                    {u'output': u'o-ve-a', u'num_cot': 4, u'per_cot': 50.0},
                    {u'output': u'o-vee', u'num_cot': 4, u'per_cot': 50.0}
                ],
                u'rasia': [
                    {u'output': u'ra-si-a', u'num_cot': 8, u'per_cot': 100.0},
                    {u'output': u'ra-sii', u'num_cot': 0, u'per_cot': 0.0}
                ],
                u'idea': [
                    {u'output': u'i-de-a', u'num_cot': 8, u'per_cot': 100.0},
                    {u'output': u'i-dee', u'num_cot': 0, u'per_cot': 0.0}
                ]
            },
            u'grammar': u'{(c1, c3), (c1, c2)}',
            u'apriori': u'[["c1", "c3"], ["c1", "c2"]]',
            u'input_totals': {
                u'idea': {u'raw_sum': 8, u'per_sum': 100.0},
                u'lasi-a': {u'raw_sum': 8, u'per_sum': 100.0},
                u'rasia': {u'raw_sum': 8, u'per_sum': 100.0},
                u'ovea': {u'raw_sum': 8, u'per_sum': 100.0}
            },
            u'filename': u'grammar10.png'}]
    _calculate_grammars_and_statistics('voweldset', 8, False, 0, 'guest',
                                       'rank_volume')
    info_maker = GrammarInfoMaker('voweldset', 'guest')
    info_maker.make_grammar_info()
    dset = Dataset.objects.get(name='voweldset')
    assert dset.grammar_info == grammar_info


class TestEnqueuingFunctions(OTOrderBaseCase):

    def make_request(self, func, args):
        return json.dumps({
            'request': 'calculate',
            'func': func,
            'args': args
        })

    @mock.patch('Queue.Queue.put')
    @mock.patch('rankomatic.worker_jobs.get_queue', return_value=Queue())
    def test_calculate_grammars_and_statistics(self, mock_get_queue, mock_put):
        path = "/?classical=False&page=0&sort_by=size"
        with self.app.test_request_context(path=path):
            calculate_grammars_and_statistics('blank', 0)
        assert mock_get_queue.called
        mock_put.assert_called_with(
            self.make_request('calculate_grammars_and_statistics',
                              ('blank', 0, False, 0, 'guest', 'size'))
        )

    @mock.patch('Queue.Queue.put')
    @mock.patch('rankomatic.worker_jobs.get_queue', return_value=Queue())
    def test_calculate_entailments(self, mock_get_queue, mock_put):
        with self.app.test_request_context():
            calculate_entailments('blank')
        assert mock_get_queue.called
        mock_put.assert_called_with(self.make_request(
            'calculate_entailments', ('blank', 'guest')
        ))

    @mock.patch('Queue.Queue.put')
    @mock.patch('rankomatic.worker_jobs.get_queue', return_value=Queue())
    def test_make_grammar_info(self, mock_get_queue, mock_put):
        with self.app.test_request_context():
            make_grammar_info('blank')
        assert mock_get_queue.called
        mock_put.assert_called_with(self.make_request(
            'make_grammar_info', ('blank', 'guest')
        ))
