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
    assert " entity_name [dns_name [dns_name ...]]" in stdout


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


def test_server_command_issues_server_certificate_with_additional_subject_alternative_names(tmpdir):
    # John wants to issue a server certificate that will include a
    # number of additional DNS subject alternative names. He switches
    # to his project directory, and initialises the CA hierarchy
    # there.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    # He then runs command for issuing a server certificate, providing
    # additional DNS subject alternative names..
    stdout, stderr, exit_code = run_command('gimmecert', 'server', 'myserver', 'myserver.local', 'myserver.example.com')

    # The command finishes without any errors being reported.
    assert stderr == ""
    assert exit_code == 0

    # John then a look at generated certificate file.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver.cert.pem')

    # No errors are reported, and he notices that the provided subject
    # alternative names have been included in the certificate in
    # addition to default one based on the server entity name.
    assert exit_code == 0
    assert stderr == ""

    assert "DNS:myserver," in stdout
    assert "DNS:myserver.local," in stdout
    assert "DNS:myserver.example.com\n" in stdout


def test_server_command_does_not_overwrite_existing_artifacts(tmpdir):
    # John has become an avid user of Gimmecert. He uses it in a lot
    # of projects, including one specific project which he had set-up
    # a couple of months ago, where he has issued some server
    # certificate.
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "myserver")

    private_key = tmpdir.join(".gimmecert", "server", "myserver.key.pem").read()
    certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()

    # After a couple of months of inactivity on that particular
    # project, John is again asked to do something in relation to
    # it. He recalls that he needed to issue a server certificate for
    # it, so he goes ahead and tries to do it again.
    tmpdir.chdir()
    stdout, stderr, exit_code = run_command("gimmecert", "server", "myserver")

    # John realizes in last moment, just as he presses ENTER, that he
    # had issued certificate already. He wonders if he'd need to
    # redeploy it again now, though. To his (small) relief, he
    # realizes is it not necessary, since the tool has refused to
    # overwrite the old key and certificate. Instead he is presented
    # with an error notifying him that the certificate has already
    # been issued.
    assert exit_code != 0
    assert stderr == "Refusing to overwrite existing data. Certificate has already been issued for server myserver.\n"
    assert stdout == ""

    # John double-checks (just to be on the safe side), and can see
    # that both the private key and certificate have been left
    # unchanged.
    assert tmpdir.join(".gimmecert", "server", "myserver.key.pem").read() == private_key
    assert tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read() == certificate


def test_server_command_key_specification(tmpdir):
    # John is setting-up a quick and dirty project to test some
    # functionality revolving around X.509 certificates. Since he does
    # not care much about the strength of private keys for it, he
    # wants to use 1024-bit RSA keys.

    # He switches to his project directory, and initialises the CA
    # hierarchy, requesting that 1024-bit RSA keys should be used.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "rsa:1024")

    # John issues a server certificates.
    stdout, stderr, exit_code = run_command('gimmecert', 'server', 'myserver1')

    # John observes that the process was completed successfully.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')

    # And indeed, the generated private key uses the same size as the
    # one he specified for the CA hierarchy.
    assert "Private-Key: (1024 bit)" in stdout

    # He then has a look at the certificate.
    stdout, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver1.cert.pem')

    # Likewise with the private key, the certificate is also using the
    # 1024-bit RSA key.
    assert "Public-Key: (1024 bit)" in stdout

    # At some point John realises that to cover all bases, he needs to
    # have a test with a server that uses 2048-bit RSA keys as
    # well. He does not want to regenerate all of the X.509 artefacts,
    # and would like to instead issues a single 2048-bit RSA key for a
    # specific server instead.

    # He starts off by having a look at the help for the server command.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "-h")

    # John notices the option for passing-in a key specification.
    assert " --key-specification" in stdout
    assert " -k" in stdout

    # John goes ahead and tries to issue a server certificate using
    # key specification option.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "--key-specification", "rsas:2048", "myserver2")

    # Unfortunately, the command fails due to John's typo.
    assert exit_code != 0
    assert "invalid key_specification" in stderr

    # John tries again, fixing his typo.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "--key-specification", "rsa:2048", "myserver2")

    # This time around he succeeds.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver2.key.pem')

    # He nods with his head, observing that the generated private key
    # uses the same key size as he has specified.
    assert "Private-Key: (2048 bit)" in stdout
