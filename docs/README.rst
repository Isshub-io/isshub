:orphan:

==================================
Welcome to IssHub's documentation!
==================================

--------------------
Online documentation
--------------------

Documentation is available at `<https://isshub.readthedocs.io>`_

-------
Content
-------

This documentation will includes a lot of things, but not everything will be present from day one:

- install process
- run process
- dev process and tools
- how things works from a dev point of view (including source code documentation)
- how things works from a user point of view
- ...

-----------
Local build
-----------

To build the documentation:

- install dependencies::

    pip install -e .[docs]

- build the documentations::

    make doc

  or::

    cd docs
    make html


Then point your browser to: file:///path/to/isshub/docs/_build/html/index.html
