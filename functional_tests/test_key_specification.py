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


def test_commands_report_key_specification_option_as_available():
    # John is looking into improving the security of one of his
    # projects. One of the items he has on the list is to try out
    # stronger private keys, while comparing the performance results
    # against the use of weaker keys. Before he goes into production,
    # he wants to try things out in his test environment.
    #
    # John knows that the Gimmecert by default does not prompt the
    # user to specify desired key size. What he would really like to
    # do, however, is to explicitly specify himself what kind of
    # private keys should be generated instead.

    # He starts off by checking  the help for the init command first.
    stdout, _, _ = run_command('gimmecert', 'init', '-h')

    # John notices that there is an option to provide a custom key
    # specification, and that the default is 2048-bit RSA.
    assert "--key-specification" in stdout
    assert " -k" in stdout
    assert "Default is rsa:2048" in stdout

    # The option allows him to pick between RSA and ECDSA. For RSA he
    # can specify a custom key size, while for ECDSA he can pick
    # between one of the listed named curves.
    assert "rsa:BIT_LENGTH" in stdout
    assert "ecdsa:CURVE_NAME" in stdout
    assert "curves: " in stdout
    assert "secp192r1" in stdout
    assert "secp224r1" in stdout
    assert "secp256k1" in stdout
    assert "secp256r1" in stdout
    assert "secp384r1" in stdout
    assert "secp521r1" in stdout

    # Next, he decides to have a look at the server command.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "-h")

    # John notices the option for passing-in a key specification, and
    # that the default is to use same key specification as used by the
    # CA hierarchy.
    assert " --key-specification" in stdout
    assert " -k" in stdout
    assert "use same" in stdout
    assert "as used by CA hierarchy" in stdout

    # The option allows him to pick between RSA and ECDSA. For RSA he
    # can specify a custom key size, while for ECDSA he can pick
    # between one of the listed named curves.
    assert "rsa:BIT_LENGTH" in stdout
    assert "ecdsa:CURVE_NAME" in stdout
    assert "curves: " in stdout
    assert "secp192r1" in stdout
    assert "secp224r1" in stdout
    assert "secp256k1" in stdout
    assert "secp256r1" in stdout
    assert "secp384r1" in stdout
    assert "secp521r1" in stdout

    # John then has a look at the client command.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "-h")

    # John notices the option for passing-in a key specification, and
    # that the default is to use same key specification as used by the
    # CA hierarchy.
    assert " --key-specification" in stdout
    assert " -k" in stdout
    assert "use same" in stdout
    assert "as used by CA hierarchy" in stdout

    # The option allows him to pick between RSA and ECDSA. For RSA he
    # can specify a custom key size, while for ECDSA he can pick
    # between one of the listed named curves.
    assert "rsa:BIT_LENGTH" in stdout
    assert "ecdsa:CURVE_NAME" in stdout
    assert "curves: " in stdout
    assert "secp192r1" in stdout
    assert "secp224r1" in stdout
    assert "secp256k1" in stdout
    assert "secp256r1" in stdout
    assert "secp384r1" in stdout
    assert "secp521r1" in stdout

    # Finally, he reviews the renew command.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # John notices the option for passing-in a key specification, and
    # that the default is to use same key specification as currently
    # in use by the currently issued certificate.
    assert " --key-specification" in stdout
    assert " -k" in stdout
    assert "use same" in stdout
    assert "as used for current certificate" in stdout

    # The option allows him to pick between RSA and ECDSA. For RSA he
    # can specify a custom key size, while for ECDSA he can pick
    # between one of the listed named curves.
    assert "rsa:BIT_LENGTH" in stdout
    assert "ecdsa:CURVE_NAME" in stdout
    assert "curves: " in stdout
    assert "secp192r1" in stdout
    assert "secp224r1" in stdout
    assert "secp256k1" in stdout
    assert "secp256r1" in stdout
    assert "secp384r1" in stdout
    assert "secp521r1" in stdout


def test_initialisation_with_rsa_private_key_specification(tmpdir):
    # John wants to initialise CA hierarchy using stronger RSA
    # keys. He switches to his project directory.
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


def test_server_command_default_key_specification_with_rsa(tmpdir):
    # John needs to perform some quick tests revolving around the use
    # of X.509 certificates, but he does not care about the generated
    # private key strength. He primarily needs to deal with
    # certificate validation. For this reason, he wants to increase
    # the test speed by generating smaller RSA private keys.

    # He switches to his project directory, and initialises the CA
    # hierarchy, requesting that 1024-bit RSA keys should be used.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "rsa:1024")

    # John issues a server certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'server', 'myserver1')

    # John observes that the process was completed successfully.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')

    # He can see that the generated private key uses the same size as the
    # one he specified for the CA hierarchy.
    assert "Private-Key: (1024 bit)" in stdout


