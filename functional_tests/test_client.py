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


def test_client_command_available_with_help():
    # After issuing a couple of server certificates, John has decided
    # to test out TLS client certificate authentication in his
    # project. For this, naturally, he needs a client certificate.
    # Hoping that the Gimmecert tool has ability to generate those
    # too, he runs the tool to see available commands.
    stdout, stderr, exit_code = run_command("gimmecert")

    # Looking at output, John notices the client command.
    assert exit_code == 0
    assert stderr == ""
    assert "client" in stdout

    # He goes ahead and has a look at the client command invocation to
    # check what kind of parameters he might need to provide.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "-h")

    # John can see that the command accepts a single positional
    # argument - an entity name.
    assert exit_code == 0
    assert stderr == ""
    assert stdout.startswith("usage: gimmecert client")
    assert stdout.split('\n')[2].endswith(" entity_name")  # Third line of help.


def test_client_command_requires_initialised_hierarchy(tmpdir):
    # John is about to issue a client certificate. He switches to his
    # project directory.
    tmpdir.chdir()

    # John tries to issue a client certificate.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "myclient")

    # Unfortunately, John has forgotten to initialise the CA hierarchy
    # from within this directory, and is instead presented with an
    # error.
    assert stdout == ""
    assert stderr == "CA hierarchy must be initialised prior to issuing client certificates. Run the gimmecert init command first.\n"
    assert exit_code != 0


def test_client_command_issues_client_certificate(tmpdir):
    # John is about to issue a client certificate. He switches to his
    # project directory, and initialises the CA hierarchy there.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    # He then runs command for issuing a client certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'client', 'myclient')

    # John notices that the command has run without an error, and that
    # it has printed out path to the private key and certificate.
    assert stderr == ""
    assert exit_code == 0
    assert "Client certificate issued." in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout

    # John has a look at the generated private key using the OpenSSL
    # CLI.
    stdout, stderr, exit_code = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient.key.pem')

    # No errors are reported, and John is able to see some details
    # about the generated key.
    assert exit_code == 0
    assert stderr == ""
    assert "Private-Key: (2048 bit)" in stdout

    # John then has a look at the generated certificate file.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/client/myclient.cert.pem')

    # Once again, there are no errors, and he can see some details
    # about the certificate.
    assert exit_code == 0
    assert stderr == ""
    assert 'Certificate:' in stdout

    # John has a quick look at issuer and subject DN stored in
    # certificate.
    issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/client/myclient.cert.pem')
    subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/client/myclient.cert.pem')
    issuer_dn = issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    subject_dn = subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # He notices the issuer DN is as expected based on the directory
    # name, and that client certificate subject DN simply has CN field
    # with the name he provided earlier.
    assert issuer_dn == "CN = %s Level 1 CA" % tmpdir.basename
    assert subject_dn == "CN = myclient"

    # John takes a look at certificate purpose, since he wants to
    # ensure it is a proper TLS client certificate.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-purpose', '-in', '.gimmecert/client/myclient.cert.pem')

    # He verifies that the provided certificate has correct purpose.
    assert "SSL client : Yes" in stdout
    assert "SSL client CA : No" in stdout
    assert "SSL server CA : No" in stdout
    assert "SSL server : No" in stdout

    # Finally, he decides to check if the certificate can be verified
    # using the CA certificate chain.
    _, _, error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/client/myclient.cert.pem"
    )

    # He is happy to see that verification succeeds.
    assert error_code == 0


def test_client_command_does_not_overwrite_existing_artifacts(tmpdir):
    # John has used Gimmecert in one of his previous projects. In
    # particular, he has issued some TLS client certificates for
    # testing the TLS client authentication.
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "client", "myclient")

    private_key = tmpdir.join(".gimmecert", "client", "myclient.key.pem").read()
    certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()

    # After some months of inactivity, John figures he needs to
    # perform a quick test on the project related to TLS client
    # certificate authentication. He goes ahead and runs a command to
    # issue the client certificate.
    tmpdir.chdir()
    stdout, stderr, exit_code = run_command("gimmecert", "client", "myclient")

    # John realizes in last moment, just as he presses ENTER, that he
    # had issued certificate already. He wonders if he'd need to
    # redeploy it again now, though. Luckily, Gimmecert detects this,
    # and provides him with an informative warning.
    assert exit_code != 0
    assert stderr == "Refusing to overwrite existing data. Certificate has already been issued for client myclient.\n"
    assert stdout == ""

    # John double-checks (just to be on the safe side), and can see
    # that both the private key and certificate have been left
    # unchanged.
    assert tmpdir.join(".gimmecert", "client", "myclient.key.pem").read() == private_key
    assert tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read() == certificate
