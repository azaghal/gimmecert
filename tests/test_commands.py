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
import sys

import cryptography.x509

import gimmecert.commands

import pytest
from unittest import mock
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
    status_code = gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)

    assert isinstance(status_code, int)


def test_server_reports_error_if_directory_is_not_initialised(tmpdir):

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, tmpdir.strpath, 'myserver', None, None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert "must be initialised" in stderr
    assert stdout == ""
    assert status_code == gimmecert.commands.ExitCode.ERROR_NOT_INITIALISED


@pytest.mark.parametrize(
    "entity_name, custom_csr_path, strings_expected_in_output, strings_not_expected_in_output",
    [
        # New server certificate, generate private key.
        ("myserver", None,
         [".gimmecert/server/myserver.key.pem", ".gimmecert/server/myserver.cert.pem"],
         [".gimmecert/server/myserver.csr.pem"]),

        # New server certificate, use custom CSR.
        ("myserver", "custom_csr/mycustom.csr.pem",
         [".gimmecert/server/myserver.cert.pem", ".gimmecert/server/myserver.csr.pem"],
         [".gimmecert/server/myserver.key.pem"]),
    ]
)
def test_server_reports_success_and_outputs_correct_information(sample_project_directory, key_with_csr,
                                                                entity_name, custom_csr_path,
                                                                strings_expected_in_output, strings_not_expected_in_output):
    """
    Tests if the server command reports success and outputs correct
    information for user.

    Test is parametrised in order to avoid code duplication.

    Tests have been designed to cater to different output depending on
    whether the CSR was passed-in or not.

    For each variation we have lines we expect in standard output, and
    lines which we expect _not_ to be in standard output. E.g. if
    private key was generated by Gimmecert, we don't expect to see
    information about the CSR and vice-versa.
    """

    sample_project_directory.chdir()

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.server(stdout_stream, stderr_stream,
                                            sample_project_directory.strpath, entity_name, None,
                                            custom_csr_path)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""

    for expected in strings_expected_in_output:
        assert expected in stdout

    for not_expected in strings_not_expected_in_output:
        assert not_expected not in stdout


