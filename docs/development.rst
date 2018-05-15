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

Tests can be run in a number of different ways, depending on what you
want to test and how.

To run the unit tests via setup script, run the following command from
repository root::

  python setup.py test

To run the unit tests directly, run the following command from
repository root::

  pytest

Tests can be also run with coverage checks. By default coverage is
configured to report to standard output. Report will only list files
which lack coverage. For each file a percentage will be shown, as well
as line numbers that were not covered by tests. To include coverage
checks, run tests with::

  pytest --cov

.. warning::
   Gimmecert project has 100% coverage requirement. Anything below
   will trigger failures when coverage checks are run.

Should you desire to generate coverage report in HTML format, run
(coverage report will be put into directory ``coverage/``)::

  pytest --cov --cov-report=html:coverage/

Functional tests must be run explicitly (since they tend to take more
time), with::

  pytest functional_tests/

In addition to proper linting, implemented code should be pruned of
unused imports and variables. Linting should be conformant to PEP8,
with the exception of line length, which is allowed to be up to 160
characters. Linting and code sanity checks are not executed
automatically, but can easily be run with::

  flake8

Documentation should be buildable at all times. Documentation build
can be triggered with a simple::

  cd docs/
  make html

Tests can also be run using `tox <https://tox.readthedocs.io/>`_:

.. note::
   When running tests via ``tox``, functional tests and coverage
   checks are included as well.

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


Versioning schema
-----------------

Project employs `semantic versioning <http://semver.org/>`_ schema. In
short:

- Each version is composed of major, minor, and patch number. For example, in
  version ``1.2.3``, ``1`` is the major, ``2`` is the minor, and ``3`` is the
  patch number.
- Major number is bumped when making a backwards incompatible change.
- Minor number is bumped when new features or changes are made without
  breaking backwards compatibility.
- Patch number is bumped when backporting bug or security fixes into
  an older release.

In addition to versioning schema, project employs a specific
nomenclature for naming the branches:

- All new development (both for features and bug/security fixes) uses
  master branch as the base.
- Features and bug/security fixes are implemented in a local branch
  based on the master branch. Local branches are named after the
  lower-cased issue number. For example, if the issuer number is
  ``GC-43``, the implementation branch will be named
  ``gc-43``. Normally these branches are only local, but if necessary
  they can be pushed to central repository for collaboration or
  preview purposes.
- Patch releases are based off the maintenance branches. Mainteance
  branches are named after the ``MAJOR`` and ``MINOR`` number of the
  version - ``maintenance/MAJOR.MINOR``. For example, if a new release
  is made with version ``1.2.0``, the corresponding branch that is
  created for maintenance will be named ``maintenance/1.2`` (notice the absence of
  ``.0`` at the end).


Backporting fixes
-----------------

From time to time it might become useful to apply a bug/security fix
to both the master branch, and to maintenace branch.

When a bug should be applied to maintenance branch as well, procedure
is as follows:

1. Create a new bug report in `issue tracker
   <https://projects.majic.rs/gimmecert>`_. Target version should be
   either the next minor or next major release (i.e. whatver will get
   released from the master branch).

2. Create a copy of the bug report, modifying the issue title to include phrase
   ``(backport to MAJOR.MINOR)`` at the end, with ``MAJOR`` and ``MINOR``
   replaced with correct versioning information for the maintenance
   branch. Make sure to set correct target version (patch release).

3. Resolve the bug for next major/minor release.

4. Resolve the bug in maintenace branch by backporting (cherry-picking
   if possible) the fix into maintenace branch. Make sure to resign
   (cherry-picking invalidates OpenPGP signature) and reword (to
   reference the backport issue) the commit.


Release notes
-------------

Release notes are written in parallel to resolving project issues, in
the ``docs/releasenotes.rst`` file. In other words, any time a new
feature, bug fix etc is implemented, an entry should be created in the
relase notes file. This applies for tasks and user stories as well.

By ensuring the release notes are always up-to-date, the release
process is simpler, faster, and less error prone.

Release notes are always added under section title **NEXT
RELEASE**. This placeholder section title is replaced during the
release process.

Release notes for each version consist out of two parts - the general
release description, and listing of resolved issues.

General description provides a high-level overview of new
functionality and fixes included in the release, and points to any
important/breaking changes.

The listing of resolved issues is split-up based on issue type, and
lists all issues that have been resolved in the given release. Each
issue in the list is provied as URL link pointing to issue URL in the
issue tracker, with the link text in format ``ISSUE_NUMBER:
ISSUE_TITLE``. Both issue number and issue title are taken from the
issue tracker.

To provide a more visual example, template for single release note is
as follows::

  NEXT RELEASE
  ------------

  [General description of release.]

  Resolved issues:

  - **User stories**:

    - `ISSUER_NUMBER: ISSUE_TITLE <ISSUE_URL>`_
    - `ISSUER_NUMBER: ISSUE_TITLE <ISSUE_URL>`_
  - **Feature requests**:

    - `ISSUER_NUMBER: ISSUE_TITLE <ISSUE_URL>`_
    - `ISSUER_NUMBER: ISSUE_TITLE <ISSUE_URL>`_
  - **Enhancements**:

    - `ISSUER_NUMBER: ISSUE_TITLE <ISSUE_URL>`_
    - `ISSUER_NUMBER: ISSUE_TITLE <ISSUE_URL>`_
  - **Tasks**:

    - `ISSUER_NUMBER: ISSUE_TITLE <ISSUE_URL>`_
    - `ISSUER_NUMBER: ISSUE_TITLE <ISSUE_URL>`_


Release process
---------------

The release process for Gimmecert is centered around the use of
included ``release.sh`` script. The script takes care of a number of
tedious tasks, including:

- Updating the version information in release notes and ``setup.py``.
- Tagging a release.
- Starting a new section in release notes.
- Switching version back to development in ``setup.py``.
- Publishing changes to origin Git repository and publishing release
  to PyPI.

When releasing a new major/minor version (from the master branch), the
release script will take care of setting-up a maintenance branch as
well.

Patch releases should be done from maintenance branches. New
major/minor releases should be done from the master branch.

.. warning::
   Keep in mind that the release script is interactive, it cannot be
   run unattended.

Perform the following steps in order to release new version of
Gimmecert:

1. Make sure that Git is correctly set-up for signing using GnuPG, and
   that the necessary key material is available.

2. Verify that there are no outstanding issues for this release in the
   issue tracker.

3. Switch to project virtual environment.

4. Ensure that the repository is synchronised with origin, and that a
   correct branch is checked out (master or maintenance).

5. Go through release notes for ``NEXT VERSION``, and ensure the
   general description and listed issues look fine. Make any necessary
   changes, commit them, and push them to the origin.

6. Prepare the release:

   .. warning::
      Make sure to provide correct version.

   ::

      ./release.sh prepare VERSION

7. Verify that the preparation process was successful.

8. Publish the release:

   .. warning::
      Make sure to provide correct version.

   ::

      ./release.sh publish VERSION

9. Build release documentation on `Read the Docs project page
   <https://readthedocs.org/projects/gimmecert/>`_, and update the
   default version if this was a new major/minor release.

10. Verify documentation looks good on `Read the Docs documentation
    page <https://gimmecert.readthedocs.io/>`_.

11. Mark the release issue as resolved in the issue tracker.

12. Release the version via release center in the issue
    tracker. Upload source archive from the ``dist/`` directory.

13. Archive outdated releases in the issue tracker.
