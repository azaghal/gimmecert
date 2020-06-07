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


def test_init_command_available_with_help():
    # John has decided it is time to try out the tool. He starts off
    # by running the short usage help.
    stdout, stderr, returncode = run_command("gimmecert", "-h")

    # Looking at output, John notices the init command.
    assert returncode == 0
    assert stderr == ""
    assert 'init' in stdout

    # John decides to look at a more detailed description of this
    # command before proceeding.
    stdout, stderr, returncode = run_command("gimmecert", "init", "-h")

    # John notices that this command has some useful usage
    # instructions, which allows him to study the available arguments.
    assert returncode == 0
    assert stderr == ""
    assert stdout.startswith("usage: gimmecert init")


def test_initialisation_on_fresh_directory(tmpdir):
    # After reading the help, John decides it's time to initialise the
    # CA hierarchy so he can use it for issuing server and client
    # certificates in his project.

    # John switches to his project directory.
    tmpdir.chdir()

    # He runs the initialisation command.
    stdout, stderr, exit_code = run_command('gimmecert', 'init')

    # The tool exits without any errors, and shows some informative
    # text to John that the directory has been initialised.
    assert exit_code == 0
    assert stderr == ""
    assert "CA hierarchy initialised using 2048-bit RSA keys." in stdout

    # The tool also points John to generated key and certificate material.
    assert ".gimmecert/ca/level1.key.pem" in stdout
    assert ".gimmecert/ca/level1.cert.pem" in stdout
    assert ".gimmecert/ca/chain-full.cert.pem" in stdout

    # Happy that he didn't have to enter long commands, John inspects
    # the CA key first using the OpenSSL CLI.
    stdout, stderr, exit_code = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/ca/level1.key.pem')

    # No errors are reported, and John is able ot see some details
    # about the generated key.
    assert exit_code == 0
    assert stderr == ""
    assert "Private-Key: (2048 bit)" in stdout

    # John then has a look at the generated certificate file.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/ca/level1.cert.pem')

    # With no errors again, he can see some of the details in
    # certificate.
    assert 'Certificate:' in stdout

    # John runs reads the issuer and subject DN stored in certificate.
    issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/ca/level1.cert.pem')
    subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/ca/level1.cert.pem')
    issuer_dn = issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    subject_dn = subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # He notices that the issuer and subject DN are identical (since
    # it's a root CA certificate), and can also see that the subject
    # DN has just the CN with working directory's name in it.
    assert issuer_dn == subject_dn
    assert subject_dn.rstrip() == 'CN = %s Level 1 CA' % tmpdir.basename

    # John has a quick look at generated certificate and chain, only
    # to realise they are identical.
    with open(".gimmecert/ca/level1.cert.pem") as cert_file, open(".gimmecert/ca/chain-full.cert.pem") as chain_file:
        assert cert_file.read() == chain_file.read()


def test_initialisation_on_existing_directory(tmpdir):
    # After a wild weekend out, John comes back to the office on
    # Monday morning, still a bit hangover. Back on Friday, John has
    # already initialised the CA hierarchy for one of his projects.
    tmpdir.chdir()
    run_command('gimmecert', 'init')

    # Unfortunately, John has forgot that he has done so. Therefore he
    # switches to his project directory and runs the command again.
    tmpdir.chdir()
    stdout, stderr, exit_code = run_command('gimmecert', 'init')

    # Instead of viewing information about his CA hierarchy
    # initialised, John is (somewhat pleasantly) surprised to see that
    # the tool has informed him the initialisation has already been
    # run.
    assert exit_code != 0
    assert stdout == ""
    assert stderr == "CA hierarchy has already been initialised.\n"


def test_initialisation_with_custom_base_name(tmpdir):
    # John has been using the tool for a while now in a number of test
    # environments. Unfortunately, he has started to mix-up
    # certificates coming from different envioronments where the
    # project directories have the same name. What he would like to do
    # is to be able to specify the base name explicitly, instead of
    # letting the tool pick it for him.

    # John decides to check the command help from CLI.
    stdout, _, _ = run_command('gimmecert', 'init', '-h')

    # Amongst the different options, he notices one in particular that
    # draws his attention. The option seems to be usable for
    # specifying the base name for the CAs - exactly what he needed.
    assert "--ca-base-name" in stdout
    assert " -b " in stdout

    # John switches to his project directory.
    tmpdir.chdir()

    # This time around he runs the command using the newly-found
    # option.
    stdout, stderr, exit_code = run_command('gimmecert', 'init', '--ca-base-name', 'My Project')

    # Command finishes execution with success, and he is informed that
    # his CA hierarchy has been initialised..
    assert exit_code == 0
    assert stderr == ""
    assert "CA hierarchy initialised using 2048-bit RSA keys." in stdout

    # Just before he starts using the CA certificates further, he
    # decides to double-check the results. He runs a couple of
    # commands to get the issuer and subject DN from generated
    # certificate.
    issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/ca/level1.cert.pem')
    subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/ca/level1.cert.pem')
    issuer_dn = issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    subject_dn = subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # To his delight, both the issuer and subject DN are identical,
    # and now they are based on his custom-provided name instead of
    # project name.
    assert issuer_dn.rstrip() == subject_dn.rstrip() == "CN = My Project Level 1 CA"
    assert tmpdir.basename not in issuer_dn


