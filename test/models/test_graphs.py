import gridfs
import mock

from nose.tools import assert_raises, raises, with_setup
from rankomatic.models.graphs import GridFSGraph, EntailmentGraph, GrammarGraph
from test.structures import structures as structs
from rankomatic import db


def no_setup():
    pass


def erase_temp_files():
    fs = gridfs.GridFS(db.get_pymongo_db(), collection='tmp')
    filenames = [f for f in fs.list() if 'temp' in f]
    for filename in filenames:
        fs.delete(fs.get_last_version(filename)._id)


def raise_no_file(*args, **kwargs):
    raise gridfs.NoFile


def test_constructer_bad_args():
    for not_string in ['', None, 5]:
        yield check_gridfsgraph_constructor_bad_arg, not_string


def check_gridfsgraph_constructor_bad_arg(not_string):
    with assert_raises(TypeError):
        GridFSGraph(dset_name=not_string, basename='basename')
    with assert_raises(TypeError):
        GridFSGraph(dset_name='dset_name', basename=not_string)


@raises(NotImplementedError)
def test_visualize_bare_graph():
    graph = GridFSGraph(dset_name='poop', basename='dumb')
    graph.visualize()


class SubclassGraph(GridFSGraph):

    def make_graph(self):
        self.add_edge('a', 'b')
        self.layout('dot')


@with_setup(no_setup, erase_temp_files)
def test_gridfs_graph_visualize_success():
    scg = SubclassGraph(dset_name='temp', basename='test')
    assert not scg.is_visualized()
    scg.visualize()
    assert scg.is_visualized()


@with_setup(no_setup, erase_temp_files)
@mock.patch('pygraphviz.AGraph.draw')
def test_gridfs_graph_visualize_already_vizualized(mock_draw):
    with mock.patch('gridfs.GridFS.get_last_version'):
        scg = SubclassGraph(dset_name='temp', basename='test')
        scg.visualize()
        assert not mock_draw.called


def test_entailment_graph():
    ents = [structs.entailments_no_cycles, structs.entailments_with_cycles]
    graph_strings = [structs.entailments_no_cycles_graph_string,
                     structs.entailments_with_cycles_graph_string]
    cots_by_cand = [structs.cots_by_cand_no_cycles,
                    structs.cots_by_cand_with_cycles]
    for i in range(len(ents)):
        graph = EntailmentGraph(ents[i], {}, 'temp',
                                cots_by_cand[i])
        graph_str = graph_strings[i]
    yield (check_graph_works, graph, graph_str, 'temp/entailments.png')


def test_grammar_graph():
    graph = GrammarGraph(structs.graph_testing_grammar, 'temp', 0)
    filename = 'temp/grammar0.png'
    yield check_graph_works, graph, structs.grammar_graph_string, filename


@mock.patch('pygraphviz.AGraph.layout')
@with_setup(no_setup, erase_temp_files)
def check_graph_works(graph, graph_str, filename, mock_layout):
    graph.make_graph()
    assert mock_layout.called
    assert graph.string() == graph_str
    assert graph.filename == filename