def test_server_command_key_specification_with_rsa(tmpdir):
    # John is working on a project where he has already initialised CA
    # hierarchy using strong RSA keys. However, now he has a need to
    # issue a couple of weaker RSA keys for performance testing.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "rsa:3072")

    # John goes ahead and issues a server certificate using key
    # specification option.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "--key-specification", "rsa:2048", "myserver1")

    # The run finishes without any errors.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')

    # He nods with his head, observing that the generated private key
    # uses the same key size as he has requested.
    assert "Private-Key: (2048 bit)" in stdout


def test_client_command_default_key_specification_with_rsa(tmpdir):
    # John needs to perform some quick tests revolving around the use
    # of X.509 certificates, but he does not care about the generated
    # private key strength. He primarily needs to deal with
    # certificate validation. For this reason, he wants to increase
    # the test speed by generating smaller RSA private keys.

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

    # He can see that the generated private key uses the same size as the
    # one he specified for the CA hierarchy.
    assert "Private-Key: (1024 bit)" in stdout


def test_client_command_key_specification_with_rsa(tmpdir):
    # John is working on a project where he has already initialised CA
    # hierarchy using strong RSA keys. However, now he has a need to
    # issue a couple of weaker RSA keys for performance testing.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "rsa:3072")

    # John goes ahead and issues a client certificate using key
    # specification option.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "--key-specification", "rsa:2048", "myclient1")

    # The run finishes without any errors.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient1.key.pem')

    # He nods with his head, observing that the generated private key
    # uses the same key size as he has specified.
    assert "Private-Key: (2048 bit)" in stdout


def test_renew_command_key_specification_with_rsa(tmpdir):
    # John has set-up a project where he has issued a couple of
    # certificates. For some of them he has used externally-generated
    # private keys.
    tmpdir.chdir()

    run_command("openssl", "req", "-newkey", "rsa:3072", "-nodes", "-keyout", "myserver2.key.pem",
                "-new", "-subj", "/CN=myserver2", "-out", "myserver2.csr.pem")
    run_command("openssl", "req", "-newkey", "rsa:3072", "-nodes", "-keyout", "myclient2.key.pem",
                "-new", "-subj", "/CN=myclient2", "-out", "myclient2.csr.pem")

    run_command("gimmecert", "init")

    run_command('gimmecert', 'server', 'myserver1')
    run_command('gimmecert', 'client', 'myclient1')

    run_command("gimmecert", "server", "--csr", "myserver2.csr.pem", "myserver2")
    run_command("gimmecert", "client", "--csr", "myclient2.csr.pem", "myclient2")

    # After some testing he realises that he needs to perform some
    # tests using a different RSA key size.

    # He renews the server certificate first.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "--new-private-key", "--key-specification", "rsa:1024", "-p", "myserver1")

    # Command suceeds.
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

    # And once again, Gimmecert has created the key with correct size.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient1.key.pem')
    assert "Private-Key: (1024 bit)" in stdout

    # After some further testing, John decides to renew the
    # certificates that have been issued using a CSR. He requests new
    # private keys to be generated as well.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "-p", "myserver1")
    assert exit_code == 0
    assert stderr == ""

    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "-p", "myclient1")
    assert exit_code == 0
    assert stderr == ""

    # John is unsure if the same key specification has been used. So
    # he goes ahead and has a look at the server key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')

    # The renew command has used the same key specification for the
    # new private key as for the old private key.
    assert "Private-Key: (1024 bit)" in stdout

    # He performs the same check on the client key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient1.key.pem')

    # The renew command has used the same key specification for the
    # new private key as for the old private key.
    assert "Private-Key: (1024 bit)" in stdout

    # After using his manually generated private keys for a while,
    # John accidentally deletes them from his managed machine. Instead
    # of redoing the whole process with CSRs, he decides to simply
    # regenerate the private keys and certificates and copy them over.
    run_command('gimmecert', 'renew', 'server', '--new-private-key', 'myserver2')
    run_command('gimmecert', 'renew', 'client', '--new-private-key', 'myclient2')

    # John realizes that the original private keys he generated used
    # 3072-bit RSA, while the CA hierarchy uses 2048-bit RSA. He
    # decides to check if the generated key ended-up using CA
    # hierarchy defaults, or the same key size he used when generating
    # the keys manually.
    #
    # He checks the server private key, and everything seems right -
    # same key size is used as in case of the old private key.
    stdout, stderr, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/server/myserver2.key.pem')
    assert "Private-Key: (3072 bit)" in stdout

    # Then he has a look at the client private key, and that one is
    # also using the same key size as the old private key.
    stdout, _, _ = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/client/myclient2.key.pem')
    assert "Private-Key: (3072 bit)" in stdout