def test_server_outputs_private_key_to_file_without_csr(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem')
    csr_file = tmpdir.join('.gimmecert', 'server', 'myserver.csr.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)

    assert private_key_file.check(file=1)
    assert not csr_file.check()

    private_key_file_content = private_key_file.read()

    assert private_key_file_content.startswith('-----BEGIN RSA PRIVATE KEY')
    assert private_key_file_content.endswith('END RSA PRIVATE KEY-----\n')


def test_server_outputs_certificate_to_file(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem')
    csr_file = tmpdir.join('.gimmecert', 'client', 'myclient.csr.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)

    assert certificate_file.check(file=1)
    assert not csr_file.check()

    certificate_file_content = certificate_file.read()

    assert certificate_file_content.startswith('-----BEGIN CERTIFICATE')
    assert certificate_file_content.endswith('END CERTIFICATE-----\n')


def test_server_errors_out_if_certificate_already_issued(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Previous run.
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)
    existing_private_key = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem').read()
    certificate = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem').read()

    # New run.
    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, tmpdir.strpath, 'myserver', None, None)

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

    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath, 'myclient', None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert "must be initialised" in stderr
    assert stdout == ""
    assert status_code == gimmecert.commands.ExitCode.ERROR_NOT_INITIALISED


def test_client_returns_status_code(tmpdir):
    status_code = gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)

    assert isinstance(status_code, int)


def test_client_reports_success_and_paths_to_generated_artifacts(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath, 'myclient', None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "certificate issued" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert ".gimmecert/client/myclient.csr.pem" not in stdout
    assert stderr == ""


def test_client_outputs_private_key_to_file_without_csr(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'client', 'myclient.key.pem')
    csr_file = tmpdir.join('.gimmecert', 'client', 'myclient.csr.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)

    assert private_key_file.check(file=1)
    assert not csr_file.check()

    private_key_file_content = private_key_file.read()

    assert private_key_file_content.startswith('-----BEGIN RSA PRIVATE KEY')
    assert private_key_file_content.endswith('END RSA PRIVATE KEY-----\n')


def test_client_outputs_certificate_to_file(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)

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
    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)
    existing_private_key = tmpdir.join('.gimmecert', 'client', 'myclient.key.pem').read()
    certificate = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem').read()

    # New run.
    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath, 'myclient', None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED
    assert "already been issued" in stderr
    assert "client myclient" in stderr
    assert stdout == ""
    assert tmpdir.join('.gimmecert', 'client', 'myclient.key.pem').read() == existing_private_key
    assert tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem').read() == certificate


def test_renew_returns_status_code(tmpdir):
    tmpdir.chdir()

    status_code = gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', False, None, None)

    assert isinstance(status_code, int)


def test_renew_reports_error_if_directory_is_not_initialised(tmpdir):

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', False, None, None)

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

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', False, None, None)

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

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'client', 'myclient', False, None, None)

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
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', False, None, None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Renewed certificate for server myserver." in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.csr.pem" not in stdout
    assert stderr == ""


def test_renew_reports_success_and_paths_to_client_artifacts(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'client', 'myclient', False, None, None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Renewed certificate for client myclient." in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.csr.pem" not in stdout
    assert stderr == ""


def test_renew_keeps_server_private_key(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)
    private_key_after_issuance = private_key_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', False, None, None)
    private_key_after_renewal = private_key_file.read()

    assert private_key_after_issuance == private_key_after_renewal


def test_renew_keeps_client_private_key(tmpdir):
    depth = 1
    private_key_file = tmpdir.join('.gimmecert', 'client', 'myclient.key.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)
    private_key_after_issuance = private_key_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'client', 'myclient', False, None, None)
    private_key_after_renewal = private_key_file.read()

    assert private_key_after_issuance == private_key_after_renewal


def test_renew_replaces_server_certificate(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)
    certificate_after_issuance = certificate_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', False, None, None)
    certificate_after_renewal = certificate_file.read()

    assert certificate_after_issuance != certificate_after_renewal
    assert certificate_after_renewal.startswith('-----BEGIN CERTIFICATE')
    assert certificate_after_renewal.endswith('END CERTIFICATE-----\n')


def test_renew_replaces_client_certificate(tmpdir):
    depth = 1
    certificate_file = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)
    certificate_after_issuance = certificate_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'client', 'myclient', False, None, None)
    certificate_after_renewal = certificate_file.read()

    assert certificate_after_issuance != certificate_after_renewal
    assert certificate_after_renewal.startswith('-----BEGIN CERTIFICATE')
    assert certificate_after_renewal.endswith('END CERTIFICATE-----\n')


def test_renew_reports_success_and_paths_to_server_artifacts_with_new_key(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', True, None, None)

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

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)
    private_key_after_issuance = private_key_file.read()

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', True, None, None)
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

    myserver3_csr_file = tmpdir.join('server3.csr.pem')
    myserver3_private_key = gimmecert.crypto.generate_private_key()
    myserver3_csr = gimmecert.crypto.generate_csr('blah', myserver3_private_key)
    gimmecert.storage.write_csr(myserver3_csr, myserver3_csr_file.strpath)

    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    with freeze_time('2018-02-01 00:15:00'):
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver1', None, None)

    with freeze_time('2018-03-01 00:15:00'):
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver2', ['myservice1.example.com', 'myservice2.example.com'], None)

    with freeze_time('2018-04-01 00:15:00'):
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver3', None, myserver3_csr_file.strpath)

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stdout_lines = stdout.split("\n")
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "Server certificates\n-------------------\n" in stdout
    assert "No server certificates" not in stdout

    index_myserver1 = stdout_lines.index("CN=myserver1")  # Should not raise
    index_myserver2 = stdout_lines.index("CN=myserver2")  # Should not raise
    index_myserver3 = stdout_lines.index("CN=myserver3")  # Should not raise

    myserver1_validity = stdout_lines[index_myserver1 + 1]
    myserver1_dns = stdout_lines[index_myserver1 + 2]
    myserver1_private_key_path = stdout_lines[index_myserver1 + 3]
    myserver1_certificate_path = stdout_lines[index_myserver1 + 4]

    myserver2_validity = stdout_lines[index_myserver2 + 1]
    myserver2_dns = stdout_lines[index_myserver2 + 2]
    myserver2_private_key_path = stdout_lines[index_myserver2 + 3]
    myserver2_certificate_path = stdout_lines[index_myserver2 + 4]

    myserver3_validity = stdout_lines[index_myserver3 + 1]
    myserver3_dns = stdout_lines[index_myserver3 + 2]
    myserver3_csr_path = stdout_lines[index_myserver3 + 3]
    myserver3_certificate_path = stdout_lines[index_myserver3 + 4]

    assert myserver1_validity == "    Validity: 2018-02-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myserver1_dns == "    DNS: myserver1"
    assert myserver1_private_key_path == "    Private key: .gimmecert/server/myserver1.key.pem"
    assert myserver1_certificate_path == "    Certificate: .gimmecert/server/myserver1.cert.pem"

    assert myserver2_validity == "    Validity: 2018-03-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myserver2_dns == "    DNS: myserver2, myservice1.example.com, myservice2.example.com"
    assert myserver2_private_key_path == "    Private key: .gimmecert/server/myserver2.key.pem"
    assert myserver2_certificate_path == "    Certificate: .gimmecert/server/myserver2.cert.pem"

    assert myserver3_validity == "    Validity: 2018-04-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myserver3_dns == "    DNS: myserver3"
    assert myserver3_csr_path == "    CSR: .gimmecert/server/myserver3.csr.pem"
    assert myserver3_certificate_path == "    Certificate: .gimmecert/server/myserver3.cert.pem"


def test_status_reports_client_certificate_information(tmpdir):
    depth = 3

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    myclient3_csr_file = tmpdir.join('client3.csr.pem')
    myclient3_private_key = gimmecert.crypto.generate_private_key()
    myclient3_csr = gimmecert.crypto.generate_csr('blah', myclient3_private_key)
    gimmecert.storage.write_csr(myclient3_csr, myclient3_csr_file.strpath)

    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    with freeze_time('2018-02-01 00:15:00'):
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient1', None)

    with freeze_time('2018-03-01 00:15:00'):
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient2', None)

    with freeze_time('2018-04-01 00:15:00'):
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient3', myclient3_csr_file.strpath)

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stdout_lines = stdout.split("\n")
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "Client certificates\n-------------------\n" in stdout
    assert "No client certificates" not in stdout

    index_myclient1 = stdout_lines.index("CN=myclient1")  # Should not raise
    index_myclient2 = stdout_lines.index("CN=myclient2")  # Should not raise
    index_myclient3 = stdout_lines.index("CN=myclient3")  # Should not raise

    myclient1_validity = stdout_lines[index_myclient1 + 1]
    myclient1_private_key_path = stdout_lines[index_myclient1 + 2]
    myclient1_certificate_path = stdout_lines[index_myclient1 + 3]

    myclient2_validity = stdout_lines[index_myclient2 + 1]
    myclient2_private_key_path = stdout_lines[index_myclient2 + 2]
    myclient2_certificate_path = stdout_lines[index_myclient2 + 3]

    myclient3_validity = stdout_lines[index_myclient3 + 1]
    myclient3_csr_path = stdout_lines[index_myclient3 + 2]
    myclient3_certificate_path = stdout_lines[index_myclient3 + 3]

    assert myclient1_validity == "    Validity: 2018-02-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myclient1_private_key_path == "    Private key: .gimmecert/client/myclient1.key.pem"
    assert myclient1_certificate_path == "    Certificate: .gimmecert/client/myclient1.cert.pem"

    assert myclient2_validity == "    Validity: 2018-03-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myclient2_private_key_path == "    Private key: .gimmecert/client/myclient2.key.pem"
    assert myclient2_certificate_path == "    Certificate: .gimmecert/client/myclient2.cert.pem"

    assert myclient3_validity == "    Validity: 2018-04-01 00:00:00 UTC - 2019-01-01 00:15:00 UTC"
    assert myclient3_csr_path == "    CSR: .gimmecert/client/myclient3.csr.pem"
    assert myclient3_certificate_path == "    Certificate: .gimmecert/client/myclient3.cert.pem"


def test_status_reports_no_server_certificates_were_issued(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Just create some sample data, but no server certificates.
    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient1', None)
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient2', None)

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "Server certificates\n-------------------\n\nNo server certificates have been issued." in stdout, \
        "Missing message about no server certificates being issued:\n%s" % stdout


def test_status_reports_no_client_certificates_were_issued(tmpdir):
    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Just create some sample data, but no client certificates.
    with freeze_time('2018-01-01 00:15:00'):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver1', None, None)
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver2', None, None)

    status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""
    assert "Client certificates\n-------------------\n\nNo client certificates have been issued." in stdout, \
        "Missing message about no client certificates being issued:\n%s" % stdout


@pytest.mark.parametrize("subject_dn_line", [
    "CN=My Project Level 1 CA [END ENTITY ISSUING CA]",
    "CN=myserver",
    "CN=myclient",
])
@pytest.mark.parametrize("issuance_date, status_date, validity_status", [
    ("2018-01-01 00:15:00", "2018-06-01 00:00:00", ""),
    ("2018-01-01 00:15:00", "2017-01-01 00:15:00", " [NOT VALID YET]"),
    ("2018-01-01 00:15:00", "2020-01-01 00:15:00", " [EXPIRED]"),
])
def test_certificate_marked_as_not_valid_or_expired_as_appropriate(tmpdir, subject_dn_line, issuance_date, status_date, validity_status):
    """
    Tests if various certificates (CA, server, client) are marked and
    valid/invalid in terms of validity dates.

    The test has been parametrised since the pattern is pretty similar
    between these.
    """

    depth = 1

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Perform action on our fixed issuance date.
    with freeze_time(issuance_date):
        gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, "My Project", depth)
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)

    # Move to specific date in future/past for different validity checks.
    with freeze_time(status_date):
        status_code = gimmecert.commands.status(stdout_stream, stderr_stream, tmpdir.strpath)

    stdout = stdout_stream.getvalue()
    stdout_lines = stdout.split("\n")
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert stderr == ""

    index_dn = stdout_lines.index(subject_dn_line)  # Should not raise
    validity = stdout_lines[index_dn + 1]

    assert validity.endswith(validity_status)


