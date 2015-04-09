import mock
import gridfs
from copy import deepcopy
from nose.tools import raises

import ot.data
import test.structures.structures as structures
from rankomatic import models, db
from test.test_tools import delete_bad_datasets
from rankomatic.models.grammar import GrammarList


class TestDataset(object):

    def setUp(self):
        self.data = {
            'constraints': ['c1', 'c2', 'c3', 'c4'],
            'candidates': ot.data.voweldset,
            'name': 'voweldset',
            'apriori_ranking': [['c1', 'c2']]
        }
        self.d = models.Dataset(data=self.data, data_is_from_form=False)
        self.d.classical = False
        self.entailments_fname = "".join([self.d.name, "/", 'entailments.png'])
        self.grammar_format_str = self.d.name + "/grammar%d.png"
        self.fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')

    def tearDown(self):
        pymongodb = db.get_pymongo_db()
        pymongodb.tmp.files.drop()
        pymongodb.tmp.chunks.drop()
        delete_bad_datasets()

    def test_bare_constructor(self):
        d = models.Dataset()
        assert d.upload_date
        assert not d.name
        assert len(d.constraints) == 3
        assert not d.candidates
        assert not d.global_entailments
        assert not d.apriori_entailments
        assert not d.grammars
        assert not d.apriori_ranking.list_grammar
        assert d.poot
        assert d.user == "guest"

    def test_constructor_no_data_not_from_form(self):
        d = models.Dataset(data_is_from_form=False)
        assert d.upload_date
        assert not d.name
        assert len(d.constraints) == 3
        assert not d.candidates
        assert not d.global_entailments
        assert not d.apriori_entailments
        assert not d.grammars
        assert d.apriori_ranking.list_grammar == []
        assert d.poot
        assert d.user == "guest"

    def test_constructor_data_not_from_form(self):
        assert self.candidates_are_set_correctly(self.d, self.data)
        assert self.d.user == "guest"
        assert self.d.name == "voweldset"
        assert self.d.apriori_ranking.list_grammar == [['c1', 'c2']]

    def test_constructor_data_from_form(self):
        form_data = self.d.create_form_data()
        form_dset = models.Dataset(data=form_data)
        assert self.candidates_are_set_correctly(form_dset, self.data)
        assert form_dset.name == self.data['name']
        assert form_dset.apriori_ranking.list_grammar == [['c1', 'c2']]

    def test_save_and_retrieve_apriori(self):
        self.d.save()
        new_dset = models.Dataset.objects.get(name=self.d.name,
                                              user=self.d.user)
        assert new_dset.apriori_ranking
        assert new_dset.apriori_ranking.list_grammar == [['c1', 'c2']]
        apriori_dset = new_dset.apriori_ranking.dset
        assert apriori_dset.name == self.d.name
        assert apriori_dset.user == self.d.user

    def test_create_form_data(self):
        form_data = self.d.create_form_data()
        assert form_data == {
            'name': 'voweldset',
            'constraints': ['c1', 'c2', 'c3', 'c4'],
            'input_groups': [
                {'candidates': [
                    {
                        'input': 'ovea',
                        'output': 'o-ve-a',
                        'violation_vector': [0, 1, 1, 0],
                        'optimal': True
                    },
                    {
                        'input': 'ovea',
                        'output': 'o-vee',
                        'violation_vector': [0, 0, 0, 1],
                        'optimal': True
                    }
                ]},
                {'candidates': [
                    {
                        'input': 'idea',
                        'output': 'i-de-a',
                        'violation_vector': [0, 1, 1, 0],
                        'optimal': True
                    },
                    {
                        'input': 'idea',
                        'output': 'i-dee',
                        'violation_vector': [1, 0, 0, 1],
                        'optimal': False
                    }
                ]},
                {'candidates': [
                    {
                        'input': 'lasi-a',
                        'output': 'la-si-a',
                        'violation_vector': [0, 0, 1, 0],
                        'optimal': True
                    },
                    {
                        'input': 'lasi-a',
                        'output': 'la-sii',
                        'violation_vector': [0, 0, 0, 1],
                        'optimal': True
                    }
                ]},
                {'candidates': [
                    {
                        'input': 'rasia',
                        'output': 'ra-si-a',
                        'violation_vector': [0, 0, 1, 0],
                        'optimal': True
                    },
                    {
                        'input': 'rasia',
                        'output': 'ra-sii',
                        'violation_vector': [1, 0, 0, 1],
                        'optimal': False
                    }
                ]}
            ],
            'apriori_ranking': '[["c1", "c2"]]'
        }

    def test_raw_grammars(self):
        self.d.apriori_ranking = []
        self.d.sort_by = 'size'
        # calculate once
        assert self.d.raw_grammars == [
            frozenset([(3, 1), (2, 1)]),
            frozenset([(3, 1), (2, 4)]),
            frozenset([(3, 2), (3, 1), (2, 1)]),
            frozenset([(3, 1), (2, 4), (2, 1)]),
            frozenset([(3, 1), (4, 1), (2, 1)]),
            frozenset([(3, 1), (2, 3), (2, 1)]),
            frozenset([(3, 1), (2, 3), (2, 4), (2, 1)]),
            frozenset([(2, 3), (3, 1), (4, 1), (2, 1)]),
            frozenset([(3, 1), (4, 1), (2, 4), (2, 1)]),
            frozenset([(3, 2), (3, 1), (4, 1), (2, 1)]),
            frozenset([(2, 3), (3, 1), (4, 1), (2, 4), (2, 1)])
        ]

        # recalculate cached
        assert self.d.raw_grammars == [
            frozenset([(3, 1), (2, 1)]),
            frozenset([(3, 1), (2, 4)]),
            frozenset([(3, 2), (3, 1), (2, 1)]),
            frozenset([(3, 1), (2, 4), (2, 1)]),
            frozenset([(3, 1), (4, 1), (2, 1)]),
            frozenset([(3, 1), (2, 3), (2, 1)]),
            frozenset([(3, 1), (2, 3), (2, 4), (2, 1)]),
            frozenset([(2, 3), (3, 1), (4, 1), (2, 1)]),
            frozenset([(3, 1), (4, 1), (2, 4), (2, 1)]),
            frozenset([(3, 2), (3, 1), (4, 1), (2, 1)]),
            frozenset([(2, 3), (3, 1), (4, 1), (2, 4), (2, 1)])
        ]

        # get from grammar strings
        self.d.grammars = None
        assert self.d.raw_grammars == [
            frozenset([(3, 1), (2, 1)]),
            frozenset([(3, 1), (2, 4)]),
            frozenset([(3, 2), (3, 1), (2, 1)]),
            frozenset([(3, 1), (2, 4), (2, 1)]),
            frozenset([(3, 1), (4, 1), (2, 1)]),
            frozenset([(3, 1), (2, 3), (2, 1)]),
            frozenset([(3, 1), (2, 3), (2, 4), (2, 1)]),
            frozenset([(2, 3), (3, 1), (4, 1), (2, 1)]),
            frozenset([(3, 1), (4, 1), (2, 4), (2, 1)]),
            frozenset([(3, 2), (3, 1), (4, 1), (2, 1)]),
            frozenset([(2, 3), (3, 1), (4, 1), (2, 4), (2, 1)])
        ]

    def candidates_are_set_correctly(self, dataset, ot_dset):
        num_set = 0
        for c in ot_dset['candidates']:
            source_cand = models.candidate.Candidate(data=c)
            for dest_cand in dataset.candidates:
                if source_cand == dest_cand:
                    num_set += 1
        return num_set == len(ot_dset['candidates'])

    def test_process_form_data(self):
        data = {
            'name': 'voweldset',
            'candidates': ot.data.voweldset,
            'constraints': ['c1', 'c2', 'c3', 'c4'],
            'apriori_ranking': [['c1', 'c2']]
        }
        d = models.Dataset(data=data, data_is_from_form=False)
        form_data = d.create_form_data()
        ot_data = models.Dataset().process_form_data(form_data)
        assert ot_data == data

    def test_calculate_compatible_grammars(self):
        # classical by default
        data = {
            'constraints': ['C1', 'C2', 'C3'],
            'candidates': [
                {
                    'input': 'a',
                    'output': 'b',
                    'optimal': True,
                    'violation_vector': {1: 1, 2: 0, 3: 1}
                },
                {
                    'input': 'a',
                    'output': 'c',
                    'optimal': False,
                    'violation_vector': {1: 0, 2: 1, 3: 0}
                }
            ],
            'name': 'blank'
        }
        grams = [
            frozenset([(1, 2), (3, 2), (1, 3)]),
            frozenset([(1, 2), (3, 2), (3, 1)]),
            frozenset([(1, 2), (3, 2)])
        ]
        apriori_data = deepcopy(data)
        apriori_data.update({'apriori_ranking': [('C3', 'C1')]})
        apriori_grams = [grams[0]]
        yield self.check_calculate_compatible_grammars, data, grams
        yield (self.check_calculate_compatible_grammars,
               apriori_data, apriori_grams)

    def check_calculate_compatible_grammars(self, data, grams):
        d = models.Dataset(data=data, data_is_from_form=False)
        d.calculate_compatible_grammars()
        assert d.raw_grammars == grams

    compatible_poot_grammars = set([
        frozenset([(3, 1), (2, 3), (2, 4), (2, 1)]),
        frozenset([(3, 2), (3, 1), (2, 1)]),
        frozenset([(3, 1), (2, 4), (2, 1)]),
        frozenset([(4, 1), (3, 1), (2, 3), (2, 1)]),
        frozenset([(3, 1), (2, 1)]),
        frozenset([(3, 1), (4, 1), (2, 1)]), frozenset([(3, 1), (2, 4)]),
        frozenset([(3, 1), (2, 3), (2, 1)]),
        frozenset([(3, 1), (4, 1), (2, 4), (2, 1)]),
        frozenset([(4, 1), (3, 1), (2, 3), (2, 4), (2, 1)]),
        frozenset([(3, 2), (3, 1), (4, 1), (2, 1)])
    ])

    @mock.patch('ot.poot.PoOT.get_grammars',
                return_value=compatible_poot_grammars)
    def test_calculate_compatible_poot_grammars(self, mock_get_grammars):
        self.d.sort_by = 'size'
        self.d.calculate_compatible_grammars()
        for gram_string in [gram.string for gram in self.d.grammars]:
            assert gram_string in structures.compatible_poot_grammars
        assert len(structures.compatible_poot_grammars) == len(self.d.grammars)
        assert mock_get_grammars.called_with(False)

    def test_calculate_compatible_grammars_no_grammars(self):
        self.data['candidates'] = ot.data.no_rankings
        self.d = models.Dataset(self.data, False)
        self.d.calculate_compatible_grammars()
        assert self.d.grammars == []

    def test_grammar_to_string(self):
        self.d.sort_by = 'size'
        self.d.calculate_compatible_grammars()
        gram_str = self.d.grammar_to_string(0)
        assert gram_str == '{(c1, c3), (c1, c2)}'

    def test_grammar_to_json(self):
        self.d.sort_by = 'size'
        self.d.calculate_compatible_grammars()
        gram_str = self.d.grammar_to_json(0)
        assert gram_str == '[["c1", "c3"], ["c1", "c2"]]'

    def test_grammar_to_string_empty_grammar(self):
        data = {
            'name': 'blank',
            'constraints': ['c1', 'c2', 'c3'],
            'candidates': [
                {
                    'input': 'a',
                    'output': 'b',
                    'optimal': True,
                    'violation_vector': {1: 0, 2: 0, 3: 0}
                },
                {
                    'input': 'a',
                    'output': 'c',
                    'optimal': False,
                    'violation_vector': {1: 1, 2: 1, 3: 1}
                }
            ]
        }
        d = models.Dataset(data=data, data_is_from_form=False)
        d.calculate_compatible_grammars()
        gram_str = d.grammar_to_string(-1)
        assert gram_str == "{ }"

    def test_calculate_entailments(self):
        self.d.apriori_ranking = []
        self.d.calculate_entailments()
        assert self.d.apriori_entailments == {}
        assert self.d.global_entailments == structures.global_entailments

        # recalculate for coverage
        self.d.calculate_entailments()
        assert self.d.global_entailments == structures.global_entailments

    def test_calculate_entailments_with_apriori(self):
        self.d.calculate_entailments()
        assert self.d.global_entailments == structures.global_entailments
        apriori_entailments = {
            'rasia, ra-si-a': ['idea, i-de-a'],
            'lasi-a, la-si-a': ['idea, i-de-a'],
            'idea, i-dee': ['lasi-a, la-sii', 'rasia, ra-sii']
        }
        assert self.d.apriori_entailments == apriori_entailments
        for entails, entaileds in self.d.apriori_entailments.iteritems():
            for entailed in entaileds:
                assert entailed not in self.d.global_entailments[entails]

    @raises(gridfs.NoFile)
    def test_visualize_and_store_entailments_no_entailments(self):
        data = {
            'constraints': ['c1', 'c2', 'c3'],
            'candidates': [{
                'input': 'a',
                'output': 'b',
                'violation_vector': {1: 0, 2: 0, 3: 0},
                'optimal': True
            }],
            'name': 'blank'
        }
        self.d = models.Dataset(data=data, data_is_from_form=False)
        self.d.calculate_entailments()
        self.d.visualize_and_store_entailments()
        self.fs.get_last_version(filename=self.entailments_fname)

    def test_visualize_and_store_entailments_with_entailments(self):
        self.d.calculate_entailments()
        self.d.visualize_and_store_entailments()
        assert self.fs.get_last_version(filename=self.entailments_fname)

        self.d.visualize_and_store_entailments()
        assert self.fs.get_last_version(filename=self.entailments_fname)

    @raises(gridfs.NoFile)
    def test_visualize_and_store_grammars_no_indices_cot(self):
        self.d.calculate_compatible_grammars()
        self.d.visualize_and_store_grammars([])
        self.fs.get_last_version(filename=(self.grammar_format_str % 0))

    @raises(gridfs.NoFile)
    def test_visualize_and_store_grammars_no_indices_poot(self):
        self.d.calculate_compatible_grammars()
        self.d.visualize_and_store_grammars([])
        self.fs.get_last_version(filename=(self.grammar_format_str % 0))

    lat4 = set([
        frozenset([(4, 2), (1, 3), (4, 3)]), frozenset([(1, 2), (3, 2), (3, 1), (3, 4), (1, 4)]), frozenset([(3, 1), (2, 1), (2, 3), (4, 3), (4, 2), (4, 1)]), frozenset([(3, 1), (3, 4), (2, 1)]), frozenset([(4, 2), (3, 1), (4, 1), (2, 1)]), frozenset([(1, 2), (4, 3)]), frozenset([(3, 1), (4, 1), (2, 4), (2, 1)]), frozenset([(3, 1), (3, 4), (2, 4), (2, 1)]), frozenset([(2, 3), (4, 2), (4, 1), (2, 1), (4, 3)]), frozenset([(1, 3), (2, 1), (2, 3), (4, 3), (4, 2), (4, 1)]), frozenset([(1, 2), (1, 3), (1, 4), (4, 3)]), frozenset([(1, 2), (1, 3), (1, 4), (2, 3), (4, 3), (4, 2)]), frozenset([(3, 1), (4, 1), (4, 3)]), frozenset([(3, 4), (1, 4)]), frozenset([(1, 3)]), frozenset([(2, 3), (3, 4), (2, 1), (1, 4), (2, 4)]), frozenset([(1, 2), (4, 2), (1, 3), (1, 4)]), frozenset([(3, 1), (2, 1)]), frozenset([(1, 3), (2, 3), (1, 4), (4, 3), (2, 4)]), frozenset([(1, 2), (4, 2), (1, 3), (2, 3), (4, 3)]), frozenset([(1, 2), (2, 4), (1, 4)]), frozenset([(4, 2), (3, 2), (3, 1)]), frozenset([(2, 3), (2, 1), (1, 4), (2, 4)]), frozenset([(2, 3), (4, 1), (2, 1), (4, 3)]), frozenset([(1, 2), (4, 2), (1, 3), (1, 4), (4, 3)]), frozenset([(1, 2), (3, 2), (1, 3)]), frozenset([(1, 2), (3, 2), (1, 3), (1, 4), (3, 4), (2, 4)]), frozenset([(4, 1)]), frozenset([(1, 2), (3, 2), (3, 1), (4, 3), (4, 2), (4, 1)]), frozenset([(4, 2)]), frozenset([(1, 3), (2, 4)]), frozenset([(2, 3), (1, 3), (4, 1), (2, 1), (4, 3)]), frozenset([(1, 3), (2, 3), (2, 1), (1, 4), (2, 4)]), frozenset([(1, 2), (1, 3), (2, 3), (1, 4), (4, 3)]), frozenset([(2, 3), (4, 2), (4, 1), (4, 3)]), frozenset([(4, 2), (3, 1), (4, 1), (2, 1), (4, 3)]), frozenset([(2, 1), (1, 4), (2, 4)]), frozenset([(1, 2), (4, 2)]), frozenset([(1, 3), (2, 1), (2, 3), (4, 3), (4, 1), (2, 4)]), frozenset([(2, 4), (1, 4)]), frozenset([(3, 4), (2, 4), (1, 4)]), frozenset([(1, 2), (3, 4)]), frozenset([(2, 3), (2, 4)]), frozenset([(3, 1), (2, 1), (2, 3), (1, 4), (3, 4), (2, 4)]), frozenset([(1, 2), (4, 2), (3, 2), (1, 4)]), frozenset([(4, 2), (4, 1)]), frozenset([(3, 2)]), frozenset([(3, 4), (4, 2), (3, 2), (3, 1), (4, 1)]), frozenset([(1, 2), (4, 2), (3, 2), (4, 1)]), frozenset([(1, 3), (2, 3), (4, 3)]), frozenset([(1, 2), (4, 2), (3, 2)]), frozenset([(4, 2), (1, 3), (2, 3), (4, 3)]), frozenset([(2, 1), (4, 3)]), frozenset([(4, 2), (4, 1), (2, 1), (4, 3)]), frozenset([(4, 2), (3, 1), (4, 1)]), frozenset([(3, 2), (3, 1), (3, 4), (2, 4), (1, 4)]), frozenset([(3, 1), (2, 3), (2, 1)]), frozenset([(1, 2), (4, 2), (3, 2), (3, 1), (3, 4)]), frozenset([(1, 2), (3, 2), (3, 4)]), frozenset([(1, 2), (1, 3), (2, 3), (2, 4), (1, 4)]), frozenset([(2, 4)]), frozenset([(3, 2), (3, 1), (4, 1)]), frozenset([(4, 2), (1, 3)]), frozenset([(1, 2), (3, 2), (3, 1), (1, 4), (4, 2), (3, 4)]), frozenset([(3, 4), (2, 4), (2, 1)]), frozenset([(1, 2), (4, 2), (4, 1)]), frozenset([(1, 2), (3, 2), (3, 4), (2, 4), (1, 4)]), frozenset([(4, 2), (3, 2)]), frozenset([(4, 2), (4, 1), (2, 1)]), frozenset([(3, 4), (2, 1), (1, 4), (2, 4)]), frozenset([(2, 4), (2, 1)]), frozenset([(2, 3), (1, 4)]), frozenset([(3, 2), (3, 1), (4, 1), (2, 1)]), frozenset([(3, 1), (3, 4), (2, 1), (1, 4), (2, 4)]), frozenset([(2, 3), (3, 1), (3, 4), (2, 4), (2, 1)]), frozenset([(2, 3), (2, 4), (1, 4)]), frozenset([(3, 1), (3, 4)]), frozenset([(2, 3), (3, 4), (2, 4), (2, 1)]), frozenset([(4, 1), (2, 1), (4, 3)]), frozenset([(1, 2)]), frozenset([(3, 2), (3, 4), (2, 4)]), frozenset([(4, 1), (4, 3)]), frozenset([(4, 1), (3, 1), (3, 4), (2, 1)]), frozenset([(1, 2), (4, 2), (1, 3)]), frozenset([(4, 2), (4, 3)]), frozenset([(1, 3), (2, 3), (2, 4), (4, 3)]), frozenset([(1, 2), (1, 3), (1, 4), (2, 3), (4, 3), (2, 4)]), frozenset([(3, 4), (3, 2), (3, 1), (4, 1), (2, 1)]), frozenset([(4, 1), (2, 1)]), frozenset([(1, 2), (1, 3), (2, 3), (4, 3), (4, 2), (4, 1)]), frozenset([(1, 3), (2, 3), (1, 4), (4, 3)]), frozenset([(1, 2), (1, 3), (2, 4), (1, 4)]), frozenset([(1, 2), (1, 3), (4, 3)]), frozenset([(2, 3), (4, 1), (2, 1), (4, 3), (2, 4)]),
        frozenset([(4, 1), (3, 1), (2, 3), (2, 1)]), frozenset([(3, 2), (3, 4), (1, 4)]), frozenset([(2, 1)]), frozenset([(4, 2), (3, 1), (4, 1), (4, 3)]), frozenset([(4, 2), (3, 2), (4, 1), (4, 3)]), frozenset([(2, 3), (2, 1), (4, 3)]), frozenset([(4, 2), (3, 2), (3, 1), (4, 1), (4, 3)]), frozenset([(3, 4), (2, 4)]), frozenset([(3, 2), (3, 4), (2, 4), (1, 4)]), frozenset([(4, 1), (3, 1), (2, 3), (2, 4), (2, 1)]), frozenset([(1, 2), (1, 4)]), frozenset([(4, 2), (3, 2), (3, 4)]), frozenset([(4, 2), (3, 2), (3, 1), (4, 1)]), frozenset([(2, 3)]), frozenset([(1, 2), (4, 2), (4, 3)]), frozenset([(3, 2), (3, 1), (2, 1), (4, 3), (4, 2), (4, 1)]), frozenset([(1, 3), (4, 3)]), frozenset([(1, 4)]), frozenset([(2, 3), (3, 4), (2, 4), (1, 4)]), frozenset([(1, 2), (3, 2), (3, 1)]), frozenset([(4, 2), (3, 1)]), frozenset([(1, 2), (3, 2), (3, 4), (3, 1), (4, 2), (4, 1)]),
        frozenset([(3, 2), (3, 1), (3, 4), (1, 4)]), frozenset([(1, 3), (2, 3)]), frozenset([(4, 2), (2, 3), (4, 3)]), frozenset([(1, 2), (4, 2), (3, 2), (1, 3)]), frozenset([(2, 3), (2, 1), (4, 3), (2, 4)]), frozenset([(3, 2), (3, 4)]), frozenset([(2, 3), (2, 1)]), frozenset([(1, 2), (3, 4), (1, 4)]), frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 1), (2, 4)]), frozenset([(1, 3), (2, 3), (2, 4)]), frozenset([(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (2, 4)]), frozenset([(3, 1), (4, 1), (2, 1), (4, 3)]), frozenset([(4, 2), (1, 3), (4, 1), (4, 3)]), frozenset([(3, 1), (2, 3), (2, 4), (2, 1)]), frozenset([(1, 3), (3, 4), (2, 4), (1, 4)]), frozenset([(4, 2), (3, 2), (3, 1), (4, 1), (2, 1)]), frozenset([(2, 3), (3, 1), (4, 1), (2, 1), (4, 3)]), frozenset([(1, 2), (4, 2), (3, 2), (1, 3), (4, 3)]), frozenset([(3, 1), (4, 1), (2, 1)]), frozenset([(4, 1), (3, 1), (3, 4)]), frozenset([(3, 2), (3, 1), (3, 4), (2, 4), (2, 1)]), frozenset([(4, 2), (3, 2), (4, 3)]), frozenset([(1, 2), (4, 2), (3, 2), (3, 1), (4, 1)]), frozenset([(3, 2), (3, 1), (2, 1)]), frozenset([(1, 2), (3, 2), (1, 4)]), frozenset([(2, 3), (1, 3), (4, 1), (4, 3)]), frozenset([(3, 1), (3, 4), (2, 4), (1, 4)]), frozenset([(3, 4), (2, 1)]), frozenset([(1, 3), (1, 4), (4, 3)]), frozenset([(1, 2), (4, 2), (3, 2), (1, 3), (1, 4)]), frozenset([(1, 3), (2, 1), (2, 3), (1, 4), (4, 3), (2, 4)]),
        frozenset([(1, 2), (3, 2), (1, 3), (1, 4)]), frozenset([(3, 2), (3, 1), (2, 1), (1, 4), (3, 4), (2, 4)]), frozenset([(1, 2), (4, 2), (3, 2), (4, 3)]), frozenset([(1, 2), (1, 3)]), frozenset([(1, 3), (2, 3), (2, 1), (4, 3), (2, 4)]), frozenset([(4, 1), (3, 1), (3, 4), (2, 4), (2, 1)]), frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 2), (4, 1)]), frozenset([(2, 3), (3, 4), (2, 4)]), frozenset([(2, 3), (4, 2), (1, 3), (4, 1), (4, 3)]), frozenset([(1, 2), (4, 2), (3, 2), (3, 1)]), frozenset([(1, 2), (4, 2), (1, 3), (4, 1), (4, 3)]), frozenset([(2, 3), (2, 4), (2, 1)]), frozenset([(4, 2), (3, 2), (3, 1), (3, 4)]), frozenset([(4, 1), (2, 3), (2, 4), (2, 1)]), frozenset([(4, 1), (2, 3)]), frozenset([(3, 4)]), frozenset([]), frozenset([(1, 2), (3, 2), (1, 3), (1, 4), (4, 3), (4, 2)]), frozenset([(1, 2), (3, 2)]), frozenset([(1, 3), (4, 1), (4, 3)]), frozenset([(1, 3), (2, 3), (2, 1), (4, 3)]), frozenset([(1, 3), (2, 4), (1, 4)]), frozenset([(1, 3), (1, 4)]), frozenset([(1, 2), (3, 2), (3, 4), (1, 4)]), frozenset([(1, 2), (4, 2), (4, 1), (4, 3)]), frozenset([(4, 2), (3, 2), (4, 1)]), frozenset([(1, 3), (3, 4), (1, 4)]), frozenset([(1, 3), (2, 3), (2, 1)]), frozenset([(3, 2), (3, 1)]), frozenset([(3, 1)]), frozenset([(1, 2), (3, 2), (3, 1), (3, 4)]), frozenset([(1, 2), (1, 3), (3, 4), (1, 4)]), frozenset([(4, 1), (3, 1), (2, 1), (2, 3), (3, 4), (2, 4)]), frozenset([(1, 2), (1, 3), (2, 3)]), frozenset([(2, 3), (4, 3)]), frozenset([(3, 1), (3, 4), (1, 4)]), frozenset([(1, 3), (2, 3), (2, 4), (1, 4)]), frozenset([(1, 2), (3, 2), (1, 3), (3, 4), (1, 4)]), frozenset([(1, 2), (4, 2), (3, 2), (3, 4)]), frozenset([(1, 3), (2, 1), (2, 3), (1, 4), (3, 4), (2, 4)]), frozenset([(1, 2), (1, 3), (2, 3), (4, 3)]),
        frozenset([(3, 1), (2, 4), (2, 1)]), frozenset([(1, 2), (1, 3), (1, 4)]), frozenset([(3, 1), (2, 4)]), frozenset([(4, 1), (2, 3), (2, 1)]), frozenset([(3, 1), (4, 1)]), frozenset([(1, 3), (2, 3), (2, 4), (2, 1)]), frozenset([(1, 2), (4, 2), (3, 2), (4, 1), (4, 3)]), frozenset([(1, 2), (3, 2), (1, 3), (4, 3), (4, 2), (4, 1)]), frozenset([(2, 3), (1, 3), (3, 4), (2, 4), (1, 4)]), frozenset([(2, 3), (2, 4), (4, 3)]), frozenset([(3, 4), (3, 2), (3, 1), (4, 1)]), frozenset([(3, 2), (3, 1), (3, 4), (2, 1)]), frozenset([(4, 2), (4, 1), (4, 3)]), frozenset([(3, 2), (3, 1), (3, 4)]), frozenset([(3, 1), (2, 1), (2, 3), (4, 3), (4, 1), (2, 4)]), frozenset([(3, 2), (1, 4)]), frozenset([(4, 1), (2, 4), (2, 1)]), frozenset([(1, 3), (2, 3), (1, 4)]), frozenset([(3, 2), (4, 1)]), frozenset([(1, 2), (4, 2), (1, 3), (4, 3)]), frozenset([(1, 2), (3, 4), (2, 4), (1, 4)]), frozenset([(1, 2), (4, 2), (1, 4)]), frozenset([(1, 2), (3, 2), (3, 1), (1, 4), (3, 4), (2, 4)]), frozenset([(1, 2), (1, 3), (3, 4), (2, 4), (1, 4)]), frozenset([(3, 2), (3, 1), (3, 4), (2, 4)]), frozenset([(2, 3), (4, 1), (4, 3)]), frozenset([(1, 2), (1, 3), (2, 3), (1, 4)]), frozenset([(4, 3)]), frozenset([(1, 2), (4, 2), (3, 2), (3, 4), (1, 4)]), frozenset([(1, 2), (3, 2), (1, 3), (1, 4), (4, 2), (3, 4)]), frozenset([(3, 1), (3, 4), (2, 4)])
    ])

    @mock.patch('ot.poot.PoOT.get_grammars', return_value=lat4)
    def test_visualize_and_store_grammars_cot(self, mock_get_grammars):
        self.data['candidates'] = ot.data.hbounded
        self.d.set_dset(self.data)
        self.d.poot = self.d.build_poot()
        self.d.calculate_compatible_grammars()
        assert mock_get_grammars.called_with(False)
        self.d.visualize_and_store_grammars(range(5))
        for i in range(5):
            assert self.fs.get_last_version(filename=(
                self.grammar_format_str % i))

    visualized_poot_grammars = set([
        frozenset([(3, 1), (2, 3), (2, 4), (2, 1)]),
        frozenset([(3, 2), (3, 1), (2, 1)]),
        frozenset([(3, 1), (2, 4), (2, 1)]),
        frozenset([(4, 1), (3, 1), (2, 3), (2, 1)]),
        frozenset([(3, 1), (2, 1)]), frozenset([(3, 1), (4, 1), (2, 1)]),
        frozenset([(3, 1), (2, 4)]), frozenset([(3, 1), (2, 3), (2, 1)]),
        frozenset([(3, 1), (4, 1), (2, 4), (2, 1)]),
        frozenset([(4, 1), (3, 1), (2, 3), (2, 4), (2, 1)]),
        frozenset([(3, 2), (3, 1), (4, 1), (2, 1)])
    ])

    @mock.patch('ot.poot.PoOT.get_grammars',
                return_value=visualized_poot_grammars)
    def test_visualize_and_store_grammars_poot(self, mock_get_grammars):
        self.d.calculate_compatible_grammars()
        self.d.visualize_and_store_grammars(range(5))
        for i in range(5):
            assert self.fs.get_last_version(filename=(
                self.grammar_format_str % i))
        assert mock_get_grammars.called_with(False)

    def test_get_cot_stats_by_cand(self):
        self.d.sort_by = 'size'
        self.d.calculate_compatible_grammars()
        stats = self.d.get_cot_stats_by_cand(self.d.raw_grammars[0])
        assert stats == structures.cot_stats_by_cand

    def test_sort_by(self):
        assert self.d.sort_by == 'rank_volume'
        self.d.calculate_compatible_grammars()
        assert self.d.grammars
        self.d.sort_by = 'size'
        assert not self.d.grammars
        assert self.d.sort_by == 'size'
        self.d.sort_by = 'size'
        assert self.d.sort_by == 'size'

    change_sort_grammars = set([
        frozenset([(3, 1), (2, 3), (2, 4), (2, 1)]),
        frozenset([(3, 2), (3, 1), (2, 1)]),
        frozenset([(3, 1), (2, 4), (2, 1)]),
        frozenset([(4, 1), (3, 1), (2, 3), (2, 1)]),
        frozenset([(3, 1), (2, 1)]), frozenset([(3, 1), (4, 1), (2, 1)]),
        frozenset([(3, 1), (2, 4)]), frozenset([(3, 1), (2, 3), (2, 1)]),
        frozenset([(3, 1), (4, 1), (2, 4), (2, 1)]),
        frozenset([(4, 1), (3, 1), (2, 3), (2, 4), (2, 1)]),
        frozenset([(3, 2), (3, 1), (4, 1), (2, 1)])
    ])

    @mock.patch('ot.poot.PoOT.get_grammars', return_value=change_sort_grammars)
    def test_changing_sort_by_changes_graph_images(self, mock_get_grammars):
        assert self.d.sort_by == 'rank_volume'
        self.d.calculate_compatible_grammars()
        assert mock_get_grammars.called_with(False)
        self.d.visualize_and_store_grammars([0])
        fname = 'voweldset/grammar0.png'
        old_image_hash = self.fs.get_last_version(filename=fname).md5
        self.d.sort_by = 'size'
        self.d.calculate_compatible_grammars()
        assert mock_get_grammars.called_with(False)
        self.d.visualize_and_store_grammars([0])
        new_image_hash = self.fs.get_last_version(filename=fname).md5
        assert not old_image_hash == new_image_hash

    @raises(gridfs.NoFile)
    def test_remove_old_files(self):
        self.d.calculate_entailments()
        self.d.visualize_and_store_entailments()
        assert self.fs.get_last_version(filename=self.entailments_fname)

        self.d.remove_old_files()
        self.fs.get_last_version(filename=self.entailments_fname)

    def test_num_compatible_poots(self):
        self.d.apriori_ranking = []
        self.d.calculate_compatible_grammars()
        assert self.d.num_compatible_poots() == 11

    def test_num_total_poots(self):
        assert self.d.num_total_poots() == 219

    num_compatible_cot_grammars = set([
        frozenset([(4, 2), (3, 2), (3, 1), (4, 1)]),
        frozenset([(1, 2), (4, 2), (3, 2), (4, 1), (4, 3)]),
        frozenset([(4, 2), (3, 2), (3, 1), (4, 1), (2, 1)]),
        frozenset([(4, 2), (3, 2), (4, 1), (4, 3)]),
        frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 1), (2, 4)]),
        frozenset([(3, 2), (4, 1)]),
        frozenset([(1, 2), (3, 2), (3, 1), (4, 3), (4, 2), (4, 1)]),
        frozenset([(3, 2), (3, 1), (2, 1), (4, 3), (4, 2), (4, 1)]),
        frozenset([(4, 2), (3, 2), (3, 1), (4, 1), (4, 3)]),
        frozenset([(1, 2), (4, 2), (3, 2), (3, 1), (4, 1)]),
        frozenset([(1, 2), (3, 2), (3, 4), (3, 1), (4, 2), (4, 1)]),
        frozenset([(4, 2), (3, 2), (4, 1)]),
        frozenset([(1, 2), (3, 2), (1, 3), (4, 3), (4, 2), (4, 1)]),
        frozenset([(3, 4), (3, 2), (3, 1), (4, 1), (2, 1)]),
        frozenset([(3, 2), (3, 4), (3, 1), (2, 1), (4, 2), (4, 1)]),
        frozenset([(3, 4), (3, 2), (3, 1), (4, 1)]),
        frozenset([(3, 2), (3, 1), (4, 1), (2, 1)]),
        frozenset([(3, 2), (3, 1), (4, 1)]),
        frozenset([(3, 4), (4, 2), (3, 2), (3, 1), (4, 1)]),
        frozenset([(1, 2), (4, 2), (3, 2), (4, 1)])
    ])

    @mock.patch('ot.poot.PoOT.get_grammars',
                return_value=num_compatible_cot_grammars)
    def test_num_compatible_cots(self, mock_get_grammars):
        data = {'name': 'cv_dset'}
        data.update(ot.data.cv_dset)
        d = models.Dataset(data=data, data_is_from_form=False)
        assert d.num_compatible_cots() == 6
        assert mock_get_grammars.called_with(False)

    def test_num_total_cots(self):
        data = {'name': 'cv_dset'}
        data.update(ot.data.cv_dset)
        d = models.Dataset(data=data, data_is_from_form=False)
        assert d.num_total_cots() == 24

    def test_delete_dset_deletes_grammar_list(self):
        original_num_grammarlist = len(GrammarList.objects)
        self.d.save()
        self.d.calculate_compatible_grammars()
        assert self.d.grammars
        assert len(GrammarList.objects) == original_num_grammarlist + 1
        self.d.grammars = None
        assert len(GrammarList.objects) == original_num_grammarlist + 1
        self.d.delete()
        assert len(GrammarList.objects) == original_num_grammarlist
