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

from freezegun import freeze_time


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
    assert "server myserver" in stderr
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

    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath, 'myclient')

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert "must be initialised" in stderr
    assert stdout == ""
    assert status_code == gimmecert.commands.ExitCode.ERROR_NOT_INITIALISED


def test_client_returns_status_code(tmpdir):
    status_code = gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient')

    assert isinstance(status_code, int)


def test_client_reports_success_and_paths_to_generated_artifacts(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath, 'myclient')

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "certificate issued" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert stderr == ""


def test_client_outputs_private_key_to_file(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'client', 'myclient.key.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient')

    assert private_key_file.check(file=1)

    private_key_file_content = private_key_file.read()

    assert private_key_file_content.startswith('-----BEGIN RSA PRIVATE KEY')
    assert private_key_file_content.endswith('END RSA PRIVATE KEY-----\n')


def test_client_outputs_certificate_to_file(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient')

    assert certificate_file.check(file=1)

    certificate_file_content = certificate_file.read()

    assert certificate_file_content.startswith('-----BEGIN CERTIFICATE-----')
    assert certificate_file_content.endswith('-----END CERTIFICATE-----\n')


def test_client_errors_out_if_certificate_already_issued(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Previous run.
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient')
    existing_private_key = tmpdir.join('.gimmecert', 'client', 'myclient.key.pem').read()
    certificate = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem').read()

    # New run.
    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath, 'myclient')

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED
    assert "already been issued" in stderr
    assert "client myclient" in stderr
    assert stdout == ""
    assert tmpdir.join('.gimmecert', 'client', 'myclient.key.pem').read() == existing_private_key
    assert tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem').read() == certificate


def test_server_reports_success_if_certificate_already_issued_but_update_was_requested(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Previous run.
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)
    existing_private_key = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem').read()
    certificate = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem').read()

    # New run.
    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, tmpdir.strpath, 'myserver', None, True)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert "renewed with new DNS subject alternative names" in stdout
    assert "key has remained unchanged" in stdout
    assert stderr == ""
    assert tmpdir.join('.gimmecert', 'server', 'myserver.key.pem').read() == existing_private_key
    assert tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem').read() != certificate


def test_server_reports_success_if_certificate_not_already_issued_but_update_was_requested(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, tmpdir.strpath, 'myserver', None, True)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert stderr == ""


def test_renew_returns_status_code(tmpdir):
    tmpdir.chdir()

    status_code = gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', False)

    assert isinstance(status_code, int)


def test_renew_reports_error_if_directory_is_not_initialised(tmpdir):

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', False)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert "No CA hierarchy has been initialised yet" in stderr
    assert stdout == ""
    assert status_code == gimmecert.commands.ExitCode.ERROR_NOT_INITIALISED


def test_renew_reports_error_if_no_existing_server_certificate_is_present(tmpdir):
    depth = 1
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', False)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.ERROR_UNKNOWN_ENTITY
    assert "Cannot renew certificate" in stderr
    assert "server myserver" in stderr
    assert stdout == ""


def test_renew_reports_error_if_no_existing_client_certificate_is_present(tmpdir):
    depth = 1
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'client', 'myclient', False)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.ERROR_UNKNOWN_ENTITY
    assert "Cannot renew certificate" in stderr
    assert "client myclient" in stderr
    assert stdout == ""


def test_renew_reports_success_and_paths_to_server_artifacts(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', False)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Renewed certificate for server myserver." in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert stderr == ""


def test_renew_reports_success_and_paths_to_client_artifacts(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient')

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'client', 'myclient', False)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Renewed certificate for client myclient." in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert stderr == ""


def test_renew_keeps_server_private_key(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)
    private_key_after_issuance = private_key_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', False)
    private_key_after_renewal = private_key_file.read()

    assert private_key_after_issuance == private_key_after_renewal


def test_renew_keeps_client_private_key(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'client', 'myclient.key.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient')
    private_key_after_issuance = private_key_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'client', 'myclient', False)
    private_key_after_renewal = private_key_file.read()

    assert private_key_after_issuance == private_key_after_renewal


def test_renew_replaces_server_certificate(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)
    certificate_after_issuance = certificate_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', False)
    certificate_after_renewal = certificate_file.read()

    assert certificate_after_issuance != certificate_after_renewal
    assert certificate_after_renewal.startswith('-----BEGIN CERTIFICATE')
    assert certificate_after_renewal.endswith('END CERTIFICATE-----\n')


def test_renew_replaces_client_certificate(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient')
    certificate_after_issuance = certificate_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'client', 'myclient', False)
    certificate_after_renewal = certificate_file.read()

    assert certificate_after_issuance != certificate_after_renewal
    assert certificate_after_renewal.startswith('-----BEGIN CERTIFICATE')
    assert certificate_after_renewal.endswith('END CERTIFICATE-----\n')


