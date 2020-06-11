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


def test_renew_command_available_with_help():
    # John has been issuing server and client certificates using
    # Gimmecert for a while now. The project has been in use for quite
    # some time, and John has realised the certificates might be about
    # to expire. Thinking how tedious it would be to generate
    # everything again from scratch, he tries to figure out if there
    # is an easier way to do it instead of providing information for
    # all of the entities instead.
    stdout, stderr, exit_code = run_command("gimmecert")

    # Looking at output, John notices the renew command.
    assert exit_code == 0
    assert stderr == ""
    assert "renew" in stdout

    # He goes ahead and has a look at command invocation to check what
    # kind of parameters he might need to provide.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # John can see that the command accepts two positional argument -
    # type of entity, and entity name.
    assert exit_code == 0
    assert stderr == ""
    assert stdout.startswith("usage: gimmecert renew")
    assert stdout.split('\n')[3].endswith("{server,client} entity_name")  # Fourth line of help (first two are options)


def test_renew_command_requires_initialised_hierarchy(tmpdir):
    # John decides it's time to renew one of the certificates. He
    # switches to his project directory.
    tmpdir.chdir()

    # John tries to renew a server certificate.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "myserver")

    # John has forgotten to initialise the CA hierarchy from within
    # this directory, and is instead presented with an error.
    assert exit_code != 0
    assert stdout == ""
    assert stderr == "No CA hierarchy has been initialised yet. Run the gimmecert init command and issue some certificates first.\n"

    # John gives the screen a weird look, and tries again, this time
    # with a client certificate renewal.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "myclient")

    # John gets presented with the same error yet again. Suddenly, he
    # realizes he is in a wrong directory... Oh well...
    assert exit_code != 0
    assert stdout == ""
    assert stderr == "No CA hierarchy has been initialised yet. Run the gimmecert init command and issue some certificates first.\n"


def test_renew_command_reports_error_if_entity_does_not_exist(tmpdir):
    # John finally finds his way around to the project directory where
    # Gimmecert has already been used to set-up a hierarchy, and where
    # a couple of server and client certificates have been issued.
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "someserver")
    run_command("gimmecert", "client", "someclient")

    # He runs the command for renewing a server certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'server', 'myserver')

    # Unfortunately for him, this server certificate has not been
    # issued before, and he is presented with an error.
    assert exit_code != 0
    assert stdout == ''
    assert stderr == "Cannot renew certificate. No existing certificate found for server myserver.\n"

    # This is going to be one of those days... He tries then to renew
    # a client certificate instead.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'client', 'myclient')

    # To his dismay, this results in error as well. He hasn't issued
    # such a certificate before either.
    assert exit_code != 0
    assert stdout == ''
    assert stderr == "Cannot renew certificate. No existing certificate found for client myclient.\n"


