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


def test_commands_report_csr_option_as_available():
    # John is in the process of testing a new project deployment. As
    # part of the process, he generates private keys on the servers,
    # and needs to issue corresponding certificates.

    # John knows that he can generate both private key and certificate
    # using Gimmecert, but in this particular case he would like to
    # keep his private keys on the server side intact. John goes ahead
    # and checks if the issuance commands support passing-in a CSR
    # instead of using locally generated private key.

    # He checks help for the server command.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "-h")

    # John notcies the option for passing-in a CSR.
    assert " --csr " in stdout
    assert " -c " in stdout

    # He checks help for the client command.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "-h")

    # John notcies the option for passing-in a CSR.
    assert " --csr " in stdout
    assert " -c " in stdout

    # He checks help for the renew command.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # John notcies the option for passing-in a CSR.
    assert " --csr " in stdout
    assert " -c " in stdout


def test_client_certificate_issuance_by_passing_csr_as_file(tmpdir):
    # John is working on a project where he has already generated
    # client private key.
    tmpdir.chdir()
    run_command("openssl", "genrsa", "-out", "myclient1.key.pem", "2048")

    # However, he still needs to have a CA as a trustpoint, so he goes
    # ahead and initialises Gimmecert for this purpose.
    run_command("gimmecert", "init")

    # Before issuing the certificate, he goes ahead and generates a
    # CSR for the client private key
    run_command("openssl", "req", "-new", "-key", "myclient1.key.pem", "-subj", "/CN=myclient1", "-out", "myclient1.csr.pem")

    # John issues client certificate using CSR.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "--csr", "myclient1.csr.pem", "myclient1")

    # The operation is successful, and he is presented with
    # information about generated artefacts.
    assert exit_code == 0
    assert stderr == ""
    assert ".gimmecert/client/myclient1.cert.pem" in stdout
    assert ".gimmecert/client/myclient1.csr.pem" in stdout

    # John also notices that there is no mention of a private key.
    assert ".gimmecert/client/myclient1.key.pem" not in stdout

    # John notices that the content of stored CSR is identical to the
    # one he provided.
    original_csr = tmpdir.join("myclient1.csr.pem").read()
    stored_csr = tmpdir.join(".gimmecert", "client", "myclient1.csr.pem").read()
    assert original_csr == stored_csr

    # John then quickly has a look at the public key associated with
    # the private key, and public key stored in certificate.
    public_key, _, _ = run_command("openssl", "rsa", "-pubout", "-in", "myclient1.key.pem")
    certificate_public_key, _, _ = run_command("openssl", "x509", "-pubkey", "-noout", "-in", ".gimmecert/client/myclient1.cert.pem")

    # To his delight, they are identical.
    assert certificate_public_key == public_key


def test_server_certificate_issuance_by_passing_csr_as_file(tmpdir):
    # John is working on a project where he has already generated
    # server private key.
    tmpdir.chdir()
    run_command("openssl", "genrsa", "-out", "myserver1.key.pem", "2048")

    # However, he still needs to have a CA as a trustpoint, so he goes
    # ahead and initialises Gimmecert for this purpose.
    run_command("gimmecert", "init")

    # Before issuing the certificate, he goes ahead and generates a
    # CSR for the server private key
    run_command("openssl", "req", "-new", "-key", "myserver1.key.pem", "-subj", "/CN=myserver1", "-out", "myserver1.csr.pem")

    # John issues server certificate using CSR.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "--csr", "myserver1.csr.pem", "myserver1")

    # The operation is successful, and he is presented with
    # information about generated artefacts.
    assert exit_code == 0
    assert stderr == ""
    assert ".gimmecert/server/myserver1.cert.pem" in stdout
    assert ".gimmecert/server/myserver1.csr.pem" in stdout

    # John also notices that there is no mention of a private key.
    assert ".gimmecert/server/myserver1.key.pem" not in stdout

    # John notices that the content of stored CSR is identical to the
    # one he provided.
    original_csr = tmpdir.join("myserver1.csr.pem").read()
    stored_csr = tmpdir.join(".gimmecert", "server", "myserver1.csr.pem").read()
    assert original_csr == stored_csr

    # John then quickly has a look at the public key associated with
    # the private key, and public key stored in certificate.
    public_key, _, _ = run_command("openssl", "rsa", "-pubout", "-in", "myserver1.key.pem")
    certificate_public_key, _, _ = run_command("openssl", "x509", "-pubkey", "-noout", "-in", ".gimmecert/server/myserver1.cert.pem")

    # To his delight, they are identical.
    assert certificate_public_key == public_key
