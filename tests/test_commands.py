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
    ca_dir = tmpdir.join('.gimmecert', 'ca')
    server_dir = tmpdir.join('.gimmecert', 'server')
    depth = 1

    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    assert os.path.exists(base_dir.strpath)
    assert os.path.exists(ca_dir.strpath)
    assert os.path.exists(server_dir.strpath)


def test_init_generates_single_ca_artifact_for_depth_1(tmpdir):
    depth = 1

    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').strpath)


def test_init_generates_three_ca_artifacts_for_depth_3(tmpdir):
    depth = 3

    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level2.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level2.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level3.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level3.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').strpath)


def test_init_outputs_full_chain_for_depth_1(tmpdir):
    depth = 1

    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    level1_certificate = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    full_chain = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()
    assert level1_certificate == full_chain
    assert full_chain.replace(level1_certificate, '') == ''


def test_init_outputs_full_chain_for_depth_3(tmpdir):
    depth = 3

    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    level1_certificate = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    level2_certificate = tmpdir.join('.gimmecert', 'ca', 'level2.cert.pem').read()
    level3_certificate = tmpdir.join('.gimmecert', 'ca', 'level3.cert.pem').read()
    full_chain = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()
    assert level1_certificate in full_chain
    assert level2_certificate in full_chain
    assert level3_certificate in full_chain
    assert full_chain == "%s\n%s\n%s" % (level1_certificate, level2_certificate, level3_certificate)


def test_init_returns_true_if_directory_has_not_been_previously_initialised(tmpdir):
    depth = 1

    tmpdir.chdir()

    initialised = gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    assert initialised is True


def test_init_returns_false_if_directory_has_been_previously_initialised(tmpdir):
    depth = 1

    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)
    initialised = gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    assert initialised is False


def test_init_does_not_overwrite_artifcats_if_already_initialised(tmpdir):
    depth = 1

    tmpdir.chdir()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    level1_private_key_before = tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').read()
    level1_certificate_before = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    full_chain_before = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()

    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    level1_private_key_after = tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').read()
    level1_certificate_after = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    full_chain_after = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()

    assert level1_private_key_before == level1_private_key_after
    assert level1_certificate_before == level1_certificate_after
    assert full_chain_before == full_chain_after


def test_server_returns_status_and_message(tmpdir):
    tmpdir.chdir()

    status, message = gimmecert.commands.server(tmpdir.strpath, 'myserver', None)

    assert isinstance(status, bool)
    assert isinstance(message, str)


def test_server_reports_error_if_directory_is_not_initialised(tmpdir):
    tmpdir.chdir()

    status, message = gimmecert.commands.server(tmpdir.strpath, 'myserver', None)

    assert status is False
    assert "must be initialised" in message


def test_server_reports_paths_to_generated_artifacts(tmpdir):
    depth = 1

    tmpdir.chdir()
    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    status, message = gimmecert.commands.server(tmpdir.strpath, 'myserver', None)

    assert status is True
    assert ".gimmecert/server/myserver.key.pem" in message
    assert ".gimmecert/server/myserver.cert.pem" in message


def test_server_outputs_private_key_to_file(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem')

    tmpdir.chdir()
    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(tmpdir.strpath, 'myserver', None)

    assert private_key_file.check(file=1)

    private_key_file_content = private_key_file.read()

    assert private_key_file_content.startswith('-----BEGIN RSA PRIVATE KEY')
    assert private_key_file_content.endswith('END RSA PRIVATE KEY-----\n')


def test_server_outputs_certificate_to_file(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem')

    tmpdir.chdir()
    gimmecert.commands.init(tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(tmpdir.strpath, 'myserver', None)

    assert certificate_file.check(file=1)

    certificate_file_content = certificate_file.read()

    assert certificate_file_content.startswith('-----BEGIN CERTIFICATE')
    assert certificate_file_content.endswith('END CERTIFICATE-----\n')