def test_renew_only_certificate(tmpdir):
    # At the end of his wits, John finally finds the correct project
    # directory where he has previuosly set-up the CA hierarchy and
    # issued a couple of certificates.
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "myserver", "myserver.local")
    run_command("gimmecert", "client", "myclient")

    # He fetches some information about the existing certificates.
    old_server_private_key = tmpdir.join(".gimmecert", "server", "myserver.key.pem").read()
    old_server_issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/server/myserver.cert.pem')
    old_server_subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/server/myserver.cert.pem')
    old_server_public_key, _, _ = run_command('openssl', 'x509', '-noout', '-pubkey', '-in', '.gimmecert/server/myserver.cert.pem')
    old_server_certificate_info, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver.cert.pem')
    old_server_issuer_dn = old_server_issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    old_server_subject_dn = old_server_subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    old_client_private_key = tmpdir.join(".gimmecert", "client", "myclient.key.pem").read()
    old_client_issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/client/myclient.cert.pem')
    old_client_subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/client/myclient.cert.pem')
    old_client_public_key, _, _ = run_command('openssl', 'x509', '-noout', '-pubkey', '-in', '.gimmecert/client/myclient.cert.pem')
    old_client_certificate_info, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/client/myclient.cert.pem')
    old_client_issuer_dn = old_client_issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    old_client_subject_dn = old_client_subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # He runs the renewal command for server certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'server', 'myserver')

    # No errors are reported, and he is presented with a nice
    # informative message about certificate being renewed, as well as
    # paths to artifacts.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for server myserver." in stdout
    assert ".gimmecert/server/myserver.key.pem" in stdout
    assert ".gimmecert/server/myserver.cert.pem" in stdout

    # He does the same for the client certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'client', 'myclient')

    # No errors are reported, and he is presented with a nice
    # informative message about certificate being renewed, as well as
    # paths to artifacts.
    assert exit_code == 0
    assert stderr == ""
    assert "Renewed certificate for client myclient." in stdout
    assert ".gimmecert/client/myclient.key.pem" in stdout
    assert ".gimmecert/client/myclient.cert.pem" in stdout

    # John has a look at generated certificates.
    new_server_private_key = tmpdir.join(".gimmecert", "server", "myserver.key.pem").read()
    new_server_issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/server/myserver.cert.pem')
    new_server_subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/server/myserver.cert.pem')
    new_server_public_key, _, _ = run_command('openssl', 'x509', '-noout', '-pubkey', '-in', '.gimmecert/server/myserver.cert.pem')
    new_server_certificate_info, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver.cert.pem')
    new_server_issuer_dn = new_server_issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    new_server_subject_dn = new_server_subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    new_client_private_key = tmpdir.join(".gimmecert", "client", "myclient.key.pem").read()
    new_client_issuer_dn, _, _ = run_command('openssl', 'x509', '-noout', '-issuer', '-in', '.gimmecert/client/myclient.cert.pem')
    new_client_subject_dn, _, _ = run_command('openssl', 'x509', '-noout', '-subject', '-in', '.gimmecert/client/myclient.cert.pem')
    new_client_public_key, _, _ = run_command('openssl', 'x509', '-noout', '-pubkey', '-in', '.gimmecert/client/myclient.cert.pem')
    new_client_certificate_info, _, _ = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/client/myclient.cert.pem')
    new_client_issuer_dn = new_client_issuer_dn.replace('issuer=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting
    new_client_subject_dn = new_client_subject_dn.replace('subject=', '', 1).rstrip().replace(' /CN=', 'CN = ', 1)  # OpenSSL 1.0 vs 1.1 formatting

    # John compares the values from old certificates and new
    # certificates. To his delight, the same private key and naming
    # have been reused, but the certificates have definitively been
    # replaced.
    assert new_server_private_key == old_server_private_key
    assert new_server_issuer_dn == old_server_issuer_dn
    assert new_server_subject_dn == old_server_subject_dn
    assert new_server_public_key == old_server_public_key
    assert "DNS:myserver, DNS:myserver.local\n" in new_server_certificate_info
    assert new_server_certificate_info != old_server_certificate_info

    assert new_client_private_key == old_client_private_key
    assert new_client_issuer_dn == old_client_issuer_dn
    assert new_client_subject_dn == old_client_subject_dn
    assert new_client_public_key == old_client_public_key
    assert new_client_certificate_info != old_client_certificate_info

    # Finally, he runs a check to ensure the certificates can be
    # verified using the CA certificate chain.
    _, _, verify_server_error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/server/myserver.cert.pem"
    )

    _, _, verify_client_error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/client/myclient.cert.pem"
    )

    # He is happy to see that verification succeeds.
    assert verify_server_error_code == 0
    assert verify_client_error_code == 0


