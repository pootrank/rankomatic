from rq import Queue
from redis import Redis

from rankomatic.util import get_dset, get_username, get_url_args

redis_conn = Redis()
q = Queue(connection=redis_conn)
GRAMS_PER_PAGE = 20

def calculate_grammars_and_statistics(dset_name, sort_value):
    classical, page, sort_by = get_url_args()
    username = get_username()
    q.enqueue(_calculate_grammars_and_statistics, args=(dset_name, sort_value,
                                                        classical, page,
                                                        username, sort_by))


def _calculate_grammars_and_statistics(dset_name, sort_value,
                                       classical, page, username, sort_by):
    gc = GrammarCalculator(dset_name, sort_value, classical,
                           page, username, sort_by)
    gc._get_initial_data()
    gc._calculate_global_stats()
    gc._calculate_navbar_info()
    gc._truncate_grams_for_pagination()
    gc.dset.global_stats_calculated = True
    gc.dset.save()


def calculate_entailments(dset_name):
    q.enqueue(_calculate_entailments, args=(dset_name, get_username()))


def _calculate_entailments(dset_name, username):
    dset = get_dset(dset_name, username=username)
    dset.calculate_global_entailments()
    dset.visualize_and_store_entailments()


def make_grammar_info(dset_name):
    info_maker = GrammarInfoMaker(dset_name, get_username())
    q.enqueue(info_maker.make_grammar_info)


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
        self.grams = self._get_correct_grammars()
        self.dset.global_stats = {}

    def _get_correct_grammars(self):
        if self.classical:
            self._set_classical_sort_value()
        self.dset.sort_by = self.sort_by
        self.dset.calculate_compatible_grammars()
        raw_grammars = enumerate(self.dset.raw_grammars)
        sorter = self.dset.get_grammar_sorter()
        return [(i, g) for i, g in raw_grammars if sorter(g) == self.sort_value]

    def _set_classical_sort_value(self):
        if self.sort_by == 'size':
            self.sort_value = self._classical_grammar_length()
        else:
            self.sort_value = 1

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
        sort_values = self._get_possible_sort_values()
        num_rank_grams = len(self.grams)
        self.dset.grammar_navbar = self._get_min_max_indices(num_rank_grams)
        self.dset.grammar_navbar.update({
            'lengths': sort_values,
            'num_rank_grams': num_rank_grams,
        })

    def _get_possible_sort_values(self):
        if self.sort_by == 'size':
            reverse = True
        else:  # default 'rank_volume'
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


class GrammarInfoMaker():

    def __init__(self, dset_name, username):
        self.dset_name = dset_name
        self.username = username

    def make_grammar_info(self):
        self.dset = get_dset(self.dset_name, self.username)
        self.grams = eval(self.dset.global_stats['grams'])
        self.dset.visualize_and_store_grammars([x[0] for x in self.grams])
        grammar_info = []
        for gram in self.grams:
            cot_stats_by_cand = self.dset.get_cot_stats_by_cand(gram[1])
            input_totals = self._sum_all_cot_stats(cot_stats_by_cand)
            grammar_info.append({
                'grammar': self._make_grammar_string(gram[0]),
                'filename': self._make_grammar_filename(gram[0]),
                'cots_by_cand': cot_stats_by_cand,
                'input_totals': input_totals})
        self.dset.grammar_info = grammar_info
        self.dset.grammar_stats_calculated = True
        self.dset.save()

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

