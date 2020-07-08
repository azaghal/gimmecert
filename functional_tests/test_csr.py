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


from .base import run_command, run_interactive_command


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


def test_client_certificate_issuance_by_passing_csr_as_file_rsa(tmpdir):
    # John is working on a project where he has already generated
    # client RSA private key.
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


def test_server_certificate_issuance_by_passing_csr_as_file_rsa(tmpdir):
    # John is working on a project where he has already generated
    # server RSA private key.
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


def test_renew_certificate_originally_issued_with_csr_rsa(tmpdir):
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


def test_renew_certificate_originally_issued_with_private_key_using_csr_rsa(tmpdir):
    # John has an existing project where he has generated a server and
    # client private key with corresponding CSR.
    tmpdir.chdir()
    run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myserver.key.pem",
                "-subj", "/CN=myserver", "-out", "mycustomserver.csr.pem")
    run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myclient.key.pem",
                "-subj", "/CN=myclient", "-out", "mycustomclient.csr.pem")

    # He wants to grab some certificates for those, so he goes ahead
    # and initialised the CA hierarchy.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    # He proceeds to issue a server and client certificate.
    run_command("gimmecert", "server", "myserver")
    run_command("gimmecert", "client", "myclient")

    # Very quickly John realises that he has mistakenly forgotten to
    # pass-in the relevant CSRs, and that Gimmecert has generated
    # private keys locally and issued certificates for them.
    assert tmpdir.join('.gimmecert', 'server', 'myserver.key.pem').check(file=1)
    assert not tmpdir.join('.gimmecert', 'server', 'myserver.csr.pem').check(file=1)
    assert tmpdir.join('.gimmecert', 'client', 'myclient.key.pem').check(file=1)
    assert not tmpdir.join('.gimmecert', 'client', 'myclient.csr.pem').check(file=1)

    # John has a look at generated artefacts.
    server_old_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_old_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    client_old_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_old_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # He also has a look at the CSRs he generated for both server and
    # client.
    server_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", "mycustomserver.csr.pem")
    server_csr = tmpdir.join("mycustomserver.csr.pem").read()

    client_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", "mycustomclient.csr.pem")
    client_csr = tmpdir.join("mycustomclient.csr.pem").read()

    # He goes ahead and renews the server certificate first,
    # passing-in the CSR this time around.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "--csr", "mycustomserver.csr.pem", "server", "myserver")

    # No errors are shown, and John is informed about generated
    # artefacts, and that the private key has been removed and
    # replaced with the CSR.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for server myserver." in stdout
    assert "Private key used for issuance of previous certificate has been removed, and replaced with the passed-in CSR." in stdout
    assert ".gimmecert/server/myserver.csr.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.key.pem" not in stdout

    # John has a look at generated artefacts.
    server_stored_csr = tmpdir.join(".gimmecert", "server", "myserver.csr.pem").read()
    server_stored_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.csr.pem")

    server_new_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_new_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    # John notices that, for start, the private key has indeed been
    # removed from the filesystem, that the content of the certificate
    # has changed, that the passed-in CSR has been stored, and that
    # public key from the certificate matches the public key in CSR.
    assert not tmpdir.join(".gimmecert", "server", "myserver.key.pem").check()
    assert server_new_certificate != server_old_certificate
    assert server_stored_csr == server_csr
    assert server_new_certificate_public_key == server_csr_public_key

    # John renews the client certificate afterwards, passing-in the
    # CSR this time around.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "--csr", "mycustomclient.csr.pem", "client", "myclient")

    # No errors are shown, and John is informed about generated
    # artefacts, and that the private key has been removed and
    # replaced with the CSR.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for client myclient." in stdout
    assert "Private key used for issuance of previous certificate has been removed, and replaced with the passed-in CSR." in stdout
    assert ".gimmecert/client/myclient.csr.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.key.pem" not in stdout

    # John has a look at generated artefacts.
    client_stored_csr = tmpdir.join(".gimmecert", "client", "myclient.csr.pem").read()
    client_stored_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.csr.pem")

    client_new_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_new_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # John notices that, for start, the private key has indeed been
    # removed from the filesystem, that the content of the certificate
    # has changed, that the passed-in CSR has been stored, and that
    # public key from the certificate matches the public key in CSR.
    assert not tmpdir.join(".gimmecert", "client", "myclient.key.pem").check()
    assert client_new_certificate != client_old_certificate
    assert client_stored_csr == client_csr
    assert client_new_certificate_public_key == client_csr_public_key


