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

import gimmecert.commands


def test_init_sets_up_directory_structure(tmpdir):
    base_dir = tmpdir.join('.gimmecert')
    ca_dir = tmpdir.join('.gimmecert')

    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath)

    assert os.path.exists(base_dir.strpath)
    assert os.path.exists(ca_dir.strpath)


def test_init_generates_ca_artifacts(tmpdir):
    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath)

    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').strpath)
