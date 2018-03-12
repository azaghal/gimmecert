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

import argparse
import io
import os

import gimmecert.commands


def test_init_sets_up_directory_structure(tmpdir):
    base_dir = tmpdir.join('.gimmecert')
    ca_dir = tmpdir.join('.gimmecert', 'ca')
    server_dir = tmpdir.join('.gimmecert', 'server')
    depth = 1

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    assert os.path.exists(base_dir.strpath)
    assert os.path.exists(ca_dir.strpath)
    assert os.path.exists(server_dir.strpath)


def test_init_generates_single_ca_artifact_for_depth_1(tmpdir):
    depth = 1

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').strpath)


def test_init_generates_three_ca_artifacts_for_depth_3(tmpdir):
    depth = 3

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level2.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level2.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level3.key.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level3.cert.pem').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').strpath)


def test_init_outputs_full_chain_for_depth_1(tmpdir):
    depth = 1

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    level1_certificate = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    full_chain = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()
    assert level1_certificate == full_chain
    assert full_chain.replace(level1_certificate, '') == ''


def test_init_outputs_full_chain_for_depth_3(tmpdir):
    depth = 3

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    level1_certificate = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    level2_certificate = tmpdir.join('.gimmecert', 'ca', 'level2.cert.pem').read()
    level3_certificate = tmpdir.join('.gimmecert', 'ca', 'level3.cert.pem').read()
    full_chain = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()
    assert level1_certificate in full_chain
    assert level2_certificate in full_chain
    assert level3_certificate in full_chain
    assert full_chain == "%s\n%s\n%s" % (level1_certificate, level2_certificate, level3_certificate)


def test_init_returns_success_if_directory_has_not_been_previously_initialised(tmpdir):
    depth = 1

    status_code = gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    assert status_code == gimmecert.commands.ExitCode.SUCCESS


def test_init_returns_error_code_if_directory_has_been_previously_initialised(tmpdir):
    depth = 1

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    status_code = gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    assert status_code == gimmecert.commands.ExitCode.ERROR_ALREADY_INITIALISED


def test_init_does_not_overwrite_artifcats_if_already_initialised(tmpdir):
    depth = 1

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    level1_private_key_before = tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').read()
    level1_certificate_before = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    full_chain_before = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    level1_private_key_after = tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').read()
    level1_certificate_after = tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').read()
    full_chain_after = tmpdir.join('.gimmecert', 'ca', 'chain-full.cert.pem').read()

    assert level1_private_key_before == level1_private_key_after
    assert level1_certificate_before == level1_certificate_after
    assert full_chain_before == full_chain_after


def test_server_returns_status_code(tmpdir):
    status_code = gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)

    assert isinstance(status_code, int)


def test_server_reports_error_if_directory_is_not_initialised(tmpdir):

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, tmpdir.strpath, 'myserver', None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert "must be initialised" in stderr
    assert stdout == ""
    assert status_code == gimmecert.commands.ExitCode.ERROR_NOT_INITIALISED


def test_server_reports_success_and_paths_to_generated_artifacts(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, tmpdir.strpath, 'myserver', None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert stderr == ""


def test_server_outputs_private_key_to_file(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)

    assert private_key_file.check(file=1)

    private_key_file_content = private_key_file.read()

    assert private_key_file_content.startswith('-----BEGIN RSA PRIVATE KEY')
    assert private_key_file_content.endswith('END RSA PRIVATE KEY-----\n')


def test_server_outputs_certificate_to_file(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)

    assert certificate_file.check(file=1)

    certificate_file_content = certificate_file.read()

    assert certificate_file_content.startswith('-----BEGIN CERTIFICATE')
    assert certificate_file_content.endswith('END CERTIFICATE-----\n')


def test_server_errors_out_if_certificate_already_issued(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Previous run.
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)
    existing_private_key = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem').read()
    certificate = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem').read()

    # New run.
    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, tmpdir.strpath, 'myserver', None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED
    assert "already been issued" in stderr
    assert stdout == ""
    assert tmpdir.join('.gimmecert', 'server', 'myserver.key.pem').read() == existing_private_key
    assert tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem').read() == certificate


def test_init_command_stdout_and_stderr_for_single_ca(tmpdir):
    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(stdout_stream, stderr_stream, tmpdir.strpath, "myproject", 1)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert stderr == ""
    assert "CA hierarchy initialised" in stdout
    assert ".gimmecert/ca/level1.cert.pem" in stdout
    assert ".gimmecert/ca/level1.key.pem" in stdout
    assert ".gimmecert/ca/chain-full.cert.pem" in stdout


def test_init_command_stdout_and_stderr_for_multiple_cas(tmpdir):
    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(stdout_stream, stderr_stream, tmpdir.strpath, "myproject", 3)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert stderr == ""
    assert "CA hierarchy initialised" in stdout
    assert ".gimmecert/ca/level1.cert.pem" in stdout
    assert ".gimmecert/ca/level1.key.pem" in stdout
    assert ".gimmecert/ca/level2.cert.pem" in stdout
    assert ".gimmecert/ca/level2.key.pem" in stdout
    assert ".gimmecert/ca/level3.cert.pem" in stdout
    assert ".gimmecert/ca/level3.key.pem" in stdout
    assert ".gimmecert/ca/chain-full.cert.pem" in stdout


def test_init_command_stdout_and_stderr_if_hierarchy_already_initialised(tmpdir):
    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, "myproject", 1)

    gimmecert.commands.init(stdout_stream, stderr_stream, tmpdir.strpath, "myproject", 1)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert "CA hierarchy has already been initialised" in stderr
    assert stdout == ""


def test_help_command_returns_success_status_code():
    status_code = gimmecert.commands.help_(io.StringIO(), io.StringIO(), argparse.ArgumentParser())

    assert status_code == gimmecert.commands.ExitCode.SUCCESS


def test_help_command_outputs_help():
    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    parser = argparse.ArgumentParser(description="This is help")

    gimmecert.commands.help_(stdout_stream, stderr_stream, parser)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert stderr == ""
    assert "usage" in stdout
    assert "--help" in stdout


def test_usage_command_returns_success_status_code():
    status_code = gimmecert.commands.usage(io.StringIO(), io.StringIO(), argparse.ArgumentParser())

    assert status_code == gimmecert.commands.ExitCode.SUCCESS


def test_usage_command_outputs_usage():
    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    parser = argparse.ArgumentParser(description="This is help")

    gimmecert.commands.usage(stdout_stream, stderr_stream, parser)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert stderr == ""
    assert "usage:" in stdout
    assert len(stdout.splitlines()) == 1


def test_client_reports_error_if_directory_is_not_initialised(tmpdir):

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert "must be initialised" in stderr
    assert stdout == ""
    assert status_code == gimmecert.commands.ExitCode.ERROR_NOT_INITIALISED


def test_client_returns_status_code(tmpdir):
    status_code = gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath)

    assert isinstance(status_code, int)