def test_renew_certificate_originally_issued_with_csr_using_private_key_rsa(tmpdir):
    # John has an existing project where he has generated a server and
    # client private key with corresponding CSR.
    tmpdir.chdir()
    run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myserver.key.pem",
                "-subj", "/CN=myserver", "-out", "mycustomserver.csr.pem")
    run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myclient.key.pem",
                "-subj", "/CN=myclient", "-out", "mycustomclient.csr.pem")

    # He wants to grab some certificates for those, so he goes ahead
    # and initialises the CA hierarchy.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    # He proceeds to issue a server and client certificate using the
    # CSRs.
    run_command("gimmecert", "server", "--csr", "mycustomserver.csr.pem", "myserver")
    run_command("gimmecert", "client", "--csr", "mycustomserver.csr.pem", "myclient")

    # John has a look at generated artefacts.
    server_old_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_old_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    client_old_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_old_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # John accidentally removes the generated private keys.
    tmpdir.join('myserver.key.pem').remove()
    tmpdir.join('myclient.key.pem').remove()

    # He realises that the issued certificates are now useless to him,
    # and decides to renew the certificates and let Gimmecert generate
    # private keys for him.

    # He goes ahead and renews the server certificate first,
    # requesting a new private key along the way.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "--new-private-key", "server", "myserver")

    # No errors are shown, and John is informed about generated
    # artefacts, and that the CSR has been replaced with a generated
    # private key.
    assert exit_code == 0
    assert stderr == ""
    assert "Generated new private key and renewed certificate for server myserver." in stdout
    assert "CSR used for issuance of previous certificate has been removed, and a private key has been generated in its place." in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.csr.pem" not in stdout

    # John has a look at generated artefacts.
    server_generated_private_key_public_key, _, _ = run_command("openssl", "rsa", "-pubout", "-in", ".gimmecert/server/myserver.key.pem")

    server_new_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_new_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    # John notices that, for start, the CSR has indeed been removed
    # from the filesystem, that the content of the certificate has
    # changed, that the old public key is not the same as the new one,
    # and that public key from the certificate matches with the
    # private key.
    assert not tmpdir.join(".gimmecert", "server", "myserver.csr.pem").check()
    assert server_new_certificate != server_old_certificate
    assert server_old_certificate_public_key != server_generated_private_key_public_key
    assert server_new_certificate_public_key == server_generated_private_key_public_key

    # He goes ahead and renews the client certificate first,
    # requesting a new private key along the way.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "--new-private-key", "client", "myclient")

    # No errors are shown, and John is informed about generated
    # artefacts, and that the CSR has been replaced with a generated
    # private key.
    assert exit_code == 0
    assert stderr == ""
    assert "Generated new private key and renewed certificate for client myclient." in stdout
    assert "CSR used for issuance of previous certificate has been removed, and a private key has been generated in its place." in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.csr.pem" not in stdout

    # John has a look at generated artefacts.
    client_generated_private_key_public_key, _, _ = run_command("openssl", "rsa", "-pubout", "-in", ".gimmecert/client/myclient.key.pem")

    client_new_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_new_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # John notices that, for start, the CSR has indeed been removed
    # from the filesystem, that the content of the certificate has
    # changed, that the old public key is not the same as the new one,
    # and that public key from the certificate matches with the
    # private key.
    assert not tmpdir.join(".gimmecert", "client", "myclient.csr.pem").check()
    assert client_new_certificate != client_old_certificate
    assert client_old_certificate_public_key != client_generated_private_key_public_key
    assert client_new_certificate_public_key == client_generated_private_key_public_key