def test_renew_both_certificate_and_private_key(tmpdir):
    # John wants to replace private keys in one of his projects for
    # testing purposes to ensure the service is capable of reloading a
    # new key on the fly. He switches to project directory (where he
    # had previously set-up the CA hierarchy and issued some
    # certificates).
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "myserver", "myserver.local")
    run_command("gimmecert", "client", "myclient")

    # He is curious if there might be some built-in option to perform
    # this action. He has a look at the renew command CLI help.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # He notices the option for generating a new private key.
    assert exit_code == 0
    assert stderr == ""
    assert "--new-private-key, -p\n" in stdout

    # Before proceeding, John has a quick look at the existing private
    # keys and certificats.
    old_server_private_key = tmpdir.join(".gimmecert", "server", "myserver.key.pem").read()
    old_server_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    old_client_private_key = tmpdir.join(".gimmecert", "client", "myclient.key.pem").read()
    old_client_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()

    # He runs the renewal command for server certificate, requesting
    # the private key to be regenerated.
    stdout, stderrr, exit_code = run_command("gimmecert", "renew", "--new-private-key", "server", "myserver")

    # No errors are reported, and he is informed that both private key
    # and certificate have been renewed.
    assert exit_code == 0
    assert stderr == ""
    assert "Generated new private key and renewed certificate for server myserver." in stdout

    # He runs the same command for the client entity.
    stdout, stderrr, exit_code = run_command("gimmecert", "renew", "--new-private-key", "client", "myclient")

    # No errors are reported, and he is informed that both private key
    # and certificate have been renewed.
    assert exit_code == 0
    assert stderr == ""
    assert "Generated new private key and renewed certificate for client myclient." in stdout

    # John has a quick peek at the newly generated artifacts.
    new_server_private_key = tmpdir.join(".gimmecert", "server", "myserver.key.pem").read()
    new_server_certificate = tmpdir.join(".gimmecert", "server", "myserver.cert.pem").read()
    new_client_private_key = tmpdir.join(".gimmecert", "client", "myclient.key.pem").read()
    new_client_certificate = tmpdir.join(".gimmecert", "client", "myclient.cert.pem").read()

    # Seems like both private key and certificate have been replaced
    # for both server and client.
    assert old_server_private_key != new_server_private_key
    assert old_server_certificate != new_server_certificate
    assert old_client_private_key != new_client_private_key
    assert old_client_certificate != new_client_certificate

    # Finally, he runs a check to ensure the certificates can be
    # verified using the CA certificate chain.
    _, _, verify_server_error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/server/myserver.cert.pem"
    )

    _, _, verify_client_error_code = run_command(
        "openssl", "verify",
        "-CAfile",
        ".gimmecert/ca/chain-full.cert.pem",
        ".gimmecert/client/myclient.cert.pem"
    )

    # He is happy to see that verification succeeds.
    assert verify_server_error_code == 0
    assert verify_client_error_code == 0


def test_renew_update_dns_option(tmpdir):
    # John is in a bit of a rush to get his project going. Since he
    # needs a server certificate issued, he goes ahead and quickly
    # initialises CA and issues a server certificate, with intention
    # of accessing the service via URL https://myservice.example.com/.
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "myserver1", "mysercive.example.com")

    # Once he imports the CA certificate into his browser, and tries
    # to access the service page, he very quickly finds out that he
    # has misspelled "myservice". Just to be on the safe side, he has
    # a look at the certificate using the OpenSSL CLI.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver1.cert.pem')

    # And indeed, in addition to his server name, he can see that the
    # extra DNS subject alternative name he provided is wrong.
    assert "DNS:myserver1," in stdout
    assert "DNS:mysercive.example.com\n" in stdout
    assert "DNS:myservice.example.com" not in stdout

    # Since he wants to just replace the certificate, while preserving
    # the private key, John figures he needs to renew his certificate
    # somehow, and update the DNS names while doing so. He takes a
    # quick look at help for the renew command.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # He notices there is an option for updating DNS subject
    # alternative names.
    assert " --update-dns-names DNS_NAMES" in stdout
    assert " -u DNS_NAMES\n" in stdout

    # Based on help description, this seems to be exactly what he
    # needs.He goes ahead and runs the renewal command, specifying
    # correct DNS subject alternative names.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "--update-dns-names", "myservice.example.com", "myserver1")

    # He notices that no error has been reported by the command, and
    # that he is informed that the certificate has been renewed with
    # new DNS names, while the private key has been preserved.
    assert exit_code == 0
    assert "subject alternative names have been updated" in stdout

    # Being paranoid, he decides to double-check the certificate, just
    # to be on the safe side. He uses the OpenSSL CLI for this
    # purpose.
    stdout, stderr, exit_code = run_command('openssl', 'x509', '-noout', '-text', '-in', '.gimmecert/server/myserver1.cert.pem')

    # He notices that certificate includes the intended naming. He can
    # finally move ahead with his project.
    assert "DNS:myserver1," in stdout
    assert "DNS:myservice.example.com\n" in stdout
