#! /usr/bin/env python

from ..rankomatic import models
from pygraphviz import AGraph

d = models.Dataset.objects.get(name="cv-grammar")
g = AGraph(directed=True)
for k, v in d.entailments.iteritems():
    for entailed in v:
        g.add_edge(k, entailed)

g2 = g.copy()

d._collapse_cycles(g)

for i, graph in enumerate([g, g2]):
    graph.tred()
    fname = "g%d.png" % i
    graph.draw(fname, prog="dot")
