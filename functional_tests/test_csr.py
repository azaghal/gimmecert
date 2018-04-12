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


def test_renew_certificate_originally_issued_with_csr(tmpdir):
    # In one of his past projects, John has initialised CA hierarchy
    # and issued server and client certificate using CSR.
    tmpdir.chdir()

    run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myserver.key.pem",
                "-subj", "/CN=myserver", "-out", "mycustomserver.csr.pem")
    run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myclient.key.pem",
                "-subj", "/CN=myclient", "-out", "mycustomclient.csr.pem")

    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "--csr", "mycustomserver.csr.pem", "myserver")
    run_command("gimmecert", "client", "--csr", "mycustomclient.csr.pem", "myclient")

    # After a while John comes back to the project and has a look at
    # generated artefacts.
    server_old_stored_csr = tmpdir.join(".gimmecert", "server", "myserver.csr.pem").read()
    server_old_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()

    client_old_stored_csr = tmpdir.join(".gimmecert", "client", "myclient.csr.pem").read()
    client_old_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()

    # He decides to renew the certificates to update their
    # validity. First he runs renewal for the server certificate.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "myserver")

    # No errors are shown, and John is informed about generated
    # artefacts. He notices that there is not mention of private key.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for server myserver." in stdout
    assert ".gimmecert/server/myserver.csr.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.key.pem" not in stdout

    # John has a look at generated artefacts.
    server_new_stored_csr = tmpdir.join(".gimmecert", "server", "myserver.csr.pem").read()
    server_new_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.csr.pem")
    server_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    # John notices that the reported CSR has remained unchanged, that
    # the certificate seems to have been updated, and that the public
    # key is the same in CSR and certificate.
    assert server_new_stored_csr == server_old_stored_csr
    assert server_new_certificate != server_old_certificate
    assert server_csr_public_key == server_certificate_public_key

    # John renews the client certificate.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "myclient")

    # No errors are shown, and John is informed about generated
    # artefacts. He notices that there is not mention of private key.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for client myclient." in stdout
    assert ".gimmecert/client/myclient.csr.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.key.pem" not in stdout

    # John has a look at generated artefacts.
    client_new_stored_csr = tmpdir.join(".gimmecert", "client", "myclient.csr.pem").read()
    client_new_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.csr.pem")
    client_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # John notices that the reported CSR has remained unchanged, that
    # the certificate seems to have been updated, and that the public
    # key is the same in CSR and certificate.
    assert client_new_stored_csr == client_old_stored_csr
    assert client_new_certificate != client_old_certificate
    assert client_csr_public_key == client_certificate_public_key