def test_server_command_accepts_csr_from_stdin(tmpdir):
    # John is working on a project where he has already generated
    # server private key.
    tmpdir.chdir()
    run_command("openssl", "genrsa", "-out", "myserver1.key.pem", "2048")

    # However, he still needs to have a CA as a trustpoint, so he goes
    # ahead and initialises Gimmecert for this purpose.
    run_command("gimmecert", "init")

    # Before issuing the certificate, he generates a CSR for the
    # server private key.
    custom_csr, _, exit_code = run_command("openssl", "req", "-new", "-key", "myserver1.key.pem", "-subj", "/CN=myserver1")

    # John realises that although the CSR generation was successful, he
    # forgot to output it to a file.
    assert exit_code == 0
    assert "BEGIN CERTIFICATE REQUEST" in custom_csr
    assert "END CERTIFICATE REQUEST" in custom_csr

    # He could output the CSR into a file, and feed that into
    # Gimmecert, but he feels a bit lazy. Instead, John tries to pass
    # in a dash ("-") as input, knowing that it is commonly used as
    # shorthand for reading from standard input.
    prompt_failure, output, exit_code = run_interactive_command([], "gimmecert", "server", "--csr", "-", "myserver1")

    # John sees that the application has prompted him to provide the
    # CSR interactively, and that it waits for his input.
    assert exit_code is None, "Output was: %s" % output
    assert prompt_failure == "Command got stuck waiting for input.", "Output was: %s" % output
    assert "Please enter the CSR (finish with Ctrl-D on an empty line):" in output

    # John reruns the command, this time passing-in the CSR and ending
    # the input with Ctrl-D.
    prompt_failure, output, exit_code = run_interactive_command([(r'Please enter the CSR \(finish with Ctrl-D on an empty line\):', custom_csr + '\n\004')],
                                                                "gimmecert", "server", "--csr", "-", "myserver1")

    # The operation is successful, and he is presented with
    # information about generated artefacts.
    assert prompt_failure is None
    assert exit_code == 0
    assert ".gimmecert/server/myserver1.cert.pem" in output
    assert ".gimmecert/server/myserver1.csr.pem" in output

    # John also notices that there is no mention of a private key.
    assert ".gimmecert/server/myserver1.key.pem" not in output

    # John notices that the content of stored CSR is identical to the
    # one he provided.
    stored_csr = tmpdir.join(".gimmecert", "server", "myserver1.csr.pem").read()
    assert custom_csr == stored_csr

    # John then quickly has a look at the public key associated with
    # the private key, and public key stored in certificate.
    public_key, _, _ = run_command("openssl", "rsa", "-pubout", "-in", "myserver1.key.pem")
    certificate_public_key, _, _ = run_command("openssl", "x509", "-pubkey", "-noout", "-in", ".gimmecert/server/myserver1.cert.pem")

    # To his delight, they are identical.
    assert certificate_public_key == public_key


def test_client_command_accepts_csr_from_stdin(tmpdir):
    # John is working on a project where he has already generated
    # client private key.
    tmpdir.chdir()
    run_command("openssl", "genrsa", "-out", "myclient1.key.pem", "2048")

    # However, he still needs to have a CA as a trustpoint, so he goes
    # ahead and initialises Gimmecert for this purpose.
    run_command("gimmecert", "init")

    # Before issuing the certificate, he generates a CSR for the
    # client private key.
    custom_csr, _, exit_code = run_command("openssl", "req", "-new", "-key", "myclient1.key.pem", "-subj", "/CN=myclient1")

    # John realises that although the CSR generation was successful, he
    # forgot to output it to a file.
    assert exit_code == 0
    assert "BEGIN CERTIFICATE REQUEST" in custom_csr
    assert "END CERTIFICATE REQUEST" in custom_csr

    # He could output the CSR into a file, and feed that into
    # Gimmecert, but he feels a bit lazy. Instead, John tries to pass
    # in a dash ("-") as input, knowing that it is commonly used as
    # shorthand for reading from standard input.
    prompt_failure, output, exit_code = run_interactive_command([], "gimmecert", "client", "--csr", "-", "myclient1")

    # John sees that the application has prompted him to provide the
    # CSR interactively, and that it waits for his input.
    assert exit_code is None, "Output was: %s" % output
    assert prompt_failure == "Command got stuck waiting for input.", "Output was: %s" % output
    assert "Please enter the CSR (finish with Ctrl-D on an empty line):" in output

    # John reruns the command, this time passing-in the CSR and ending
    # the input with Ctrl-D.
    prompt_failure, output, exit_code = run_interactive_command([(r'Please enter the CSR \(finish with Ctrl-D on an empty line\):', custom_csr + '\n\004')],
                                                                "gimmecert", "client", "--csr", "-", "myclient1")

    # The operation is successful, and he is presented with
    # information about generated artefacts.
    assert prompt_failure is None
    assert exit_code == 0
    assert ".gimmecert/client/myclient1.cert.pem" in output
    assert ".gimmecert/client/myclient1.csr.pem" in output

    # John also notices that there is no mention of a private key.
    assert ".gimmecert/client/myclient1.key.pem" not in output

    # John notices that the content of stored CSR is identical to the
    # one he provided.
    stored_csr = tmpdir.join(".gimmecert", "client", "myclient1.csr.pem").read()
    assert custom_csr == stored_csr

    # John then quickly has a look at the public key associated with
    # the private key, and public key stored in certificate.
    public_key, _, _ = run_command("openssl", "rsa", "-pubout", "-in", "myclient1.key.pem")
    certificate_public_key, _, _ = run_command("openssl", "x509", "-pubkey", "-noout", "-in", ".gimmecert/client/myclient1.cert.pem")

    # To his delight, they are identical.
    assert certificate_public_key == public_key


