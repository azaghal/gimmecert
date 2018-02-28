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

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename)

    assert os.path.exists(base_dir.strpath)
    assert os.path.exists(ca_dir.strpath)


def test_init_generates_ca_artifacts(tmpdir):
    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename)

    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').strpath)


def test_init_returns_true_if_directory_has_not_been_previously_initialised(tmpdir):
    tmpdir.chdir()

    initialised = gimmecert.commands.init(tmpdir.strpath, tmpdir.basename)

    assert initialised is True


def test_init_returns_false_if_directory_has_been_previously_initialised(tmpdir):
    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename)
    initialised = gimmecert.commands.init(tmpdir.strpath, tmpdir.basename)

    assert initialised is False


def test_init_does_not_overwrite_artifcats_if_already_initialised(tmpdir):
    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename)

    level1_private_key_before = tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').read()
    level1_certificate_before = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    full_chain_before = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename)

    level1_private_key_after = tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').read()
    level1_certificate_after = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    full_chain_after = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()

    assert level1_private_key_before == level1_private_key_after
    assert level1_certificate_before == level1_certificate_after
    assert full_chain_before == full_chain_after
