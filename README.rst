Rankomatic
==========


This app is an Optimality Theory (OT) constraint-ranking website.  Implemented
using Flask, it is built on a Python implementation of Alex Djalali's solution
to the ranking problem in theoretical OT.  For the details of his solution, see
`his paper`_ "A constructive solution to the ranking problem in Partial Order
Optimality Theory" (2013).  For the source of his implementation,
refer to `the Github repo`_.

The app is organized loosely according to the recommendations in the `Flask
documentation`_.  The views are implemented using Flask
Blueprints for modularity.

In order to run it, make sure you have pip installed.  Then clone the
repository, run the commands::

  pip install -r requirements.txt
  pip install git+git://github.com/cjeffers/OT
  python runserver.py

to start the basic server on your local machine.

:Author: Cameron Jeffers
:Company: Stanford University
:Email: cwjeffers18@gmail.com

.. _his paper: https://stanford.edu/~djalali/publications.html
.. _the Github repo: https://github.com/alexdjalali/OT
.. _Flask documentation: http://flask.pocoo.org/docs