def test_renew_command_accepts_csr_from_stdin(tmpdir):
    # John has an existing project where he has generated a server and
    # client private key with corresponding CSR.
    tmpdir.chdir()
    server_csr, _, server_csr_exit_code = run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myserver.key.pem",
                                                      "-subj", "/CN=myserver")
    client_csr, _, client_csr_exit_code = run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myclient.key.pem",
                                                      "-subj", "/CN=myclient")

    # John realises that although the CSR generation was successful, he
    # forgot to output them to a file.
    assert server_csr_exit_code == 0
    assert "BEGIN CERTIFICATE REQUEST" in server_csr
    assert "END CERTIFICATE REQUEST" in server_csr

    assert client_csr_exit_code == 0
    assert "BEGIN CERTIFICATE REQUEST" in client_csr
    assert "END CERTIFICATE REQUEST" in client_csr

    # He could output the CSR into a file, and feed that into
    # Gimmecert, but he feels a bit lazy. Instead, John tries to pass
    # in a dash ("-") as input, knowing that it is commonly used as
    # shorthand for reading from standard input.

    # He goes ahead and initalises the CA hierarchy first.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    # He proceeds to issue a server and client certificate.
    run_command("gimmecert", "server", "myserver")
    run_command("gimmecert", "client", "myclient")

    # Very quickly John realises that he has mistakenly forgotten to
    # pass-in the relevant CSRs, and that Gimmecert has generated
    # private keys locally and issued certificates for them.
    assert tmpdir.join('.gimmecert', 'server', 'myserver.key.pem').check(file=1)
    assert not tmpdir.join('.gimmecert', 'server', 'myserver.csr.pem').check(file=1)
    assert tmpdir.join('.gimmecert', 'client', 'myclient.key.pem').check(file=1)
    assert not tmpdir.join('.gimmecert', 'client', 'myclient.csr.pem').check(file=1)

    # He has a look at the public key from the generated CSRs (that he
    # originally wanted to use).
    tmpfile = tmpdir.join('tempfile')

    tmpfile.write(server_csr)
    server_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", tmpfile.strpath)

    tmpfile.write(client_csr)
    client_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", tmpfile.strpath)

    # The renew command can accept a CSR to replace existing artifact
    # used for original issuance. He could output the CSRs into a
    # file, and feed that into Gimmecert, but he feels a bit
    # lazy. Instead, John tries to pass in a dash ("-") as input to
    # the renew command, knowing that it is commonly used as shorthand
    # for reading from standard input.
    renew_server_prompt_failure, renew_server_output, renew_server_exit_code = run_interactive_command(
        [],
        "gimmecert", "renew", "--csr", "-", "server", "myserver"
    )
    renew_client_prompt_failure, renew_client_output, renew_client_exit_code = run_interactive_command(
        [], "gimmecert", "renew", "--csr", "-", "client", "myclient"
    )

    # John sees that the application has prompted him to provide the
    # CSR interactively for both server and client certificate
    # renewal, and that it waits for his input.
    assert renew_server_exit_code is None, "Output was: %s" % renew_server_output
    assert renew_server_prompt_failure == "Command got stuck waiting for input.", "Output was: %s" % renew_server_output
    assert "Please enter the CSR (finish with Ctrl-D on an empty line):" in renew_server_output

    assert renew_server_exit_code is None, "Output was: %s" % renew_client_output
    assert renew_client_prompt_failure == "Command got stuck waiting for input.", "Output was: %s" % renew_client_output
    assert "Please enter the CSR (finish with Ctrl-D on an empty line):" in renew_client_output

    # John reruns renewal commands, this time passing-in the CSR and
    # ending the input with Ctrl-D.
    renew_server_prompt_failure, renew_server_output, renew_server_exit_code = run_interactive_command(
        [(r'Please enter the CSR \(finish with Ctrl-D on an empty line\):', server_csr + '\n\004')],
        "gimmecert", "renew", "--csr", "-", "server", "myserver"
    )

    renew_client_prompt_failure, renew_client_output, renew_client_exit_code = run_interactive_command(
        [(r'Please enter the CSR \(finish with Ctrl-D on an empty line\):', client_csr + '\n\004')],
        "gimmecert", "renew", "--csr", "-", "client", "myclient"
    )

    # The operation is successful, and he is presented with
    # information about generated artefacts.
    assert renew_server_prompt_failure is None
    assert renew_server_exit_code == 0
    assert ".gimmecert/server/myserver.cert.pem" in renew_server_output
    assert ".gimmecert/server/myserver.csr.pem" in renew_server_output

    assert renew_client_prompt_failure is None
    assert renew_client_exit_code == 0
    assert ".gimmecert/client/myclient.cert.pem" in renew_client_output
    assert ".gimmecert/client/myclient.csr.pem" in renew_client_output

    # John also notices that there is no mention of a private key.
    assert ".gimmecert/server/myserver.key.pem" not in renew_server_output
    assert ".gimmecert/client/myclient.key.pem" not in renew_client_output

    # John notices that the content of stored CSRs is identical to the
    # ones he provided.
    server_stored_csr = tmpdir.join(".gimmecert", "server", "myserver.csr.pem").read()
    assert server_stored_csr == server_csr

    client_stored_csr = tmpdir.join(".gimmecert", "client", "myclient.csr.pem").read()
    assert client_stored_csr == client_csr

    # John then quickly has a look at the public key from passed-in
    # CSR and compares it to the one stored in certificate.
    server_certificate_public_key, _, _ = run_command("openssl", "x509", "-pubkey", "-noout", "-in", ".gimmecert/server/myserver.cert.pem")
    client_certificate_public_key, _, _ = run_command("openssl", "x509", "-pubkey", "-noout", "-in", ".gimmecert/client/myclient.cert.pem")

    # To his delight, they are identical.
    assert server_certificate_public_key == server_csr_public_key
    assert client_certificate_public_key == client_csr_public_key