def test_initialisation_with_ecdsa_key_specification(tmpdir):
    # John wnats to initialise a CA hierarchy using ECDSA keys. He
    # switches to his project directory.
    tmpdir.chdir()

    # He decides to use the secp256r1 curve, and initialises his CA
    # hierarchy by passing-in the key specification.
    stdout, stderr, exit_code = run_command('gimmecert', 'init', '--key-specification', 'ecdsa:secp256r1')

    # Command finishes execution with success, and John notices that
    # the tool has informed him about the private key algorithm in use
    # for the CA hierarchy.
    assert exit_code == 0
    assert stderr == ""
    assert "CA hierarchy initialised using secp256r1 ECDSA keys." in stdout

    # John goes ahead and inspects the CA private key to ensure his
    # private key specification has been accepted.
    stdout, stderr, exit_code = run_command('openssl', 'ec', '-noout', '-text', '-in', '.gimmecert/ca/level1.key.pem')

    assert exit_code == 0
    assert stderr == "read EC key\n"  # OpenSSL prints this out to stderr no matter what.

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


def test_server_command_default_key_specification_with_ecdsa(tmpdir):
    # John is setting-up a project to test some functionality
    # revolving around the use of X.509 certificates. He has used RSA
    # extensively before, but now he wants to switch to using ECDSA
    # private keys instead.

    # He switches to his project directory, and initialises the CA
    # hierarchy, requesting that secp256r1 ECDSA keys should be used.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "ecdsa:secp384r1")

    # John issues a server certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'server', 'myserver1')

    # John observes that the process was completed successfully.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'ec', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')

    # And indeed, the generated private key uses the same algorithm as
    # the one he specified for the CA hierarchy.
    assert "ASN1 OID: secp384r1" in stdout


def test_server_command_key_specification_with_ecdsa(tmpdir):
    # John is setting-up a project where he needs to test performance
    # using different curves for ECDSA keys.

    # He switches to his project directory, and initialises the CA
    # hierarchy, requesting that secp192r1 ECDSA keys should be used.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "ecdsa:secp192r1")

    # Very soon he realizes that he needs to test performance using
    # different elliptic curve algorithms for proper comparison. He
    # decides to start off with secp224r1, and issues a new server
    # certificate, passing-in the necessary key specification.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "--key-specification", "ecdsa:secp224r1", "myserver1")

    # The process finishes with success.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'ec', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')

    # He nods with his head, observing that the generated private key
    # uses the same algorithm as he has specified.
    assert "ASN1 OID: secp224r1" in stdout


def test_client_command_default_key_specification_with_ecdsa(tmpdir):
    # John is setting-up a project to test some functionality
    # revolving around the use of X.509 certificates. He has used RSA
    # extensively before, but now he wants to switch to using ECDSA
    # private keys instead.

    # He switches to his project directory, and initialises the CA
    # hierarchy, requesting that secp256r1 ECDSA keys should be used.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "ecdsa:secp521r1")

    # John issues a client certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'client', 'myclient1')

    # John observes that the process was completed successfully.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'ec', '-noout', '-text', '-in', '.gimmecert/client/myclient1.key.pem')

    # And indeed, the generated private key uses the same algorithm as
    # the one he specified for the CA hierarchy.
    assert "ASN1 OID: secp521r1" in stdout


def test_client_command_key_specification_with_ecdsa(tmpdir):
    # John is setting-up a project where he needs to test performance
    # when using different ECDSA private key sizes.

    # He switches to his project directory, and initialises the CA
    # hierarchy, requesting that secp192r1 ECDSA keys should be used.
    tmpdir.chdir()
    run_command("gimmecert", "init", "--key-specification", "ecdsa:secp192r1")

    # Very soon he realizes that he needs to test performance using
    # different elliptic curve algorithms for proper comparison. He
    # decides to start off with secp224r1, and issues a new server
    # certificate, passing-in the necessary key specification.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "--key-specification", "ecdsa:secp224r1", "myclient1")

    # The process finishes with success.
    assert exit_code == 0
    assert stderr == ""

    # He runs a command to see details about the generated private
    # key.
    stdout, _, _ = run_command('openssl', 'ec', '-noout', '-text', '-in', '.gimmecert/client/myclient1.key.pem')

    # He nods with his head, observing that the generated private key
    # uses the same algorithm as he has specified.
    assert "ASN1 OID: secp224r1" in stdout