def test_client_reports_success_and_paths_to_generated_artifacts_with_csr(tmpdir):
    depth = 1
    custom_csr_file = tmpdir.join('mycustom.csr.pem')

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    private_key = gimmecert.crypto.generate_private_key()
    custom_csr = gimmecert.crypto.generate_csr('blah', private_key)
    gimmecert.storage.write_csr(custom_csr, custom_csr_file.strpath)

    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath, 'myclient', custom_csr_file.strpath)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "certificate issued" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.csr.pem" in stdout
    assert ".gimmecert/client/myclient.key.pem" not in stdout
    assert stderr == ""


def test_client_outputs_passed_in_csr_to_file_without_private_key(tmpdir):
    depth = 1

    private_key_file = tmpdir.join('.gimmecert', 'client', 'myclient.key.pem')
    csr_file = tmpdir.join('.gimmecert', 'client', 'myclient.csr.pem')
    custom_csr_file = tmpdir.join('mycustom.csr.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr('mycustomcsr', private_key)
    gimmecert.storage.write_csr(csr, custom_csr_file.strpath)
    custom_csr_file_content = custom_csr_file.read()

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', custom_csr_file.strpath)

    assert csr_file.check(file=1)
    assert not private_key_file.check()

    csr_file_content = csr_file.read()

    assert csr_file_content == custom_csr_file_content


def test_client_uses_correct_public_key_without_csr(tmpdir):
    depth = 1

    private_key_file = tmpdir.join('.gimmecert', 'client', 'myclient.key.pem')
    certificate_file = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', None)

    private_key = gimmecert.storage.read_private_key(private_key_file.strpath)
    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)

    private_key_public_numbers = private_key.public_key().public_numbers()
    certificate_public_numbers = certificate.public_key().public_numbers()

    assert certificate_public_numbers == private_key_public_numbers


