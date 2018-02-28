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