def test_client_certificate_issuance_by_passing_csr_as_file_ecdsa(tmpdir):
    # John is working on a project where he has already generated
    # client ECDSA private key.
    tmpdir.chdir()
    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myclient1.key.pem", "-name", "secp256r1")

    # However, he still needs to have a CA as a trustpoint, so he goes
    # ahead and initialises Gimmecert for this purpose.
    run_command("gimmecert", "init")

    # Before issuing the certificate, he goes ahead and generates a
    # CSR for the client private key.
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
    public_key, _, _ = run_command("openssl", "ec", "-pubout", "-in", "myclient1.key.pem")
    certificate_public_key, _, _ = run_command("openssl", "x509", "-pubkey", "-noout", "-in", ".gimmecert/client/myclient1.cert.pem")

    # To his delight, they are identical.
    assert certificate_public_key == public_key


def test_server_certificate_issuance_by_passing_csr_as_file_ecdsa(tmpdir):
    # John is working on a project where he has already generated
    # server ECDSA private key.
    tmpdir.chdir()
    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myserver1.key.pem", "-name", "secp256r1")

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
    public_key, _, _ = run_command("openssl", "ec", "-pubout", "-in", "myserver1.key.pem")
    certificate_public_key, _, _ = run_command("openssl", "x509", "-pubkey", "-noout", "-in", ".gimmecert/server/myserver1.cert.pem")

    # To his delight, they are identical.
    assert certificate_public_key == public_key


def test_renew_certificate_originally_issued_with_csr_ecdsa(tmpdir):
    # In one of his past projects, John has initialised CA hierarchy
    # and issued server and client certificate using CSR.
    tmpdir.chdir()

    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myserver.key.pem", "-name", "secp256r1")
    run_command("openssl", "req", "-new", "-key", "myserver.key.pem", "-subj", "/CN=myserver", "-out", "mycustomserver.csr.pem")

    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myclient.key.pem", "-name", "secp256r1")
    run_command("openssl", "req", "-new", "-key", "myclient.key.pem", "-subj", "/CN=myserver", "-out", "mycustomclient.csr.pem")

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