def test_client_uses_correct_public_key_but_no_naming_with_csr(tmpdir):
    depth = 1

    custom_csr_file = tmpdir.join('customcsr.pem')
    certificate_file = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem')

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr('mycustomcsr', private_key)
    gimmecert.storage.write_csr(csr, custom_csr_file.strpath)

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', custom_csr_file.strpath)

    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)

    csr_public_numbers = csr.public_key().public_numbers()
    certificate_public_numbers = certificate.public_key().public_numbers()

    assert certificate_public_numbers == csr_public_numbers
    assert csr.subject != certificate.subject


def test_server_outputs_passed_in_csr_to_file_without_private_key(tmpdir):
    depth = 1

    private_key_file = tmpdir.join('.gimmecert', 'server', 'myserver.key.pem')
    csr_file = tmpdir.join('.gimmecert', 'server', 'myserver.csr.pem')
    custom_csr_file = tmpdir.join('mycustom.csr.pem')

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr('mycustomcsr', private_key)
    gimmecert.storage.write_csr(csr, custom_csr_file.strpath)
    custom_csr_file_content = custom_csr_file.read()

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, custom_csr_file.strpath)

    assert csr_file.check(file=1)
    assert not private_key_file.check()

    csr_file_content = csr_file.read()

    assert csr_file_content == custom_csr_file_content


