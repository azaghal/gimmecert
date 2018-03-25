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


from .base import run_command


def test_renew_command_available_with_help():
    # John has been issuing server and client certificates using
    # Gimmecert for a while now. The project has been in use for quite
    # some time, and John has realised the certificates might be about
    # to expire. Thinking how tedious it would be to generate
    # everything again from scratch, he tries to figure out if there
    # is an easier way to do it instead of providing information for
    # all of the entities instead.
    stdout, stderr, exit_code = run_command("gimmecert")

    # Looking at output, John notices the renew command.
    assert exit_code == 0
    assert stderr == ""
    assert "renew" in stdout

    # He goes ahead and has a look at command invocation to check what
    # kind of parameters he might need to provide.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # John can see that the command accepts two positional argument -
    # type of entity, and entity name.
    assert exit_code == 0
    assert stderr == ""
    assert stdout.startswith("usage: gimmecert renew")
    assert stdout.split('\n')[0].endswith("{server,client} entity_name")  # First line of help


def test_renew_command_requires_initialised_hierarchy(tmpdir):
    # John decides it's time to renew one of the certificates. He
    # switches to his project directory.
    tmpdir.chdir()

    # John tries to renew a server certificate.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "myserver")

    # John has forgotten to initialise the CA hierarchy from within
    # this directory, and is instead presented with an error.
    assert exit_code != 0
    assert stdout == ""
    assert stderr == "No CA hierarchy has been initialised yet. Run the gimmecert init command and issue some certificates first.\n"

    # John gives the screen a weird look, and tries again, this time
    # with a client certificate renewal.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "myclient")

    # John gets presented with the same error yet again. Suddenly, he
    # realizes he is in a wrong directory... Oh well...
    assert exit_code != 0
    assert stdout == ""
    assert stderr == "No CA hierarchy has been initialised yet. Run the gimmecert init command and issue some certificates first.\n"


def test_renew_command_reports_error_if_entity_does_not_exist(tmpdir):
    # John finally finds his way around to the project directory where
    # Gimmecert has already been used to set-up a hierarchy, and where
    # a couple of server and client certificates have been issued.
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "someserver")
    run_command("gimmecert", "client", "someclient")

    # He runs the command for renewing a server certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'server', 'myserver')

    # Unfortunately for him, this server certificate has not been
    # issued before, and he is presented with an error.
    assert exit_code != 0
    assert stdout == ''
    assert stderr == "Cannot renew certificate. No existing certificate found for server myserver.\n"

    # This is going to be one of those days... He tries then to renew
    # a client certificate instead.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'client', 'myclient')

    # To his dismay, this results in error as well. He hasn't issued
    # such a certificate before either.
    assert exit_code != 0
    assert stdout == ''
    assert stderr == "Cannot renew certificate. No existing certificate found for client myclient.\n"


def test_renew_command_renews_certificate(tmpdir):
    # At the end of his wits, John finally finds the correct project
    # directory where he has previuosly set-up the CA hierarchy and
    # issued a couple of certificates.
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "myserver", "myserver.local")
    run_command("gimmecert", "client", "myclient")

    # He fetches some information about the existing certificates.
    old_server_private_key = tmpdir.join(".gimmecert", "server", "myserver.key.pem").read()
    old_server_issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/server/myserver.cert.pem')
    old_server_subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/server/myserver.cert.pem')
    old_server_public_key, _, _ = run_command('openssl', 'x509', '-noout', '-pubkey', '-in', '.gimmecert/server/myserver.cert.pem')
    old_server_certificate_info, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver.cert.pem')
    old_server_issuer_dn = old_server_issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    old_server_subject_dn = old_server_subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    old_client_private_key = tmpdir.join(".gimmecert", "client", "myclient.key.pem").read()
    old_client_issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/client/myclient.cert.pem')
    old_client_subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/client/myclient.cert.pem')
    old_client_public_key, _, _ = run_command('openssl', 'x509', '-noout', '-pubkey', '-in', '.gimmecert/client/myclient.cert.pem')
    old_client_certificate_info, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/client/myclient.cert.pem')
    old_client_issuer_dn = old_client_issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    old_client_subject_dn = old_client_subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # He runs the renewal command for server certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'server', 'myserver')

    # No errors are reported, and he is presented with a nice
    # informative message about certificate being renewed, as well as
    # paths to artifacts.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for server myserver." in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout

    # He does the same for the client certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'client', 'myclient')

    # No errors are reported, and he is presented with a nice
    # informative message about certificate being renewed, as well as
    # paths to artifacts.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for client myclient." in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout

    # John has a look at generated certificates.
    new_server_private_key = tmpdir.join(".gimmecert", "server", "myserver.key.pem").read()
    new_server_issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/server/myserver.cert.pem')
    new_server_subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/server/myserver.cert.pem')
    new_server_public_key, _, _ = run_command('openssl', 'x509', '-noout', '-pubkey', '-in', '.gimmecert/server/myserver.cert.pem')
    new_server_certificate_info, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver.cert.pem')
    new_server_issuer_dn = new_server_issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    new_server_subject_dn = new_server_subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    new_client_private_key = tmpdir.join(".gimmecert", "client", "myclient.key.pem").read()
    new_client_issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/client/myclient.cert.pem')
    new_client_subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/client/myclient.cert.pem')
    new_client_public_key, _, _ = run_command('openssl', 'x509', '-noout', '-pubkey', '-in', '.gimmecert/client/myclient.cert.pem')
    new_client_certificate_info, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/client/myclient.cert.pem')
    new_client_issuer_dn = new_client_issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    new_client_subject_dn = new_client_subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # John compares the values from old certificates and new
    # certificates. To his delight, the same private key and naming
    # have been reused, but the certificates have definitively been
    # replaced.
    assert new_server_private_key == old_server_private_key
    assert new_server_issuer_dn == old_server_issuer_dn
    assert new_server_subject_dn == old_server_subject_dn
    assert new_server_public_key == old_server_public_key
    assert "DNS:myserver, DNS:myserver.local\n" in new_server_certificate_info
    assert new_server_certificate_info != old_server_certificate_info

    assert new_client_private_key == old_client_private_key
    assert new_client_issuer_dn == old_client_issuer_dn
    assert new_client_subject_dn == old_client_subject_dn
    assert new_client_public_key == old_client_public_key
    assert new_client_certificate_info != old_client_certificate_info

    # Finally, he runs a check to ensure the certificates can be
    # verified using the CA certificate chain.
    _, _, verify_server_error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/server/myserver.cert.pem"
    )

    _, _, verify_client_error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/server/myserver.cert.pem"
    )

    # He is happy to see that verification succeeds.
    assert verify_server_error_code == 0
    assert verify_client_error_code == 0
