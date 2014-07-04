import gridfs
from nose.tools import raises
import ot.data
from .. import models
from .. import db
import structures


class TestDataset(object):
    def setUp(self):
        self.data = {
            'constraints': ['c1', 'c2', 'c3', 'c4'],
            'candidates': ot.data.voweldset
        }
        self.d = models.Dataset(data=self.data, data_is_from_form=False)
        self.d.name = "test_dset"
        self.entailments_fname = "".join([self.d.name, "/", 'entailments.svg'])
        self.grammar_format_str = self.d.name + "/grammar%d.svg"
        self.fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')

    def tearDown(self):
        pymongodb = db.get_pymongo_db()
        pymongodb.tmp.files.drop()
        pymongodb.tmp.chunks.drop()

    def test_constructor(self):
        self.check_bare_constructor()
        self.check_constructor_data_not_from_form()
        self.check_constructor_no_data_not_from_form()
        self.check_constructor_data_from_form()

    def test_raw_grammars(self):
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
            frozenset([(2, 3), (3, 1), (4, 1), (2, 4), (2, 1)])]

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
            frozenset([(2, 3), (3, 1), (4, 1), (2, 4), (2, 1)])]

    def check_constructor_data_not_from_form(self):
        assert self.candidates_are_set_correctly(self.d, self.data)

    def check_constructor_data_from_form(self):
        form_data = self.d.create_form_data()
        form_dset = models.Dataset(data=form_data)
        assert self.candidates_are_set_correctly(form_dset, self.data)

    def test_create_form_data(self):
        form_data = self.d.create_form_data()
        assert form_data == {
            'constraints': ['c1', 'c2', 'c3', 'c4'],
            'input_groups': [
                {'candidates': [
                    {
                        'inp': 'ovea',
                        'outp': 'o.ve.a',
                        'vvector': [0, 1, 1, 0],
                        'optimal': True
                    },
                    {
                        'inp': 'ovea',
                        'outp': 'o.vee',
                        'vvector': [0, 0, 0, 1],
                        'optimal': True
                    }
                ]},

                {'candidates': [
                    {
                        'inp': 'idea',
                        'outp': 'i.de.a',
                        'vvector': [0, 1, 1, 0],
                        'optimal': True
                    },
                    {
                        'inp': 'idea',
                        'outp': 'i.dee',
                        'vvector': [1, 0, 0, 1],
                        'optimal': False
                    }
                ]},

                {'candidates': [
                    {
                        'inp': 'lasi-a',
                        'outp': 'la.si.a',
                        'vvector': [0, 0, 1, 0],
                        'optimal': True
                    },
                    {
                        'inp': 'lasi-a',
                        'outp': 'la.sii',
                        'vvector': [0, 0, 0, 1],
                        'optimal': True
                    }
                ]},

                {'candidates': [
                    {
                        'inp': 'rasia',
                        'outp': 'ra.si.a',
                        'vvector': [0, 0, 1, 0],
                        'optimal': True
                    },
                    {
                        'inp': 'rasia',
                        'outp': 'ra.sii',
                        'vvector': [1, 0, 0, 1],
                        'optimal': False
                    }
                ]}
            ]
        }

    def check_bare_constructor(self):
        d = models.Dataset()
        assert d.upload_date
        assert not d.name
        assert len(d.constraints) == 3
        assert not d.candidates
        assert not d.entailments
        assert not d.grammars
        assert d.poot

    def check_constructor_no_data_not_from_form(self):
        d = models.Dataset(data_is_from_form=False)
        assert d.upload_date
        assert not d.name
        assert len(d.constraints) == 3
        assert not d.candidates
        assert not d.entailments
        assert not d.grammars
        assert d.poot

    def candidates_are_set_correctly(self, dataset, ot_dset):
        num_set = 0
        for c in ot_dset['candidates']:
            source_cand = models.Candidate(data=c)
            for dest_cand in dataset.candidates:
                if source_cand == dest_cand:
                    num_set += 1
        return num_set == len(ot_dset['candidates'])

    def test_process_form_data(self):
        data = {
            'candidates': ot.data.voweldset,
            'constraints': ['c1', 'c2', 'c3', 'c4']
        }
        d = models.Dataset(data=data, data_is_from_form=False)
        form_data = d.create_form_data()
        ot_data = models.Dataset().process_form_data(form_data)
        assert ot_data == data

    def test_calculate_compatible_grammars(self):
        d = models.Dataset.objects.get(name="test")
        assert not d._grammars
        d.calculate_compatible_grammars()
        assert d.grammars == [[[u'C2', u'C1'], [u'C2', u'C3'], [u'C3', u'C1']],
                              [[u'C2', u'C1'], [u'C2', u'C3'], [u'C1', u'C3']]]

    def test_calculate_compatible_poot_grammars(self):
        self.d.calculate_compatible_grammars(classical=False)
        assert self.d.grammars == structures.compatible_poot_grammars

    def test_calculate_compatible_grammars_no_grammars(self):
        self.data['candidates'] = ot.data.no_rankings
        self.d = models.Dataset(self.data, False)
        self.d.calculate_compatible_grammars(False)
        assert self.d.grammars == []

    def test_grammar_to_string(self):
        self.d.calculate_compatible_grammars(False)
        gram_str = self.d.grammar_to_string(self.d.grammars[0])
        assert gram_str == '{(c1, c3), (c1, c2)}'
        assert self.d.grammar_to_string([]) == "{ }"

    def test_calculate_global_entailments(self):
        self.d.calculate_global_entailments()
        assert self.d.entailments == structures.global_entailments
        d = models.Dataset()
        d.calculate_global_entailments()
        assert d.entailments == {}

    @raises(gridfs.NoFile)
    def test_visualize_and_store_entailments_no_entailments(self):
        self.d = models.Dataset()
        self.d.calculate_global_entailments()
        self.d.visualize_and_store_entailments()
        self.fs.get_last_version(filename=self.entailments_fname)

    def test_visualize_and_store_entailments_with_entailments(self):
        self.d.calculate_global_entailments()
        self.d.visualize_and_store_entailments()
        assert self.fs.get_last_version(filename=self.entailments_fname)

    @raises(gridfs.NoFile)
    def test_visualize_and_store_grammars_no_indices_cot(self):
        self.d.calculate_compatible_grammars()
        self.d.visualize_and_store_grammars([])
        self.fs.get_last_version(filename=(self.grammar_format_str % 0))

    @raises(gridfs.NoFile)
    def test_visualize_and_store_grammars_no_indices_poot(self):
        self.d.calculate_compatible_grammars(classical=False)
        self.d.visualize_and_store_grammars([])
        self.fs.get_last_version(filename=(self.grammar_format_str % 0))

    def test_visualize_and_store_grammars_cot(self):
        self.data['candidates'] = ot.data.hbounded
        self.d.set_dset(self.data)
        self.d.poot = self.d.build_poot()
        self.d.calculate_compatible_grammars()
        self.d.visualize_and_store_grammars(range(5))
        for i in range(5):
            assert self.fs.get_last_version(filename=(
                self.grammar_format_str % i))

    def test_visualize_and_store_grammars_poot(self):
        self.d.calculate_compatible_grammars(classical=False)
        self.d.visualize_and_store_grammars(range(5))
        for i in range(5):
            assert self.fs.get_last_version(filename=(
                self.grammar_format_str % i))

    def test_get_cot_stats_by_cand(self):
        self.d.calculate_compatible_grammars(classical=False)
        stats = self.d.get_cot_stats_by_cand(self.d.raw_grammars[0])
        assert stats == structures.cot_stats_by_cand