def test_renew_command_key_specification_with_ecdsa(tmpdir):
    # John has set-up a project where he is using secp224r1 ECDSA keys
    # by default. He has issued a couple of certificates, with some
    # using externally-generated private keys.
    tmpdir.chdir()

    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myserver2.key.pem", "-name", "secp256r1")
    run_command("openssl", "req", "-new", "-key", "myserver2.key.pem", "-subj", "/CN=myserver2", "-out", "myserver2.csr.pem")
    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myclient2.key.pem", "-name", "secp256r1")
    run_command("openssl", "req", "-new", "-key", "myclient2.key.pem", "-subj", "/CN=myclient2", "-out", "myclient2.csr.pem")

    run_command("gimmecert", "init", "--key-specification", "ecdsa:secp224r1")

    run_command("gimmecert", "server", "myserver1")
    run_command("gimmecert", "client", "myclient1")

    run_command("gimmecert", "server", "--csr", "myserver2.csr.pem", "myserver2")
    run_command("gimmecert", "client", "--csr", "myclient2.csr.pem", "myclient2")

    # After some testing he realises that he needs to perform some
    # tests using a different elliptic curve algorithm.

    # He renews the server certificate first.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "--new-private-key", "--key-specification", "ecdsa:secp521r1", "-p", "myserver1")

    # Command suceeds.
    assert exit_code == 0
    assert stderr == ""

    # He checks the details about the generated private key, and
    # disovers that Gimmecert generated the key according to his
    # wishes.
    stdout, _, _ = run_command('openssl', 'ec', '-noout', '-text', '-in', '.gimmecert/server/myserver1.key.pem')
    assert "ASN1 OID: secp521r1" in stdout

    # John goes ahead and performs a similar operation for his client
    # entity.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "-k", "ecdsa:secp521r1", "-p", "myclient1")
    assert exit_code == 0
    assert stderr == ""

    # And once again, Gimmecert has created the key with correct size.
    stdout, stderr, _ = run_command("openssl", "ec", "-noout", "-text", "-in", ".gimmecert/client/myclient1.key.pem")
    assert "ASN1 OID: secp521r1" in stdout, stderr

    # After some further testing, John decides to renew the
    # certificates that have been issued using a CSR. He requests new
    # private keys to be generated as well.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "-p", "myserver1")
    assert exit_code == 0
    assert stderr == ""

    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "-p", "myclient1")
    assert exit_code == 0
    assert stderr == ""

    # John is unsure if the same key specification has been used, so
    # he goes ahead and has a look at the server key.
    stdout, _, _ = run_command("openssl", "ec", "-noout", "-text", "-in", ".gimmecert/server/myserver1.key.pem")

    # The renew command has used the same key specification for the
    # new private key as for the old private key.
    assert "ASN1 OID: secp521r1" in stdout

    # He performs the same check on the client key.
    stdout, _, _ = run_command("openssl", "ec", "-noout", "-text", "-in", ".gimmecert/client/myclient1.key.pem")

    # The renew command has used the same key specification for the
    # new private key as for the old private key.
    assert "ASN1 OID: secp521r1" in stdout

    # After using his manually generated private keys for a while,
    # John accidentally deletes them from his managed machine. Instead
    # of redoing the whole process with CSRs, he decides to simply
    # regenerate the private keys and certificates and copy them over.
    run_command("gimmecert", "renew", "server", "--new-private-key", "myserver2")
    run_command("gimmecert", "renew", "client", "--new-private-key", "myclient2")

    # John realizes that the original private keys he generated used
    # secp256r1, while the CA hierarchy uses secp224r1. He decides to
    # check if the generated key ended-up using CA hierarchy defaults,
    # or the same elliptic curve he used when generating the keys
    # manually.
    #
    # He checks the server private key, and everything seems good -
    # same elliptic curve (although listed under alternative name) is
    # used as in case of the old private key.
    stdout, stderr, _ = run_command("openssl", "ec", "-noout", "-text", "-in", ".gimmecert/server/myserver2.key.pem")
    assert "ASN1 OID: prime256v1" in stdout

    # Then he has a look at the client private key, and that one is
    # also using the same elliptic curve as before.
    stdout, _, _ = run_command("openssl", "ec", "-noout", "-text", "-in", ".gimmecert/client/myclient2.key.pem")
    assert "ASN1 OID: prime256v1" in stdout
