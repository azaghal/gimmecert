.. Copyright (C) 2018 Branko Majic

   This file is part of Gimmecert documentation.

   This work is licensed under the Creative Commons Attribution-ShareAlike 3.0
   Unported License. To view a copy of this license, visit
   http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to Creative
   Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.


Development
===========

This section provides information on development process for the
project, including instructions on how to set-up a development
environment or run the tests locally.


Preparing development environment
---------------------------------

There is a number of different ways a development environment can be
set-up. The process outlined here is centered around
`virtualenvwrapper
<https://virtualenvwrapper.readthedocs.io/>`_. Instructions have been
tailored for a GNU/Linux system.

Before proceeding, ensure you have the following system-wide packages
installed:

- `Python, version 3.4+ <https://www.python.org/>`_.
- `virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/>`_.

With those in place, do the following:

1. Clone the git repository::

     git clone https://code.majic.rs/gimmecert/

2. Change directory::

     cd gimmecert/

3. Create Python virtual environment:

   .. warning::
      Make sure to specify Python 3 as interpreter.

   ::

     mkvirtualenv -a . -p /usr/bin/python3 gimmecert

4. Install development requirements::

     pip install -e .[devel]

5. At this point, any time you want to run tests etc, you can easily
   switch to correct environment (this will also put you in project
   root directory) with::

     workon gimmecert


Testing
-------

Project includes both unit tests (within ``tests/`` directory) , and
functional tests (within ``functional_tests/`` directory).

Running the tests will also generate coverage report in HTML format,
stored within directory ``coverage/``.

Tests can be run in a number of different ways, depending on what you
want to test and how.

To run the unit tests via setup script, run the following command from
repository root::

  python setup.py test

To run the unit tests directly, run the following command from
repository root::

  pytest

Functional tests must be run explicitly (since they tend to take more
time), with::

  pytest functional_tests/

Linting checks are performed as part of testing. Linting checks can
easily be run with command::

  flake8

Tests can also be run using `tox <https://tox.readthedocs.io/>`_:

.. note::
   When running tests via ``tox``, functional tests are included as
   well.

::

  # Run full suite of tests on all supported Python versions.
  tox

  # List available tox environments.
  tox -l

  # Run tests against specific Python version.
  tox -e py35

  # Run documentation and linting tests only.
  tox -e doc,lint


Building documentation
----------------------

Documentation is written in `reStructuredText
<https://en.wikipedia.org/wiki/ReStructuredText>`_ and built via
`Sphinx <http://www.sphinx-doc.org/>`_.

To build documentation, run::

  cd docs/
  make html

Resulting documentation will be stored in HTML format in directory
``docs/_build/html/``.
