from collections import OrderedDict


class DatasetConverter():

    @classmethod
    def form_data_to_ot_data(cls, form_data):
        processed = cls._initialize_ot_data_from(form_data)
        for ig in form_data['input_groups']:
            for cand in ig['candidates']:
                processed['candidates'].append(cls._process_candidate(cand))
        return processed

    @classmethod
    def _initialize_ot_data_from(cls, form_data):
        return {
            'name': form_data['name'],
            'constraints': form_data['constraints'],
            'candidates': []}

    @classmethod
    def _process_candidate(cls, form_cand):
        return {
            'output': form_cand['outp'],
            'input': form_cand['inp'],
            'optimal': form_cand['optimal'],
            'vvector': cls._make_violation_vector_dict(form_cand['vvector'])}

    @classmethod
    def _make_violation_vector_dict(cls, list_vvect):
        return dict((i+1, v) for i, v in enumerate(list_vvect))

    @classmethod
    def db_dataset_to_form_data(cls, dset):
        form_data = cls._initialize_form_data(dset)
        inputs = cls._get_all_inputs_from_candidates(dset)
        for inp in inputs:
            input_group = cls._create_input_group_for(inp, dset)
            form_data['input_groups'].append(input_group)
        return form_data

    @classmethod
    def _initialize_form_data(cls, dset):
        return {
            'name': dset.name,
            'constraints': dset.constraints,
            'input_groups': []
        }

    @classmethod
    def _get_all_inputs_from_candidates(cls, dset):
        inputs = [cand.input for cand in dset.candidates]
        unique_inputs = list(OrderedDict.fromkeys(inputs))
        return unique_inputs

    @classmethod
    def _create_input_group_for(cls, inp, dset):
        input_group = {'candidates': []}
        for cand in dset.candidates:
            if cand.input == inp:
                input_group['candidates'].append(cls._make_cand_dict(cand))
        return input_group

    @classmethod
    def _make_cand_dict(self, old_cand):
        return {
            'inp': old_cand.input,
            'outp': old_cand.output,
            'optimal': old_cand.optimal,
            'vvector': old_cand.vvector
        }

    @classmethod
    def create_ot_compatible_candidates(cls, dset):
        return [{
                'input': c.input,
                'output': c.output,
                'optimal': c.optimal,
                'vvector': cls._make_violation_vector_dict(c.vvector)
                } for c in dset.candidates]


def pair_to_string(p):
    return "".join([p[0], ', ', p[1]])