def test_server_uses_correct_public_key_but_no_naming_with_csr(tmpdir):
    depth = 1

    custom_csr_file = tmpdir.join('customcsr.pem')
    certificate_file = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem')

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr('mycustomcsr', private_key)
    gimmecert.storage.write_csr(csr, custom_csr_file.strpath)

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, custom_csr_file.strpath)

    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)

    csr_public_numbers = csr.public_key().public_numbers()
    certificate_public_numbers = certificate.public_key().public_numbers()

    assert certificate_public_numbers == csr_public_numbers
    assert csr.subject != certificate.subject


def test_client_errors_out_if_certificate_already_issued_with_csr(tmpdir):
    depth = 1

    custom_csr_file = tmpdir.join('mycustom.csr.pem')

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr('mycustomcsr', private_key)
    gimmecert.storage.write_csr(csr, custom_csr_file.strpath)

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Previous run.
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', custom_csr_file.strpath)
    existing_csr = tmpdir.join('.gimmecert', 'client', 'myclient.csr.pem').read()
    certificate = tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem').read()

    # New run.
    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, tmpdir.strpath, 'myclient', custom_csr_file.strpath)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED
    assert "already been issued" in stderr
    assert "client myclient" in stderr
    assert stdout == ""
    assert tmpdir.join('.gimmecert', 'client', 'myclient.csr.pem').read() == existing_csr
    assert tmpdir.join('.gimmecert', 'client', 'myclient.cert.pem').read() == certificate


def test_server_errors_out_if_certificate_already_issued_with_csr(tmpdir):
    depth = 1

    custom_csr_file = tmpdir.join('mycustom.csr.pem')

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr('mycustomcsr', private_key)
    gimmecert.storage.write_csr(csr, custom_csr_file.strpath)

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    # Previous run.
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, custom_csr_file.strpath)
    existing_csr = tmpdir.join('.gimmecert', 'server', 'myserver.csr.pem').read()
    certificate = tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem').read()

    # New run.
    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, tmpdir.strpath, 'myserver', None, custom_csr_file.strpath)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED
    assert "already been issued" in stderr
    assert "server myserver" in stderr
    assert stdout == ""
    assert tmpdir.join('.gimmecert', 'server', 'myserver.csr.pem').read() == existing_csr
    assert tmpdir.join('.gimmecert', 'server', 'myserver.cert.pem').read() == certificate


def test_renew_reports_success_and_paths_to_server_artifacts_with_csr(tmpdir):
    depth = 1

    csr_file = tmpdir.join("mycustom.csr.pem")

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr("mytest", private_key)
    gimmecert.storage.write_csr(csr, csr_file.strpath)

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, csr_file.strpath)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', False, None, None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Renewed certificate for server myserver." in stdout
    assert ".gimmecert/server/myserver.csr.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.key.pem" not in stdout
    assert stderr == ""


def test_renew_reports_success_and_paths_to_client_artifacts_with_csr(tmpdir):
    depth = 1

    csr_file = tmpdir.join("mycustom.csr.pem")

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr("mytest", private_key)
    gimmecert.storage.write_csr(csr, csr_file.strpath)

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myclient', csr_file.strpath)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'client', 'myclient', False, None, None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Renewed certificate for client myclient." in stdout
    assert ".gimmecert/client/myclient.csr.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.key.pem" not in stdout
    assert stderr == ""


def test_renew_reports_success_and_paths_to_server_artifacts_with_csr_when_replacing_private_key(tmpdir):
    depth = 1

    csr_file = tmpdir.join("mycustom.csr.pem")

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    private_key = gimmecert.crypto.generate_private_key()
    csr = gimmecert.crypto.generate_csr("mytest", private_key)
    gimmecert.storage.write_csr(csr, csr_file.strpath)

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', False, csr_file.strpath, None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Renewed certificate for server myserver." in stdout
    assert "removed" in stdout
    assert "replaced" in stdout
    assert ".gimmecert/server/myserver.csr.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.key.pem" not in stdout
    assert stderr == ""


