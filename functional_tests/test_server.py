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


def test_server_command_available_with_help():
    # John has finally finished initialising his CA hierarchy. What he
    # wants to do now is to issue a server certificate. He starts off
    # by having a look at the list of available commands.
    stdout, stderr, exit_code = run_command("gimmecert")

    # Looking at output, John notices the server command.
    assert exit_code == 0
    assert stderr == ""
    assert "server" in stdout

    # He goes ahead and has a look at the server command invocation to
    # check what kind of parameters he might need to provide.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "-h")

    # John can see that the command accepts an entity name, and an
    # optional list of DNS subject alternative names.
    assert exit_code == 0
    assert stderr == ""
    assert stdout.startswith("usage: gimmecert server")
    assert stdout.split('\n')[0].endswith(" entity_name [dns_name [dns_name ...]]")  # First line of help.


def test_server_command_requires_initialised_hierarchy(tmpdir):
    # John is about to issue a server certificate. He switches to his
    # project directory.
    tmpdir.chdir()

    # John tries to issue a server certificate.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "myserver")

    # Unfortunately, John has forgotten to initialise the CA hierarchy
    # from within this directory, and is instead presented with an
    # error.
    assert stdout == ""
    assert stderr == "CA hierarchy must be initialised prior to issuing server certificates. Run the gimmecert init command first.\n"
    assert exit_code != 0


def test_server_command_issues_server_certificate(tmpdir):
    # John is about to issue a server certificate. He switches to his
    # project directory, and initialises the CA hierarchy there.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    # He then runs command for issuing a server certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'server', 'myserver')

    # John notices that the command has run without an error, and that
    # it has printed out path to the private key and certificate.
    assert stderr == ""
    assert exit_code == 0
    assert "Server certificate issued." in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout

    # John has a look at the generated private key using the OpenSSL
    # CLI.
    stdout, stderr, exit_code = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver.key.pem')

    # No errors are reported, and John is able to see some details
    # about the generated key.
    assert exit_code == 0
    assert stderr == ""
    assert "Private-Key: (2048 bit)" in stdout

    # John then has a look at the generated certificate file.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver.cert.pem')

    # Once again, there are no errors, and he can see some details
    # about the certificate.
    assert exit_code == 0
    assert stderr == ""
    assert 'Certificate:' in stdout

    # He notices that the certificate includes the provided entity
    # name as DNS subject alternative name.
    assert "DNS:myserver\n" in stdout

    # John has a quick look at issuer and subject DN stored in
    # certificate.
    issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/server/myserver.cert.pem')
    subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/server/myserver.cert.pem')
    issuer_dn = issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    subject_dn = subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # He notices the issuer DN is as expected based on the directory
    # name, and that server certificate subject DN simply has CN field
    # with the name he provided earlier.
    assert issuer_dn == "CN = %s Level 1 CA" % tmpdir.basename
    assert subject_dn == "CN = myserver"

    # John takes a look at certificate purpose, since he wants to
    # ensure it is a proper TLS server certificate.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-purpose', '-in', '.gimmecert/server/myserver.cert.pem')

    # He verifies that the provided certificate has correct purpose.
    assert "SSL server : Yes" in stdout
    assert "SSL server CA : No" in stdout
    assert "SSL client : No" in stdout
    assert "SSL client CA : No" in stdout

    # Finally, he decides to check if the certificate can be verified
    # using the CA certificate chain.
    _, _, error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/server/myserver.cert.pem"
    )

    # He is happy to see that verification succeeds.
    assert error_code == 0
