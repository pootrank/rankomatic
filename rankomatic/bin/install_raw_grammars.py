#! /usr/bin/env python
"""To run:
    cd $PROJECT_DIR
    python -m rankomatic.bin.install_raw_grammars <max number of constraints>
"""
from ot.ordertheory import StrictOrders
from rankomatic.models.grammar import RawGrammar
from mongoengine import OperationError
import sys

if __name__ == "__main__":
    upper_bound = int(sys.argv[1]) + 1
    orders = StrictOrders()._StrictOrders__orders(range(1, upper_bound))
    RawGrammar.objects.delete()
    num_inserted = 0
    for order in set(orders):
        try:
            order = frozenset(sorted(list(order)))
            RawGrammar(grammar=str(order)).save()
            num_inserted += 1
        except OperationError:
            pass
    print "Successfully inserted %d grammars" % num_inserted