def test_renew_replaces_server_private_key_with_csr(tmpdir):
    depth = 1

    custom_csr_file = tmpdir.join("mycustom.csr.pem")
    csr_file = tmpdir.join(".gimmecert", "server", "myserver.csr.pem")
    certificate_file = tmpdir.join(".gimmecert", "server", "myserver.cert.pem")
    private_key_file = tmpdir.join(".gimmecert", "server", "myserver.key.pem")

    custom_csr_private_key = gimmecert.crypto.generate_private_key()
    custom_csr = gimmecert.crypto.generate_csr("mycustom", custom_csr_private_key)
    gimmecert.storage.write_csr(custom_csr, custom_csr_file.strpath)
    custom_csr_file_content = custom_csr_file.read()

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, None)

    assert private_key_file.check(file=1)

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', False, custom_csr_file.strpath, None)

    assert csr_file.check(file=1)

    csr_file_content = csr_file.read()

    csr = gimmecert.storage.read_csr(csr_file.strpath)
    csr_public_numbers = csr.public_key().public_numbers()
    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)
    certificate_public_numbers = certificate.public_key().public_numbers()

    assert csr_file_content == custom_csr_file_content
    assert not private_key_file.check()
    assert certificate_public_numbers == csr_public_numbers


def test_renew_raises_exception_if_both_new_private_key_generation_and_csr_are_passed_in(tmpdir):
    depth = 1

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)

    custom_csr_file = tmpdir.join("mycustom.csr.pem")

    custom_csr_private_key = gimmecert.crypto.generate_private_key()
    custom_csr = gimmecert.crypto.generate_csr("mycustom", custom_csr_private_key)
    gimmecert.storage.write_csr(custom_csr, custom_csr_file.strpath)

    with pytest.raises(gimmecert.commands.InvalidCommandInvocation) as e_info:
        gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', True, custom_csr_file.strpath, None)

    assert str(e_info.value) == "Only one of the following two parameters should be specified: generate_new_private_key, custom_csr_path."


def test_renew_raises_exception_if_update_dns_names_is_used_for_client_certificate(sample_project_directory):

    with pytest.raises(gimmecert.commands.InvalidCommandInvocation) as e_info:
        gimmecert.commands.renew(io.StringIO(), io.StringIO(), sample_project_directory.strpath,
                                 'client', 'client-with-privkey-1',
                                 False, None, ["myservice.example.com"])

    assert str(e_info.value) == "Updating DNS subject alternative names can be done only for server certificates."


def test_renew_reports_success_and_paths_to_server_artifacts_with_private_key_when_replacing_csr(tmpdir):
    depth = 1

    custom_csr_file = tmpdir.join("mycustom.csr.pem")

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    custom_private_key = gimmecert.crypto.generate_private_key()
    custom_csr = gimmecert.crypto.generate_csr("mytest", custom_private_key)
    gimmecert.storage.write_csr(custom_csr, custom_csr_file.strpath)

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, custom_csr_file.strpath)

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, tmpdir.strpath, 'server', 'myserver', True, None, None)

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "Generated new private key and renewed certificate for server myserver." in stdout
    assert "removed" in stdout
    assert "generated" in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.csr.pem" not in stdout
    assert stderr == ""


@pytest.mark.parametrize('entity_name,key_or_csr',
                         [('server-with-privkey-1', 'key'),
                          ('server-with-csr-1', 'csr')])
def test_renew_reports_success_and_paths_to_artifacts_when_renewing_server_certificate_with_dns_names(sample_project_directory, entity_name, key_or_csr):
    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream,
                                           sample_project_directory.strpath,
                                           'server', entity_name,
                                           False, None, ["myservice.example.com"])

    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()

    assert status_code == gimmecert.commands.ExitCode.SUCCESS
    assert "DNS subject alternative names have been updated." in stdout
    assert ".gimmecert/server/%s.%s.pem" % (entity_name, key_or_csr) in stdout
    assert ".gimmecert/server/%s.cert.pem" % entity_name in stdout
    assert stderr == ""