def test_renew_certificate_originally_issued_with_private_key_using_csr_ecdsa(tmpdir):
    # John has an existing project where he has generated a server and
    # client private key with corresponding CSR.
    tmpdir.chdir()

    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myserver.key.pem", "-name", "secp256r1")
    run_command("openssl", "req", "-new", "-key", "myserver.key.pem", "-subj", "/CN=myserver", "-out", "mycustomserver.csr.pem")

    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myclient.key.pem", "-name", "secp256r1")
    run_command("openssl", "req", "-new", "-key", "myclient.key.pem", "-subj", "/CN=myserver", "-out", "mycustomclient.csr.pem")

    # He wants to grab some certificates for those, so he goes ahead
    # and initialised the CA hierarchy.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    # He proceeds to issue a server and client certificate.
    run_command("gimmecert", "server", "myserver")
    run_command("gimmecert", "client", "myclient")

    # Very quickly John realises that he has mistakenly forgotten to
    # pass-in the relevant CSRs, and that Gimmecert has generated
    # private keys locally and issued certificates for them.
    assert tmpdir.join('.gimmecert', 'server', 'myserver.key.pem').check(file=1)
    assert not tmpdir.join('.gimmecert', 'server', 'myserver.csr.pem').check(file=1)
    assert tmpdir.join('.gimmecert', 'client', 'myclient.key.pem').check(file=1)
    assert not tmpdir.join('.gimmecert', 'client', 'myclient.csr.pem').check(file=1)

    # John has a look at generated artefacts.
    server_old_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_old_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    client_old_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_old_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # He also has a look at the CSRs he generated for both server and
    # client.
    server_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", "mycustomserver.csr.pem")
    server_csr = tmpdir.join("mycustomserver.csr.pem").read()

    client_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", "mycustomclient.csr.pem")
    client_csr = tmpdir.join("mycustomclient.csr.pem").read()

    # He goes ahead and renews the server certificate first,
    # passing-in the CSR this time around.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "--csr", "mycustomserver.csr.pem", "server", "myserver")

    # No errors are shown, and John is informed about generated
    # artefacts, and that the private key has been removed and
    # replaced with the CSR.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for server myserver." in stdout
    assert "Private key used for issuance of previous certificate has been removed, and replaced with the passed-in CSR." in stdout
    assert ".gimmecert/server/myserver.csr.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.key.pem" not in stdout

    # John has a look at generated artefacts.
    server_stored_csr = tmpdir.join(".gimmecert", "server", "myserver.csr.pem").read()
    server_stored_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.csr.pem")

    server_new_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_new_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    # John notices that, for start, the private key has indeed been
    # removed from the filesystem, that the content of the certificate
    # has changed, that the passed-in CSR has been stored, and that
    # public key from the certificate matches the public key in CSR.
    assert not tmpdir.join(".gimmecert", "server", "myserver.key.pem").check()
    assert server_new_certificate != server_old_certificate
    assert server_stored_csr == server_csr
    assert server_new_certificate_public_key == server_csr_public_key

    # John renews the client certificate afterwards, passing-in the
    # CSR this time around.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "--csr", "mycustomclient.csr.pem", "client", "myclient")

    # No errors are shown, and John is informed about generated
    # artefacts, and that the private key has been removed and
    # replaced with the CSR.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for client myclient." in stdout
    assert "Private key used for issuance of previous certificate has been removed, and replaced with the passed-in CSR." in stdout
    assert ".gimmecert/client/myclient.csr.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.key.pem" not in stdout

    # John has a look at generated artefacts.
    client_stored_csr = tmpdir.join(".gimmecert", "client", "myclient.csr.pem").read()
    client_stored_csr_public_key, _, _ = run_command("openssl", "req", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.csr.pem")

    client_new_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_new_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # John notices that, for start, the private key has indeed been
    # removed from the filesystem, that the content of the certificate
    # has changed, that the passed-in CSR has been stored, and that
    # public key from the certificate matches the public key in CSR.
    assert not tmpdir.join(".gimmecert", "client", "myclient.key.pem").check()
    assert client_new_certificate != client_old_certificate
    assert client_stored_csr == client_csr
    assert client_new_certificate_public_key == client_csr_public_key


def test_renew_certificate_originally_issued_with_csr_using_private_key_ecdsa(tmpdir):
    # John has an existing project where he has generated a server and
    # client private key with corresponding CSR.
    tmpdir.chdir()

    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myserver.key.pem", "-name", "secp256r1")
    run_command("openssl", "req", "-new", "-key", "myserver.key.pem", "-subj", "/CN=myserver", "-out", "mycustomserver.csr.pem")

    run_command("openssl", "ecparam", "-genkey", "-noout", "-out", "myclient.key.pem", "-name", "secp256r1")
    run_command("openssl", "req", "-new", "-key", "myclient.key.pem", "-subj", "/CN=myserver", "-out", "mycustomclient.csr.pem")

    # He wants to grab some certificates for those, so he goes ahead
    # and initialises the CA hierarchy.
    tmpdir.chdir()
    run_command("gimmecert", "init")

    # He proceeds to issue a server and client certificate using the
    # CSRs.
    run_command("gimmecert", "server", "--csr", "mycustomserver.csr.pem", "myserver")
    run_command("gimmecert", "client", "--csr", "mycustomserver.csr.pem", "myclient")

    # John has a look at generated artefacts.
    server_old_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_old_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    client_old_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_old_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # John accidentally removes the generated private keys.
    tmpdir.join('myserver.key.pem').remove()
    tmpdir.join('myclient.key.pem').remove()

    # He realises that the issued certificates are now useless to him,
    # and decides to renew the certificates and let Gimmecert generate
    # private keys for him.

    # He goes ahead and renews the server certificate first,
    # requesting a new private key along the way.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "--new-private-key", "server", "myserver")

    # No errors are shown, and John is informed about generated
    # artefacts, and that the CSR has been replaced with a generated
    # private key.
    assert exit_code == 0
    assert stderr == ""
    assert "Generated new private key and renewed certificate for server myserver." in stdout
    assert "CSR used for issuance of previous certificate has been removed, and a private key has been generated in its place." in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout
    assert ".gimmecert/server/myserver.csr.pem" not in stdout

    # John has a look at generated artefacts.
    server_generated_private_key_public_key, _, _ = run_command("openssl", "ec", "-pubout", "-in", ".gimmecert/server/myserver.key.pem")

    server_new_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    server_new_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/server/myserver.cert.pem")

    # John notices that, for start, the CSR has indeed been removed
    # from the filesystem, that the content of the certificate has
    # changed, that the old public key is not the same as the new one,
    # and that public key from the certificate matches with the
    # private key.
    assert not tmpdir.join(".gimmecert", "server", "myserver.csr.pem").check()
    assert server_new_certificate != server_old_certificate
    assert server_old_certificate_public_key != server_generated_private_key_public_key
    assert server_new_certificate_public_key == server_generated_private_key_public_key

    # He goes ahead and renews the client certificate first,
    # requesting a new private key along the way.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "--new-private-key", "client", "myclient")

    # No errors are shown, and John is informed about generated
    # artefacts, and that the CSR has been replaced with a generated
    # private key.
    assert exit_code == 0
    assert stderr == ""
    assert "Generated new private key and renewed certificate for client myclient." in stdout
    assert "CSR used for issuance of previous certificate has been removed, and a private key has been generated in its place." in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout
    assert ".gimmecert/client/myclient.csr.pem" not in stdout

    # John has a look at generated artefacts.
    client_generated_private_key_public_key, _, _ = run_command("openssl", "ec", "-pubout", "-in", ".gimmecert/client/myclient.key.pem")

    client_new_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()
    client_new_certificate_public_key, _, _ = run_command("openssl", "x509", "-noout", "-pubkey", "-in", ".gimmecert/client/myclient.cert.pem")

    # John notices that, for start, the CSR has indeed been removed
    # from the filesystem, that the content of the certificate has
    # changed, that the old public key is not the same as the new one,
    # and that public key from the certificate matches with the
    # private key.
    assert not tmpdir.join(".gimmecert", "client", "myclient.csr.pem").check()
    assert client_new_certificate != client_old_certificate
    assert client_old_certificate_public_key != client_generated_private_key_public_key
    assert client_new_certificate_public_key == client_generated_private_key_public_key
