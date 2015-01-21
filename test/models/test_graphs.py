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
        graph = EntailmentGraph(ents[i], 'temp',
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
