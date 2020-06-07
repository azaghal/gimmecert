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


def test_initialisation_with_rsa_private_key_specification(tmpdir):
    # John is looking into improving the security of one of his
    # projects. Amongst other things, John is interested in using
    # stronger private keys for his TLS services - which he wants to
    # try out in his test envioronment first.

    # John knows that the Gimmecert tool uses 2048-bit RSA keys for
    # the CA hierarchy, but what he would really like to do is specify
    # himself what kind of private key should be generated
    # instead. He checks-out the help for the init command first.
    stdout, _, _ = run_command('gimmecert', 'init', '-h')

    # John noticies there is an option to provide a custom key
    # specification to the tool, that he can specify the length of
    # the RSA private keys, and that the default is "rsa:2048".
    assert "--key-specification" in stdout
    assert " -k" in stdout
    assert "rsa:BIT_LENGTH" in stdout
    assert "Default is rsa:2048" in stdout

    # John switches to his project directory.
    tmpdir.chdir()

    # He initalises the CA hierarchy, requesting to use 4096-bit RSA
    # keys.
    stdout, stderr, exit_code = run_command('gimmecert', 'init', '--key-specification', 'rsa:4096')

    # Command finishes execution with success, and John notices that
    # the tool has informed him of what the private key algorithm is
    # in use for the CA hierarchy.
    assert exit_code == 0
    assert stderr == ""
    assert "CA hierarchy initialised using 4096-bit RSA keys." in stdout

    # John goes ahead and inspects the CA private key to ensure his
    # private key specification has been accepted.
    stdout, stderr, exit_code = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/ca/level1.key.pem')

    assert exit_code == 0
    assert stderr == ""
    assert "Private-Key: (4096 bit)" in stdout

    # John also does a quick check on the generated certificate's
    # signing and public key algorithm.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/ca/level1.cert.pem')

    assert exit_code == 0
    assert stderr == ""
    assert "Signature Algorithm: sha256WithRSAEncryption" in stdout
    assert "Public-Key: (4096 bit)" in stdout


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