def test_initialisation_with_custom_hierarchy_depth(tmpdir):
    # John is now involved in a project where the CA hierarchy used
    # for issuing certificates is supposed to be deeper than 1. In
    # other words, he needs Level 1 CA -> Level 2 CA -> Level 3 CA ->
    # end entity certificates.

    # He hopes that the Gimmecert tool can still help him with this
    # scenario as well. At first, he runs the tool with a help flag.
    stdout, _, _ = run_command('gimmecert', 'init', '-h')

    # John notices there is an option to specify hierarchy depth.
    assert "--ca-hierarchy-depth" in stdout
    assert " -d " in stdout

    # John switches to his project directory.
    tmpdir.chdir()

    # He runs the command, specifying this time around the desired CA
    # hierarchy depth.
    stdout, stderr, exit_code = run_command('gimmecert', 'init', '--ca-hierarchy-depth', '3')

    # Command finishes execution with success, and he is informed that
    # his CA hierarchy has been initialised. He notices there are many
    # more CA artifacts listed now.
    assert exit_code == 0
    assert stderr == ""
    assert "CA hierarchy initialised using 2048-bit RSA keys." in stdout
    assert ".gimmecert/ca/level1.key.pem" in stdout
    assert ".gimmecert/ca/level1.cert.pem" in stdout
    assert ".gimmecert/ca/level2.key.pem" in stdout
    assert ".gimmecert/ca/level2.cert.pem" in stdout
    assert ".gimmecert/ca/level3.key.pem" in stdout
    assert ".gimmecert/ca/level3.cert.pem" in stdout
    assert ".gimmecert/ca/chain-full.cert.pem" in stdout

    # John goes ahead and inspects the CA keys first.
    stdout1, stderr1, exit_code1 = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/ca/level1.key.pem')
    stdout2, stderr2, exit_code2 = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/ca/level2.key.pem')
    stdout3, stderr3, exit_code3 = run_command('openssl', 'rsa', '-noout', '-text', '-in', '.gimmecert/ca/level3.key.pem')

    assert exit_code1 == 0
    assert stderr1 == ""
    assert "Private-Key: (2048 bit)" in stdout1

    assert exit_code2 == 0
    assert stderr2 == ""
    assert "Private-Key: (2048 bit)" in stdout2

    assert exit_code3 == 0
    assert stderr3 == ""
    assert "Private-Key: (2048 bit)" in stdout3

    # John then has a look at the generated CA certificate files.
    stdout1, stderr1, exit_code1 = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/ca/level1.cert.pem')
    stdout2, stderr2, exit_code2 = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/ca/level2.cert.pem')
    stdout3, stderr3, exit_code3 = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/ca/level3.cert.pem')

    # John observes that there are no errors, and that certificate
    # details are being shown.
    assert 'Certificate:' in stdout1
    assert 'Certificate:' in stdout2
    assert 'Certificate:' in stdout3

    # John then runs a bunch of commands to get the subject and issuer
    # DNs of certificates.
    issuer_dn1, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/ca/level1.cert.pem')
    subject_dn1, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/ca/level1.cert.pem')
    issuer_dn1 = issuer_dn1.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    subject_dn1 = subject_dn1.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    issuer_dn2, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/ca/level2.cert.pem')
    subject_dn2, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/ca/level2.cert.pem')
    issuer_dn2 = issuer_dn2.replace('issuer=', '', 2).rstrip().replace(' /CN=', 'CN = ', 2)  # OpenSSL 1.0 vs 1.2 formatting
    subject_dn2 = subject_dn2.replace('subject=', '', 2).rstrip().replace(' /CN=', 'CN = ', 2)  # OpenSSL 1.0 vs 1.2 formatting

    issuer_dn3, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/ca/level3.cert.pem')
    subject_dn3, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/ca/level3.cert.pem')
    issuer_dn3 = issuer_dn3.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    subject_dn3 = subject_dn3.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # He notices that the all certificates seem to be have been issued
    # by correct entity.
    assert issuer_dn1 == subject_dn1
    assert issuer_dn2 == subject_dn1
    assert issuer_dn3 == subject_dn2
    assert subject_dn1 == 'CN = %s Level 1 CA' % tmpdir.basename
    assert subject_dn2 == 'CN = %s Level 2 CA' % tmpdir.basename
    assert subject_dn3 == 'CN = %s Level 3 CA' % tmpdir.basename

    # John opens-up the chain file, and observes that all certificates
    # seem to be contained within.
    with open(".gimmecert/ca/level1.cert.pem", "r") as level1_cert_file:
        level1_cert = level1_cert_file.read()
    with open(".gimmecert/ca/level2.cert.pem", "r") as level2_cert_file:
        level2_cert = level2_cert_file.read()
    with open(".gimmecert/ca/level3.cert.pem", "r") as level3_cert_file:
        level3_cert = level3_cert_file.read()
    with open(".gimmecert/ca/chain-full.cert.pem", "r") as chain_full_file:
        chain_full = chain_full_file.read()

    assert level1_cert in chain_full
    assert level2_cert in chain_full
    assert level3_cert in chain_full

    # Just to make sure, John goes ahead and runs a command that
    # should verify the certificate signatures.
    _, _, error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/ca/level1.cert.pem",
        ".gimmecert/ca/level2.cert.pem",
        ".gimmecert/ca/level3.cert.pem"
    )

    # He is happy to see that verification succeeds.
    assert error_code == 0