def test_renew_replaces_dns_names(tmpdir):
    certificate_file = tmpdir.join(".gimmecert", "server", "myserver.cert.pem")

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, 1)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', ['myservice1.local', 'myservice2.local'], None)

    old_certificate_pem = certificate_file.read()
    old_certificate = gimmecert.storage.read_certificate(certificate_file.strpath)
    old_subject_alt_name = old_certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).value

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath,
                             'server', 'myserver',
                             False, None, ["myservice1.example.com", "myservice2.example.com"])

    new_certificate_pem = certificate_file.read()
    new_certificate = gimmecert.storage.read_certificate(certificate_file.strpath)
    new_subject_alt_name = new_certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).value

    expected_subject_alt_name = cryptography.x509.SubjectAlternativeName([
        cryptography.x509.DNSName(dns_name) for dns_name in ['myserver', 'myservice1.example.com', 'myservice2.example.com']])

    assert new_certificate_pem != old_certificate_pem
    assert old_subject_alt_name != new_subject_alt_name
    assert new_subject_alt_name == expected_subject_alt_name


def test_renew_removes_dns_names(tmpdir):
    certificate_file = tmpdir.join(".gimmecert", "server", "myserver.cert.pem")

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, 1)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', ['myservice1.local', 'myservice2.local'], None)

    old_certificate_pem = certificate_file.read()
    old_certificate = gimmecert.storage.read_certificate(certificate_file.strpath)
    old_subject_alt_name = old_certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).value

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', False, None, [])

    new_certificate_pem = certificate_file.read()
    new_certificate = gimmecert.storage.read_certificate(certificate_file.strpath)
    new_subject_alt_name = new_certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).value

    expected_subject_alt_name = cryptography.x509.SubjectAlternativeName([
        cryptography.x509.DNSName(dns_name) for dns_name in ['myserver']])

    assert new_certificate_pem != old_certificate_pem
    assert old_subject_alt_name != new_subject_alt_name
    assert new_subject_alt_name == expected_subject_alt_name


def test_renew_replaces_server_csr_with_private_key(tmpdir):
    depth = 1

    custom_csr_file = tmpdir.join("mycustom.csr.pem")
    csr_file = tmpdir.join(".gimmecert", "server", "myserver.csr.pem")
    certificate_file = tmpdir.join(".gimmecert", "server", "myserver.cert.pem")
    private_key_file = tmpdir.join(".gimmecert", "server", "myserver.key.pem")

    custom_csr_private_key = gimmecert.crypto.generate_private_key()
    custom_csr = gimmecert.crypto.generate_csr("mycustom", custom_csr_private_key)
    gimmecert.storage.write_csr(custom_csr, custom_csr_file.strpath)

    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, depth)
    gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, 'myserver', None, custom_csr_file.strpath)

    assert csr_file.check(file=1)

    gimmecert.commands.renew(io.StringIO(), io.StringIO(), tmpdir.strpath, 'server', 'myserver', True, None, None)

    assert private_key_file.check(file=1)

    private_key = gimmecert.storage.read_private_key(private_key_file.strpath)
    private_key_public_numbers = private_key.public_key().public_numbers()
    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)
    certificate_public_numbers = certificate.public_key().public_numbers()

    assert not csr_file.check()
    assert certificate_public_numbers == private_key_public_numbers


@mock.patch('gimmecert.utils.read_input')
def test_server_reads_csr_from_stdin(mock_read_input, sample_project_directory, key_with_csr):
    entity_name = 'myserver'
    stored_csr_file = sample_project_directory.join('.gimmecert', 'server', '%s.csr.pem' % entity_name)
    certificate_file = sample_project_directory.join('.gimmecert', 'server', '%s.cert.pem' % entity_name)

    # Mock our util for reading input from user.
    mock_read_input.return_value = key_with_csr.csr_pem

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.server(stdout_stream, stderr_stream, sample_project_directory.strpath, entity_name, None, '-')
    assert status_code == 0

    # Read stored/generated artefacts.
    stored_csr = gimmecert.storage.read_csr(stored_csr_file.strpath)
    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)

    custom_csr_public_numbers = key_with_csr.csr.public_key().public_numbers()
    stored_csr_public_numbers = stored_csr.public_key().public_numbers()
    certificate_public_numbers = certificate.public_key().public_numbers()

    mock_read_input.assert_called_once_with(sys.stdin, stderr_stream, "Please enter the CSR")
    assert stored_csr_public_numbers == custom_csr_public_numbers
    assert certificate_public_numbers == custom_csr_public_numbers
    assert certificate.subject != key_with_csr.csr.subject


