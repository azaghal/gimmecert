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


def test_client_command_key_specification(tmpdir):
    # John is setting-up a quick and dirty project to test some
    # functionality revolving around X.509 certificates. Since he does
    # not care much about the strength of private keys for it, he
    # wants to use 1024-bit RSA keys.

    # He switches to his project directory, and initialises the CA
    # hierarchy, requesting that 1024-bit RSA keys should be used.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "rsa:1024")

    # John issues a client certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'client', 'myclient1')

    # John observes that the process was completed successfully.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient1.key.pem')

    # And indeed, the generated private key uses the same size as the
    # one he specified for the CA hierarchy.
    assert "Private-Key: (1024 bit)" in stdout

    # He then has a look at the certificate.
    stdout, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/client/myclient1.cert.pem')

    # Likewise with the private key, the certificate is also using the
    # 1024-bit RSA key.
    assert "Public-Key: (1024 bit)" in stdout

    # At some point John realises that to cover all bases, he needs to
    # have a test with a client that uses 2048-bit RSA keys as
    # well. He does not want to regenerate all of the X.509 artefacts,
    # and would like to instead issues a single 2048-bit RSA key for a
    # specific client instead.

    # He starts off by having a look at the help for the client command.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "-h")

    # John notices the option for passing-in a key specification.
    assert " --key-specification" in stdout
    assert " -k" in stdout

    # John goes ahead and tries to issue a client certificate using
    # key specification option.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "--key-specification", "rsas:2048", "myclient2")

    # Unfortunately, the command fails due to John's typo.
    assert exit_code != 0
    assert "invalid key_specification" in stderr

    # John tries again, fixing his typo.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "--key-specification", "rsa:2048", "myclient2")

    # This time around he succeeds.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient2.key.pem')

    # He nods with his head, observing that the generated private key
    # uses the same key size as he has specified.
    assert "Private-Key: (2048 bit)" in stdout


def test_renew_command_key_specification(tmpdir):
    # John has set-up a project where he has issued a couple of
    # certificates.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    run_command('gimmecert', 'server', 'myserver1')
    run_command('gimmecert', 'client', 'myclient1')

    # However, soon he realizes that he needs to perform some tests
    # using a different RSA key size. John knows that Gimmecert comes
    # with a renew command, so he has a quick look at its help.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # John notices the option for passing-in custom key specification.
    assert " --key-specification" in stdout
    assert " -k" in stdout

    # He goes ahead and tries to renew his server certificate.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "-k", "rsa:1024", "myserver1")

    # However, Gimmecert informs him that the key specification option
    # can only be used when requesting a new private key to be
    # generated as well.
    assert exit_code != 0
    assert "argument --key-specification/-k: must be used with --new-private-key/-p" in stderr

    # John goes ahead and adds that argument as well to his command.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "-k", "rsa:1024", "-p", "myserver1")

    # This time everything goes without a hitch.
    assert exit_code == 0
    assert stderr == ""

    # He checks the details about the generated private key, and
    # disovers that Gimmecert generated the key according to his
    # wishes.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')
    assert "Private-Key: (1024 bit)" in stdout

    # John goes ahead and performs a similar operation for his client
    # entity.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "-k", "rsa:1024", "-p", "myclient1")
    assert exit_code == 0
    assert stderr == ""

    # And once again, everything seems to check-out.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient1.key.pem')
    assert "Private-Key: (1024 bit)" in stdout

    # After some further testing, John decides to renew both of his
    # certificates, together with generation of new private keys. He
    # forgets to use the key specification option, though. Both
    # commands succeed without errors.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "-p", "myserver1")
    assert exit_code == 0
    assert stderr == ""

    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "-p", "myclient1")
    assert exit_code == 0
    assert stderr == ""

    # John is unsure if the same key specification has been used,
    # however. So he goes ahead and has a look at the server key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')

    # And everything seems to be fine.
    assert "Private-Key: (1024 bit)" in stdout

    # He performs the same check on the client key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient1.key.pem')

    # No problems here either.
    assert "Private-Key: (1024 bit)" in stdout

    # Finally, John generates a couple of private keys directly on one
    # of his managed machines, and issues certificates for them via
    # CSRs.
    run_command("openssl", "req", "-newkey", "rsa:3072", "-nodes", "-keyout", "myserver2.key.pem",
                "-new", "-subj", "/CN=myserver2", "-out", "myserver2.csr.pem")
    run_command("openssl", "req", "-newkey", "rsa:3072", "-nodes", "-keyout", "myclient2.key.pem",
                "-new", "-subj", "/CN=myclient2", "-out", "myclient2.csr.pem")
    run_command("gimmecert", "server", "--csr", "myserver2.csr.pem", "myserver2")
    run_command("gimmecert", "client", "--csr", "myclient2.csr.pem", "myclient2")

    # After using his generated private keys for a while, John
    # accidentally deletes them from his managed machine. Instead of
    # redoing the whole process with CSRs, he decides to simply
    # regenerate the private keys and certificates and copy them over.
    run_command('gimmecert', 'renew', 'server', '--new-private-key', 'myserver2')
    run_command('gimmecert', 'renew', 'client', '--new-private-key', 'myclient2')

    # John realizes that the original private keys he generated used
    # 3072-bit RSA, while the CA hierarchy uses 2048-bit RSA. He
    # decides to check if the generated key ended-up using CA-defaults
    # or his own specification from before.
    #
    # He checks the server private key, and everything seems right -
    # his own key specficiation from the old private key was used.
    stdout, stderr, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver2.key.pem')
    assert "Private-Key: (3072 bit)" in stdout

    # Then he has a look at the client private key, and everything
    # checks-out for it as well.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient2.key.pem')
    assert "Private-Key: (3072 bit)" in stdout