def test_renew_reports_success_and_paths_to_server_artifacts_with_new_key(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', True)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Generated new private key and renewed certificate for server myserver." in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert stderr == ""


def test_renew_generates_new_private_key_if_requested(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None)
    private_key_after_issuance = private_key_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', True)
    private_key_after_renewal = private_key_file.read()

    assert private_key_after_issuance != private_key_after_renewal


def test_status_returns_status_code(tmpdir):
    status_code = gimmecert.commands.status(io.StringIO(), io.StringIO(), tmpdir.strpath)

    assert isinstance(status_code, int)


def test_status_reports_uninitialised_directory(tmpdir):
    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.ERROR_NOT_INITIALISED
    assert stderr == ""
    assert "CA hierarchy has not been initialised in current directory." in stdout


def test_status_reports_ca_hierarchy_information(tmpdir):
    depth = 3

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stdout_lines = stdout.split("\n")
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "CA hierarchy\n------------\n" in stdout

    index_ca_1 = stdout_lines.index("CN=%s Level 1 CA" % tmpdir.basename)  # Should not raise
    index_ca_2 = stdout_lines.index("CN=%s Level 2 CA" % tmpdir.basename)  # Should not raise
    index_ca_3 = stdout_lines.index("CN=%s Level 3 CA [END ENTITY ISSUING CA]" % tmpdir.basename)  # Should not raise
    full_chain = stdout_lines.index("Full certificate chain: .gimmecert/ca/chain-full.cert.pem")  # Shold not raise

    assert full_chain > index_ca_3 > index_ca_2 > index_ca_1, "Output ordering for CA section is wrong:\n%s" % stdout

    ca_1_validity = stdout_lines[index_ca_1 + 1]
    ca_1_certificate_path = stdout_lines[index_ca_1 + 2]

    ca_2_validity = stdout_lines[index_ca_2 + 1]
    ca_2_certificate_path = stdout_lines[index_ca_2 + 2]

    ca_3_validity = stdout_lines[index_ca_3 + 1]
    ca_3_certificate_path = stdout_lines[index_ca_3 + 2]

    assert ca_1_validity == "    Validity: 2018-01-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert ca_1_certificate_path == "    Certificate: .gimmecert/ca/level1.cert.pem"

    assert ca_2_validity == "    Validity: 2018-01-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert ca_2_certificate_path == "    Certificate: .gimmecert/ca/level2.cert.pem"

    assert ca_3_validity == "    Validity: 2018-01-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert ca_3_certificate_path == "    Certificate: .gimmecert/ca/level3.cert.pem"


def test_status_reports_server_certificate_information(tmpdir):
    depth = 3

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    with freeze_time('2018-02-01 00:15:00'):
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver1', None)

    with freeze_time('2018-03-01 00:15:00'):
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver2', ['myservice1.example.com', 'myservice2.example.com'])

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stdout_lines = stdout.split("\n")
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "Server certificates\n-------------------\n" in stdout

    index_myserver1 = stdout_lines.index("CN=myserver1")  # Should not raise
    index_myserver2 = stdout_lines.index("CN=myserver2")  # Should not raise

    myserver1_validity = stdout_lines[index_myserver1 + 1]
    myserver1_dns = stdout_lines[index_myserver1 + 2]
    myserver1_private_key_path = stdout_lines[index_myserver1 + 3]
    myserver1_certificate_path = stdout_lines[index_myserver1 + 4]

    myserver2_validity = stdout_lines[index_myserver2 + 1]
    myserver2_dns = stdout_lines[index_myserver2 + 2]
    myserver2_private_key_path = stdout_lines[index_myserver2 + 3]
    myserver2_certificate_path = stdout_lines[index_myserver2 + 4]

    assert myserver1_validity == "    Validity: 2018-02-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myserver1_dns == "    DNS: myserver1"
    assert myserver1_private_key_path == "    Private key: .gimmecert/server/myserver1.key.pem"
    assert myserver1_certificate_path == "    Certificate: .gimmecert/server/myserver1.cert.pem"

    assert myserver2_validity == "    Validity: 2018-03-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myserver2_dns == "    DNS: myserver2, myservice1.example.com, myservice2.example.com"
    assert myserver2_private_key_path == "    Private key: .gimmecert/server/myserver2.key.pem"
    assert myserver2_certificate_path == "    Certificate: .gimmecert/server/myserver2.cert.pem"


def test_status_reports_client_certificate_information(tmpdir):
    depth = 3

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    with freeze_time('2018-02-01 00:15:00'):
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient1')

    with freeze_time('2018-03-01 00:15:00'):
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient2')

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stdout_lines = stdout.split("\n")
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "Client certificates\n-------------------\n" in stdout

    index_myclient1 = stdout_lines.index("CN=myclient1")  # Should not raise
    index_myclient2 = stdout_lines.index("CN=myclient2")  # Should not raise

    myclient1_validity = stdout_lines[index_myclient1 + 1]
    myclient1_private_key_path = stdout_lines[index_myclient1 + 2]
    myclient1_certificate_path = stdout_lines[index_myclient1 + 3]

    myclient2_validity = stdout_lines[index_myclient2 + 1]
    myclient2_private_key_path = stdout_lines[index_myclient2 + 2]
    myclient2_certificate_path = stdout_lines[index_myclient2 + 3]

    assert myclient1_validity == "    Validity: 2018-02-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myclient1_private_key_path == "    Private key: .gimmecert/client/myclient1.key.pem"
    assert myclient1_certificate_path == "    Certificate: .gimmecert/client/myclient1.cert.pem"

    assert myclient2_validity == "    Validity: 2018-03-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myclient2_private_key_path == "    Private key: .gimmecert/client/myclient2.key.pem"
    assert myclient2_certificate_path == "    Certificate: .gimmecert/client/myclient2.cert.pem"


def test_status_reports_no_server_certificates_were_issued(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Just create some sample data, but no server certificates.
    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient1')
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient2')

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stdout_lines = stdout.split("\n")
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "Server certificates\n-------------------\n\nNo server certificates have been issued." in stdout, "Missing message about no server certificates being issued:\n%s" % stdout


def test_status_reports_no_client_certificates_were_issued(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Just create some sample data, but no client certificates.
    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver1', None)
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver2', None)

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stdout_lines = stdout.split("\n")
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "Client certificates\n-------------------\n\nNo client certificates have been issued." in stdout, "Missing message about no client certificates being issued:\n%s" % stdout
