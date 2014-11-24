import mock
import gridfs
from nose.tools import raises
import ot.data
from rankomatic import models, db
import test.structures.structures as structures
from test.test_tools import delete_bad_datasets


class TestDataset(object):

    def setUp(self):
        self.data = {
            'constraints': ['c1', 'c2', 'c3', 'c4'],
            'candidates': ot.data.voweldset,
            'name': 'voweldset'
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

    def test_constructor(self):
        self.check_bare_constructor()
        self.check_constructor_data_not_from_form()
        self.check_constructor_no_data_not_from_form()
        self.check_constructor_data_from_form()

    def check_bare_constructor(self):
        d = models.Dataset()
        assert d.upload_date
        assert not d.name
        assert len(d.constraints) == 3
        assert not d.candidates
        assert not d.entailments
        assert not d.grammars
        assert d.poot
        assert d.user == "guest"

    def check_constructor_no_data_not_from_form(self):
        d = models.Dataset(data_is_from_form=False)
        assert d.upload_date
        assert not d.name
        assert len(d.constraints) == 3
        assert not d.candidates
        assert not d.entailments
        assert not d.grammars
        assert d.poot
        assert d.user == "guest"

    def check_constructor_data_not_from_form(self):
        assert self.candidates_are_set_correctly(self.d, self.data)
        assert self.d.user == "guest"
        assert self.d.name == "voweldset"

    def check_constructor_data_from_form(self):
        form_data = self.d.create_form_data()
        form_dset = models.Dataset(data=form_data)
        assert self.candidates_are_set_correctly(form_dset, self.data)
        assert self.data['name'] == form_dset.name

    def test_create_form_data(self):
        form_data = self.d.create_form_data()
        assert form_data == {
            'name': 'voweldset',
            'constraints': ['c1', 'c2', 'c3', 'c4'],
            'input_groups': [
                {'candidates': [
                    {
                        'inp': 'ovea',
                        'outp': 'o-ve-a',
                        'vvector': [0, 1, 1, 0],
                        'optimal': True
                    },
                    {
                        'inp': 'ovea',
                        'outp': 'o-vee',
                        'vvector': [0, 0, 0, 1],
                        'optimal': True
                    }
                ]},
                {'candidates': [
                    {
                        'inp': 'idea',
                        'outp': 'i-de-a',
                        'vvector': [0, 1, 1, 0],
                        'optimal': True
                    },
                    {
                        'inp': 'idea',
                        'outp': 'i-dee',
                        'vvector': [1, 0, 0, 1],
                        'optimal': False
                    }
                ]},
                {'candidates': [
                    {
                        'inp': 'lasi-a',
                        'outp': 'la-si-a',
                        'vvector': [0, 0, 1, 0],
                        'optimal': True
                    },
                    {
                        'inp': 'lasi-a',
                        'outp': 'la-sii',
                        'vvector': [0, 0, 0, 1],
                        'optimal': True
                    }
                ]},
                {'candidates': [
                    {
                        'inp': 'rasia',
                        'outp': 'ra-si-a',
                        'vvector': [0, 0, 1, 0],
                        'optimal': True
                    },
                    {
                        'inp': 'rasia',
                        'outp': 'ra-sii',
                        'vvector': [1, 0, 0, 1],
                        'optimal': False
                    }
                ]}
            ]
        }

    def test_raw_grammars(self):
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
            'constraints': ['c1', 'c2', 'c3', 'c4']
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
                    'vvector': {1: 1, 2: 0, 3: 1}
                },
                {
                    'input': 'a',
                    'output': 'c',
                    'optimal': False,
                    'vvector': {1: 0, 2: 1, 3: 0}
                }
            ],
            'name': 'blank'
        }
        d = models.Dataset(data=data, data_is_from_form=False)
        d.calculate_compatible_grammars()
        for g in d.grammars:
            print g.raw_grammar
        assert d.raw_grammars == [frozenset([(1, 2), (3, 2), (1, 3)]),
                                  frozenset([(1, 2), (3, 2), (3, 1)]),
                                  frozenset([(1, 2), (3, 2)])]

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
        print gram_str
        assert gram_str == '{(c1, c3), (c1, c2)}'

    def test_grammar_to_string_empty_grammar(self):
        data = {
            'name': 'blank',
            'constraints': ['c1', 'c2', 'c3'],
            'candidates': [
                {
                    'input': 'a',
                    'output': 'b',
                    'optimal': True,
                    'vvector': {1: 0, 2: 0, 3: 0}
                },
                {
                    'input': 'a',
                    'output': 'c',
                    'optimal': False,
                    'vvector': {1: 1, 2: 1, 3: 1}
                }
            ]
        }
        d = models.Dataset(data=data, data_is_from_form=False)
        d.calculate_compatible_grammars()
        gram_str = d.grammar_to_string(-1)
        assert gram_str == "{ }"

    def test_calculate_global_entailments(self):
        self.d.calculate_global_entailments()
        assert self.d.entailments == structures.global_entailments

        # recalculate for coverage
        self.d.calculate_global_entailments()
        assert self.d.entailments == structures.global_entailments

    @raises(gridfs.NoFile)
    def test_visualize_and_store_entailments_no_entailments(self):
        data = {
            'constraints': ['c1', 'c2', 'c3'],
            'candidates': [{
                'input': 'a',
                'output': 'b',
                'vvector': {1: 0, 2: 0, 3: 0},
                'optimal': True
            }],
            'name': 'blank'
        }
        self.d = models.Dataset(data=data, data_is_from_form=False)
        self.d.calculate_global_entailments()
        self.d.visualize_and_store_entailments()
        self.fs.get_last_version(filename=self.entailments_fname)

    def test_visualize_and_store_entailments_with_entailments(self):
        self.d.calculate_global_entailments()
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
        self.d.calculate_global_entailments()
        self.d.visualize_and_store_entailments()
        assert self.fs.get_last_version(filename=self.entailments_fname)

        self.d.remove_old_files()
        self.fs.get_last_version(filename=self.entailments_fname)

    def test_num_compatible_poots(self):
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