def test_apriori_entailment_graph():
    global_ents = structs.global_entailments
    apriori_ents = {
        'rasia, ra-si-a': ['idea, i-de-a'],
        'lasi-a, la-si-a': ['idea, i-de-a'],
        'idea, i-dee': ['lasi-a, la-sii', 'rasia, ra-sii']
    }
    cots_by_cand = {
        'ovea, o-ve-a': 8,
        'lasi-a, la-si-a': 12,
        'rasia, ra-si-a': 12,
        'idea, i-de-a': 12,
        'ovea, o-vee': 16,
        'lasi-a, la-sii': 12,
        'rasia, ra-sii': 8,
        'idea, i-dee': 8
    }
    graph_str = (u'strict digraph {\n\tgraph [encoding="UTF-8"];\n\tnode [label='
    '"\\N",\n\t\tshape=rect\n\t];\n\t"<<FONT POINT-SIZE=\\"14\\">(ovea, o-ve-a'
    ')</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 8</B></FONT>>"\t [label=<<F'
    'ONT POINT-SIZE="14">(ovea, o-ve-a)</FONT><BR/><FONT POINT-SIZE="10"><B>RV'
    ': 8</B></FONT>>];\n\t"<<FONT POINT-SIZE=\\"14\\">(lasi-a, la-si-a)</FONT>'
    '<BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>"\t [label=<<FONT POI'
    'NT-SIZE="14">(lasi-a, la-si-a)</FONT><BR/><FONT POINT-SIZE="10"><B>RV: 12'
    '</B></FONT>>];\n\t"<<FONT POINT-SIZE=\\"14\\">(ovea, o-ve-a)</FONT><BR/><'
    'FONT POINT-SIZE=\\"10\\"><B>RV: 8</B></FONT>>" -> "<<FONT POINT-SIZE=\\"1'
    '4\\">(lasi-a, la-si-a)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 12</B>'
    '</FONT>>";\n\t"<<FONT POINT-SIZE=\\"14\\">(idea, i-de-a)</FONT><BR/><FONT'
    ' POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>"\t [label=<<FONT POINT-SIZE="1'
    '4">(idea, i-de-a)</FONT><BR/><FONT POINT-SIZE="10"><B>RV: 12</B></FONT>>]'
    ';\n\t"<<FONT POINT-SIZE=\\"14\\">(ovea, o-ve-a)</FONT><BR/><FONT POINT-SI'
    'ZE=\\"10\\"><B>RV: 8</B></FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(idea, i'
    '-de-a)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>";\n\t"<'
    '<FONT POINT-SIZE=\\"14\\">(lasi-a, la-si-a)</FONT><BR/><FONT POINT-SIZE='
    '\\"10\\"><B>RV: 12</B></FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(idea, i-d'
    'e-a)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>"\t [style'
    '=dashed];\n\t"<<FONT POINT-SIZE=\\"14\\">(rasia, ra-si-a)</FONT><BR/><FON'
    'T POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>"\t [label=<<FONT POINT-SIZE="'
    '14">(rasia, ra-si-a)</FONT><BR/><FONT POINT-SIZE="10"><B>RV: 12</B></FONT'
    '>>];\n\t"<<FONT POINT-SIZE=\\"14\\">(lasi-a, la-si-a)</FONT><BR/><FONT PO'
    'INT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">('
    'rasia, ra-si-a)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>'
    '>";\n\t"<<FONT POINT-SIZE=\\"14\\">(idea, i-de-a)</FONT><BR/><FONT POINT-'
    'SIZE=\\"10\\"><B>RV: 12</B></FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(rasi'
    'a, ra-si-a)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>";'
    '\n\t"<<FONT POINT-SIZE=\\"14\\">(rasia, ra-si-a)</FONT><BR/><FONT POINT-SI'
    'ZE=\\"10\\"><B>RV: 12</B></FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(idea, '
    'i-de-a)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>"\t [st'
    'yle=dashed];\n\t"<<FONT POINT-SIZE=\\"14\\">(idea, i-dee)</FONT><BR/><FON'
    'T POINT-SIZE=\\"10\\"><B>RV: 8</B></FONT>>"\t [label=<<FONT POINT-SIZE="1'
    '4">(idea, i-dee)</FONT><BR/><FONT POINT-SIZE="10"><B>RV: 8</B></FONT>>];'
    '\n\t"<<FONT POINT-SIZE=\\"14\\">(ovea, o-vee)</FONT><BR/><FONT POINT-SIZE'
    '=\\"10\\"><B>RV: 16</B></FONT>>"\t [label=<<FONT POINT-SIZE="14">(ovea, o'
    '-vee)</FONT><BR/><FONT POINT-SIZE="10"><B>RV: 16</B></FONT>>];\n\t"<<FONT'
    ' POINT-SIZE=\\"14\\">(idea, i-dee)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><'
    'B>RV: 8</B></FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(ovea, o-vee)</FONT><'
    'BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 16</B></FONT>>";\n\t"<<FONT POINT-SI'
    'ZE=\\"14\\">(rasia, ra-sii)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 8'
    '</B></FONT>>"\t [label=<<FONT POINT-SIZE="14">(rasia, ra-sii)</FONT><BR/>'
    '<FONT POINT-SIZE="10"><B>RV: 8</B></FONT>>];\n\t"<<FONT POINT-SIZE=\\"14'
    '\\">(idea, i-dee)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 8</B></FONT>'
    '>" -> "<<FONT POINT-SIZE=\\"14\\">(rasia, ra-sii)</FONT><BR/><FONT POINT-'
    'SIZE=\\"10\\"><B>RV: 8</B></FONT>>"\t [style=dashed];\n\t"<<FONT POINT-SI'
    'ZE=\\"14\\">(lasi-a, la-sii)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: '
    '12</B></FONT>>"\t [label=<<FONT POINT-SIZE="14">(lasi-a, la-sii)</FONT><B'
    'R/><FONT POINT-SIZE="10"><B>RV: 12</B></FONT>>];\n\t"<<FONT POINT-SIZE=\\'
    '"14\\">(idea, i-dee)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 8</B></F'
    'ONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(lasi-a, la-sii)</FONT><BR/><FONT P'
    'OINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>"\t [style=dashed];\n\t"<<FONT PO'
    'INT-SIZE=\\"14\\">(rasia, ra-sii)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B'
    '>RV: 8</B></FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(idea, i-dee)</FONT><B'
    'R/><FONT POINT-SIZE=\\"10\\"><B>RV: 8</B></FONT>>";\n\t"<<FONT POINT-SIZE'
    '=\\"14\\">(rasia, ra-sii)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 8</'
    'B></FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(lasi-a, la-sii)</FONT><BR/><F'
    'ONT POINT-SIZE=\\"10\\"><B>RV: 12</B></FONT>>";\n\t"<<FONT POINT-SIZE=\\"'
    '14\\">(lasi-a, la-sii)</FONT><BR/><FONT POINT-SIZE=\\"10\\"><B>RV: 12</B>'
    '</FONT>>" -> "<<FONT POINT-SIZE=\\"14\\">(ovea, o-vee)</FONT><BR/><FONT P'
    'OINT-SIZE=\\"10\\"><B>RV: 16</B></FONT>>";\n}\n')
    graph = EntailmentGraph(global_ents, apriori_ents, 'temp', cots_by_cand)
    yield check_graph_works, graph, graph_str, 'temp/entailments.png'
