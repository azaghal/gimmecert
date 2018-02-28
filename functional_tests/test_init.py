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
    assert "CA hierarchy initialised" in stdout

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
    issuer_dn = issuer_dn.replace('issuer=', '', 1)
    subject_dn = subject_dn.replace('subject=', '', 1)

    # He notices that the issuer and subject DN are identical (since
    # it's a root CA certificate), and can also see that the subject
    # DN has just the CN with working directory's name in it.
    assert issuer_dn == subject_dn
    assert subject_dn.rstrip() == 'CN = %s Level 1' % tmpdir.basename

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
    assert exit_code == 0
    assert stderr == ""
    assert "CA hierarchy has already been initialised." in stdout


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
    assert "-b" in stdout

    # John switches to his project directory.
    tmpdir.chdir()

    # This time around he runs the command using the newly-found
    # option.
    stdout, stderr, exit_code = run_command('gimmecert', 'init', '--ca-base-name', 'My Project')

    # Command finishes execution with success, and he is informed that
    # his CA hierarchy has been initialised..
    assert exit_code == 0
    assert stderr == ""
    assert "CA hierarchy initialised." in stdout

    # Just before he starts using the CA certificates further, he
    # decides to double-check the results. He runs a couple of
    # commands to get the issuer and subject DN from generated
    # certificate.
    issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/ca/level1.cert.pem')
    subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/ca/level1.cert.pem')
    issuer_dn = issuer_dn.replace('issuer=', '', 1)
    subject_dn = subject_dn.replace('subject=', '', 1)

    # To his delight, both the issuer and subject DN are identical,
    # and now they are based on his custom-provided name instead of
    # project name.
    assert issuer_dn.rstrip() == subject_dn.rstrip() == "CN = My Project Level 1"
    assert tmpdir.basename not in issuer_dn