def test_initialisation_with_ecdsa_key_specification(tmpdir):
    # John is looking into using ECDSA keys in his latest project. He
    # is already aware that Gimmecert supports use of RSA keys, but he
    # hasn't tried using it with ECDSA yet.

    # He checks the help for the init command first to see if he can
    # somehow request ECDSA keys to be used instead of RSA.
    stdout, _, _ = run_command('gimmecert', 'init', '-h')

    # John noticies there is an option to provide a custom key
    # specification to the tool, and that he can request ECDSA keys to
    # be used with a specific curve.
    assert "--key-specification" in stdout
    assert " -k" in stdout
    assert "rsa:BIT_LENGTH" in stdout
    assert "ecdsa:CURVE_NAME" in stdout

    # John can see a number of curves listed as supported.
    assert "Supported curves: " in stdout
    assert "secp192r1" in stdout
    assert "secp224r1" in stdout
    assert "secp256k1" in stdout
    assert "secp256r1" in stdout
    assert "secp384r1" in stdout
    assert "secp521r1" in stdout

    # John switches to his project directory.
    tmpdir.chdir()

    # After a short deliberation, he opts to use the secp256r1 curve,
    # and initialises his CA hierarchy.
    stdout, stderr, exit_code = run_command('gimmecert', 'init', '--key-specification', 'ecdsa:secp256r1')

    # Command finishes execution with success, and John notices that
    # the tool has informed him of what the private key algorithm is
    # in use for the CA hierarchy.
    assert exit_code == 0
    assert stderr == ""
    assert "CA hierarchy initialised using secp256r1 ECDSA keys." in stdout

    # John goes ahead and inspects the CA private key to ensure his
    # private key specification has been accepted.
    stdout, stderr, exit_code = run_command('openssl', 'ec', '-noout', '-text', '-in', '.gimmecert/ca/level1.key.pem')

    assert exit_code == 0
    assert stderr == "read EC key\n"  # OpenSSL print this out to stderr no matter what.

    # He notices that although he requested secp256r1, the output from
    # OpenSSL tool uses its older name from RFC3279 -
    # prime256v1. However, he understands this is just an alternate
    # name for the curve.
    assert "ASN1 OID: prime256v1" in stdout

    # John also does a quick check on the generated certificate's
    # signing and public key algorithm.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/ca/level1.cert.pem')

    assert exit_code == 0
    assert stderr == ""
    assert "Signature Algorithm: ecdsa-with-SHA256" in stdout
    assert "Public Key Algorithm: id-ecPublicKey" in stdout
    assert "ASN1 OID: prime256v1" in stdout