@mock.patch('gimmecert.utils.read_input')
def test_client_reads_csr_from_stdin(mock_read_input, sample_project_directory, key_with_csr):
    entity_name = 'myclient'
    stored_csr_file = sample_project_directory.join('.gimmecert', 'client', '%s.csr.pem' % entity_name)
    certificate_file = sample_project_directory.join('.gimmecert', 'client', '%s.cert.pem' % entity_name)

    # Mock our util for reading input from user.
    mock_read_input.return_value = key_with_csr.csr_pem

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.client(stdout_stream, stderr_stream, sample_project_directory.strpath, entity_name, '-')
    assert status_code == 0

    # Read stored/generated artefacts.
    stored_csr = gimmecert.storage.read_csr(stored_csr_file.strpath)
    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)

    custom_csr_public_numbers = key_with_csr.csr.public_key().public_numbers()
    stored_csr_public_numbers = stored_csr.public_key().public_numbers()
    certificate_public_numbers = certificate.public_key().public_numbers()

    mock_read_input.assert_called_once_with(sys.stdin, stderr_stream, "Please enter the CSR")
    assert stored_csr_public_numbers == custom_csr_public_numbers
    assert certificate_public_numbers == custom_csr_public_numbers
    assert certificate.subject != key_with_csr.csr.subject


@mock.patch('gimmecert.utils.read_input')
def test_renew_server_reads_csr_from_stdin(mock_read_input, sample_project_directory, key_with_csr):
    entity_name = 'myserver'
    stored_csr_file = sample_project_directory.join('.gimmecert', 'server', '%s.csr.pem' % entity_name)
    certificate_file = sample_project_directory.join('.gimmecert', 'server', '%s.cert.pem' % entity_name)

    # Generate server certificate that will be renewed.
    gimmecert.commands.server(io.StringIO(), io.StringIO(), sample_project_directory.strpath, entity_name, None, None)

    # Mock our util for reading input from user.
    mock_read_input.return_value = key_with_csr.csr_pem

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, sample_project_directory.strpath, "server", entity_name, False, '-', None)
    assert status_code == 0

    # Read stored/generated artefacts.
    stored_csr = gimmecert.storage.read_csr(stored_csr_file.strpath)
    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)

    custom_csr_public_numbers = key_with_csr.csr.public_key().public_numbers()
    stored_csr_public_numbers = stored_csr.public_key().public_numbers()
    certificate_public_numbers = certificate.public_key().public_numbers()

    mock_read_input.assert_called_once_with(sys.stdin, stderr_stream, "Please enter the CSR")
    assert stored_csr_public_numbers == custom_csr_public_numbers
    assert certificate_public_numbers == custom_csr_public_numbers
    assert certificate.subject != key_with_csr.csr.subject


@mock.patch('gimmecert.utils.read_input')
def test_renew_client_reads_csr_from_stdin(mock_read_input, sample_project_directory, key_with_csr):
    entity_name = 'myclient'
    stored_csr_file = sample_project_directory.join('.gimmecert', 'client', '%s.csr.pem' % entity_name)
    certificate_file = sample_project_directory.join('.gimmecert', 'client', '%s.cert.pem' % entity_name)

    # Generate client certificate that will be renewed.
    gimmecert.commands.client(io.StringIO(), io.StringIO(), sample_project_directory.strpath, entity_name, None)

    # Mock our util for reading input from user.
    mock_read_input.return_value = key_with_csr.csr_pem

    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()

    status_code = gimmecert.commands.renew(stdout_stream, stderr_stream, sample_project_directory.strpath, "client", entity_name, False, '-', None)
    assert status_code == 0

    # Read stored/generated artefacts.
    stored_csr = gimmecert.storage.read_csr(stored_csr_file.strpath)
    certificate = gimmecert.storage.read_certificate(certificate_file.strpath)

    custom_csr_public_numbers = key_with_csr.csr.public_key().public_numbers()
    stored_csr_public_numbers = stored_csr.public_key().public_numbers()
    certificate_public_numbers = certificate.public_key().public_numbers()

    mock_read_input.assert_called_once_with(sys.stdin, stderr_stream, "Please enter the CSR")
    assert stored_csr_public_numbers == custom_csr_public_numbers
    assert certificate_public_numbers == custom_csr_public_numbers
    assert certificate.subject != key_with_csr.csr.subject
