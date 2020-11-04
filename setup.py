#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Branko Majic
#
# This file is part of Gimmecert.
#
# Gimmecert is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Gimmecert is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Gimmecert.  If not, see <http://www.gnu.org/licenses/>.
#

import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

python_requirements = ">=3.5,<3.10"

install_requirements = [
    'cryptography>=3.2,<3.3',
    'python-dateutil>=2.8,<2.9',
]

doc_requirements = [
    'sphinx>=3.3,<3.4',
]

test_lint_requirements = [
    'flake8>=3.8,<3.9',
]

test_requirements = [
    'freezegun>=1.0,<1.1',
    'pytest>=6.1,<6.2',
    'pytest-cov>=2.10,<2.11',
    'tox>=3.20,<3.21',
    'pexpect>=4.8,<4.9',
]

release_requirements = [
    'twine',
]

setup_requirements = [
    'pytest-runner>=5.2,<5.3',
]

development_requirements = doc_requirements + test_requirements + test_lint_requirements + release_requirements

extras_requirements = {
    'devel': development_requirements,
    'doc': doc_requirements,
    'test': test_requirements,
    'testlint': test_lint_requirements,
}

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='gimmecert',
    version='0.0.0',
    packages=find_packages(exclude=['tests', 'functional_tests']),
    include_package_data=True,
    license='GPLv3+',
    description='A simple tool for quickly issuing server and client certificates.',
    long_description=README,
    url='http://projects.majic.rs/gimmecert',
    author='Branko Majic',
    author_email='branko@majic.rs',
    python_requires=python_requirements,
    install_requires=install_requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    extras_require=extras_requirements,
    entry_points={
        'console_scripts': ['gimmecert=gimmecert.cli:main'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Security',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
)
