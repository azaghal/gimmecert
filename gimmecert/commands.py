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

import os
import datetime

import gimmecert.crypto
import gimmecert.storage
import gimmecert.utils


class ExitCode:
    """
    Convenience class for storing exit codes in central location.
    """

    SUCCESS = 0
    ERROR_ALREADY_INITIALISED = 10
    ERROR_NOT_INITIALISED = 11
    ERROR_CERTIFICATE_ALREADY_ISSUED = 12
    ERROR_UNKNOWN_ENTITY = 13


def init(stdout, stderr, project_directory, ca_base_name, ca_hierarchy_depth):
    """
    Initialises the necessary directory and CA hierarchies for use in
    the specified directory.

    :param stdout: Output stream where the informative messages should be written-out.
    :type stdout: io.IOBase

    :param stderr: Output stream where the error messages should be written-out.
    :type stderr: io.IOBase

    :param project_directory: Path to directory where the structure should be initialised. Should be top-level project directory normally.
    :type project_directory: str

    :param ca_base_name: Base name to use for constructing CA subject DNs.
    :type ca_base_name: str

    :param ca_hierarchy_depth: Length/depths of CA hierarchy that should be initialised. E.g. total number of CAs in chain.
    :type ca_hierarchy_depth: int

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    # Set-up various paths.
    base_directory = os.path.join(project_directory, '.gimmecert')
    ca_directory = os.path.join(base_directory, 'ca')

    if os.path.exists(base_directory):
        print("CA hierarchy has already been initialised.", file=stderr)
        return ExitCode.ERROR_ALREADY_INITIALISED

    # Initialise the directory.
    gimmecert.storage.initialise_storage(project_directory)

    # Generate the CA hierarchy.
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy(ca_base_name, ca_hierarchy_depth)

    # Output the CA private keys and certificates.
    for level, (private_key, certificate) in enumerate(ca_hierarchy, 1):
        private_key_path = os.path.join(ca_directory, 'level%d.key.pem' % level)
        certificate_path = os.path.join(ca_directory, 'level%d.cert.pem' % level)
        gimmecert.storage.write_private_key(private_key, private_key_path)
        gimmecert.storage.write_certificate(certificate, certificate_path)

    # Output the certificate chain.
    full_chain = [certificate for _, certificate in ca_hierarchy]
    full_chain_path = os.path.join(ca_directory, 'chain-full.cert.pem')
    gimmecert.storage.write_certificate_chain(full_chain, full_chain_path)

    print("CA hierarchy initialised. Generated artefacts:", file=stdout)
    for level in range(1, ca_hierarchy_depth+1):
        print("    CA Level %d private key: .gimmecert/ca/level%d.key.pem" % (level, level), file=stdout)
        print("    CA Level %d certificate: .gimmecert/ca/level%d.cert.pem" % (level, level), file=stdout)

    print("    Full certificate chain: .gimmecert/ca/chain-full.cert.pem", file=stdout)

    return ExitCode.SUCCESS


def server(stdout, stderr, project_directory, entity_name, extra_dns_names, update_dns_names):
    """
    Generates a server private key and issues a server certificate
    using the CA hierarchy initialised within the specified directory.

    :param stdout: Output stream where the informative messages should be written-out.
    :type stdout: io.IOBase

    :param stderr: Output stream where the error messages should be written-out.
    :type stderr: io.IOBase

    :param project_directory: Path to project directory under which the CA artifacats etc will be looked-up.
    :type project_directory: str

    :param entity_name: Name of the server entity. Name will be used in subject DN and DNS subject alternative name.
    :type entity_name: str

    :param extra_dns_names: List of additional DNS names to include in the subject alternative name.
    :type extra_dns_names: list[str]

    :param update_dns_names: Whether the certificate should be renewed using the existing private key, but with new DNS subject alternative names.
    :type update: bool

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    # Set-up some paths for outputting artefacts.
    private_key_path = os.path.join(project_directory, '.gimmecert', 'server', '%s.key.pem' % entity_name)
    certificate_path = os.path.join(project_directory, '.gimmecert', 'server', '%s.cert.pem' % entity_name)

    # Ensure hierarchy is initialised.
    if not gimmecert.storage.is_initialised(project_directory):
        print("CA hierarchy must be initialised prior to issuing server certificates. Run the gimmecert init command first.", file=stderr)
        return ExitCode.ERROR_NOT_INITIALISED

    # Ensure artefacts do not exist already, unless update of DNS
    # names has been requested.
    if not update_dns_names and (
            os.path.exists(private_key_path) or
            os.path.exists(certificate_path)
    ):
        print("Refusing to overwrite existing data. Certificate has already been issued for server %s." % entity_name, file=stderr)
        return ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED

    # Read or generate the private key.
    if update_dns_names and os.path.exists(private_key_path):
        renew_certificate = True
        private_key = gimmecert.storage.read_private_key(private_key_path)
    else:
        renew_certificate = False
        private_key = gimmecert.crypto.generate_private_key()

    # Extract the public key.
    public_key = private_key.public_key()

    # Grab the issuing CA private key and certificate.
    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(os.path.join(project_directory, '.gimmecert', 'ca'))
    issuer_private_key, issuer_certificate = ca_hierarchy[-1]

    # Issue the certificate.
    certificate = gimmecert.crypto.issue_server_certificate(entity_name, public_key, issuer_private_key, issuer_certificate, extra_dns_names)

    gimmecert.storage.write_private_key(private_key, private_key_path)
    gimmecert.storage.write_certificate(certificate, certificate_path)

    # Show user information about generated artefacts.
    if renew_certificate:
        print("Server certificate renewed with new DNS subject alternative names.", file=stdout)
        print("Server private key has remained unchanged.", file=stdout)
    else:
        print("Server certificate issued.", file=stdout)

    print("Server private key: .gimmecert/server/%s.key.pem" % entity_name, file=stdout)
    print("Server certificate: .gimmecert/server/%s.cert.pem" % entity_name, file=stdout)

    return ExitCode.SUCCESS


def help_(stdout, stderr, parser):
    """
    Output help for the user.

    :param stdout: Output stream where the informative messages should be written-out.
    :type stdout: io.IOBase

    :param stderr: Output stream where the error messages should be written-out.
    :type stderr: io.IOBase

    :param parser: Parser used for processing the CLI positional and optional arguments.
    :type parser: argparse.ArgumentParser

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    parser.print_help(stdout)

    return ExitCode.SUCCESS


def usage(stdout, stderr, parser):
    """
    Output usage for the user.

    :param stdout: Output stream where the informative messages should be written-out.
    :type stdout: io.IOBase

    :param stderr: Output stream where the error messages should be written-out.
    :type stderr: io.IOBase

    :param parser: Parser used for processing the CLI positional and optional arguments.
    :type parser: argparse.ArgumentParser

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    parser.print_usage(stdout)

    return ExitCode.SUCCESS


def client(stdout, stderr, project_directory, entity_name, custom_csr_path):
    """
    Issues a client certificate using the CA hierarchy initialised
    within the specified directory.

    If custom CSR path is not passed-in, a private key will be
    generated and stored.

    If custom CSR is passed-in, no private key will be generated, and
    the CSR will be stored instead. Only the public key will be used
    from the CSR - no naming information is taken from it.

    :param stdout: Output stream where the informative messages should be written-out.
    :type stdout: io.IOBase

    :param stderr: Output stream where the error messages should be written-out.
    :type stderr: io.IOBase

    :param project_directory: Path to project directory under which the CA artifacats etc will be looked-up.
    :type project_directory: str

    :param entity_name: Name of the client entity. Name will be used in subject DN.
    :type entity_name: str

    :param custom_csr_path: Path to custom certificate signing request to use for issuing client certificate. Set to None or "" to generate private key.
    :type custom_csr_path: str or None

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    # Set-up paths where we will output artefacts.
    private_key_path = os.path.join(project_directory, '.gimmecert', 'client', '%s.key.pem' % entity_name)
    certificate_path = os.path.join(project_directory, '.gimmecert', 'client', '%s.cert.pem' % entity_name)
    csr_path = os.path.join(project_directory, '.gimmecert', 'client', '%s.csr.pem' % entity_name)

    # Ensure hierarchy is initialised.
    if not gimmecert.storage.is_initialised(project_directory):
        print("CA hierarchy must be initialised prior to issuing client certificates. Run the gimmecert init command first.", file=stderr)
        return ExitCode.ERROR_NOT_INITIALISED

    # Ensure artefacts do not exist already.
    if os.path.exists(private_key_path) or os.path.exists(certificate_path) or os.path.exists(csr_path):
        print("Refusing to overwrite existing data. Certificate has already been issued for client %s." % entity_name, file=stderr)
        return ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED

    # Grab the issuing CA private key and certificate.
    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(os.path.join(project_directory, '.gimmecert', 'ca'))
    issuer_private_key, issuer_certificate = ca_hierarchy[-1]

    # Either read public key from CSR, or generate a new private key.
    if custom_csr_path:
        csr = gimmecert.storage.read_csr(custom_csr_path)
        public_key = csr.public_key()
    else:
        private_key = gimmecert.crypto.generate_private_key()
        public_key = private_key.public_key()

    # Issue certificate using the passed-in information and
    # appropriate public key.
    certificate = gimmecert.crypto.issue_client_certificate(entity_name, public_key, issuer_private_key, issuer_certificate)

    # Output CSR or private key depending on what was provided.
    if custom_csr_path:
        gimmecert.storage.write_csr(csr, csr_path)
    else:
        gimmecert.storage.write_private_key(private_key, private_key_path)

    gimmecert.storage.write_certificate(certificate, certificate_path)

    # Show user information about generated artefacts.
    print("Client certificate issued.", file=stdout)

    if custom_csr_path:
        print("Client CSR: .gimmecert/client/%s.csr.pem" % entity_name, file=stdout)
    else:
        print("Client private key: .gimmecert/client/%s.key.pem" % entity_name, file=stdout)

    print("Client certificate: .gimmecert/client/%s.cert.pem" % entity_name, file=stdout)

    return ExitCode.SUCCESS


def renew(stdout, stderr, project_directory, entity_type, entity_name, generate_new_private_key):
    """
    Renews existing certificate, while optionally generating a new
    private key in the process. Naming and extensions are preserved.

    :param stdout: Output stream where the informative messages should be written-out.
    :type stdout: io.IOBase

    :param stderr: Output stream where the error messages should be written-out.
    :type stderr: io.IOBase

    :param project_directory: Path to project directory under which the CA artifacats etc will be looked-up.
    :type project_directory: str

    :param entity_type: Type of entity. Currently supported values are ``server`` and ``client``.
    :type entity_type: str

    :param entity_name: Name of entity. Name should refer to entity for which a certificate has already been issued.
    :type entity_name: str

    :param generate_new_private_key: Specify if a new private key should be generated, or an existing one should be used instead.
    :type generate_new_private_key: bool

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    private_key_path = os.path.join(project_directory, '.gimmecert', entity_type, '%s.key.pem' % entity_name)
    certificate_path = os.path.join(project_directory, '.gimmecert', entity_type, '%s.cert.pem' % entity_name)

    if not gimmecert.storage.is_initialised(project_directory):
        print("No CA hierarchy has been initialised yet. Run the gimmecert init command and issue some certificates first.", file=stderr)

        return ExitCode.ERROR_NOT_INITIALISED

    if not os.path.exists(certificate_path):
        print("Cannot renew certificate. No existing certificate found for %s %s." % (entity_type, entity_name), file=stderr)

        return ExitCode.ERROR_UNKNOWN_ENTITY

    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(os.path.join(project_directory, '.gimmecert', 'ca'))
    issuer_private_key, issuer_certificate = ca_hierarchy[-1]

    old_certificate = gimmecert.storage.read_certificate(certificate_path)

    if generate_new_private_key:
        private_key = gimmecert.crypto.generate_private_key()
        gimmecert.storage.write_private_key(private_key, private_key_path)
        public_key = private_key.public_key()
    else:
        public_key = old_certificate.public_key()

    certificate = gimmecert.crypto.renew_certificate(old_certificate, public_key, issuer_private_key, issuer_certificate)

    gimmecert.storage.write_certificate(certificate, certificate_path)

    if generate_new_private_key:
        print("Generated new private key and renewed certificate for %s %s." % (entity_type, entity_name), file=stdout)
    else:
        print("Renewed certificate for %s %s.\n" % (entity_type, entity_name), file=stdout)

    print("""{entity_type_titled} private key: .gimmecert/{entity_type}/{entity_name}.key.pem\n
    {entity_type_titled} certificate: .gimmecert/{entity_type}/{entity_name}.cert.pem""".format(entity_type_titled=entity_type.title(),
                                                                                                entity_type=entity_type,
                                                                                                entity_name=entity_name),
          file=stdout)

    return ExitCode.SUCCESS


def status(stdout, stderr, project_directory):
    """
    Displays information about initialised hierarchy and issued
    certificates in project directory.

    :param stdout: Output stream where the informative messages should be written-out.
    :type stdout: io.IOBase

    :param stderr: Output stream where the error messages should be written-out.
    :type stderr: io.IOBase

    :param project_directory: Path to project directory under which the artefacts are looked-up.
    :type project_directory: str

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    now = datetime.datetime.now()

    if not gimmecert.storage.is_initialised(project_directory):
        print("CA hierarchy has not been initialised in current directory.", file=stdout)
        return ExitCode.ERROR_NOT_INITIALISED

    def get_section_title(title):
        """
        Small helper function that produces section title surrounded by
        separators for better visibility.
        """

        return "%s\n%s\n%s" % ("-" * len(title), title, "-" * len(title))

    print(get_section_title("CA hierarchy"), file=stdout)

    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(os.path.join(project_directory, '.gimmecert', 'ca'))

    for i, (_, certificate) in enumerate(ca_hierarchy, 1):
        # Separator.
        print("", file=stdout)

        if i == len(ca_hierarchy):
            print(gimmecert.utils.dn_to_str(certificate.subject) + " [END ENTITY ISSUING CA]", file=stdout)
        else:
            print(gimmecert.utils.dn_to_str(certificate.subject), file=stdout)

        if certificate.not_valid_before > now:
            validity_status = " [NOT VALID YET]"
        elif certificate.not_valid_after < now:
            validity_status = " [EXPIRED]"
        else:
            validity_status = ""

        print("    Validity: %s%s" % (gimmecert.utils.date_range_to_str(certificate.not_valid_before,
                                                                        certificate.not_valid_after),
                                      validity_status), file=stdout)
        print("    Certificate: .gimmecert/ca/level%d.cert.pem" % i, file=stdout)

    # Separator.
    print("", file=stdout)

    print("Full certificate chain: .gimmecert/ca/chain-full.cert.pem", file=stdout)

    # Section separator.
    print("\n", file=stdout)

    print(get_section_title("Server certificates"), file=stdout)

    certificate_files = sorted([c for c in os.listdir(os.path.join(project_directory, '.gimmecert', 'server')) if c.endswith('.cert.pem')])

    if certificate_files:
        for certificate_file in certificate_files:
            certificate = gimmecert.storage.read_certificate(os.path.join(project_directory, '.gimmecert', 'server', certificate_file))

            # Separator.
            print("", file=stdout)

            if certificate.not_valid_before > now:
                validity_status = " [NOT VALID YET]"
            elif certificate.not_valid_after < now:
                validity_status = " [EXPIRED]"
            else:
                validity_status = ""

            print(gimmecert.utils.dn_to_str(certificate.subject), file=stdout)
            print("    Validity: %s%s" % (gimmecert.utils.date_range_to_str(certificate.not_valid_before,
                                                                            certificate.not_valid_after),
                                          validity_status), file=stdout)
            print("    DNS: %s" % ", ".join(gimmecert.utils.get_dns_names(certificate)), file=stdout)
            print("    Private key: .gimmecert/server/%s" % certificate_file.replace('.cert.pem', '.key.pem'), file=stdout)
            print("    Certificate: .gimmecert/server/%s" % certificate_file, file=stdout)
    else:
        # Separator.
        print("", file=stdout)
        print("No server certificates have been issued.", file=stdout)

    # Section separator.
    print("\n", file=stdout)

    print(get_section_title("Client certificates"), file=stdout)

    certificate_files = sorted([c for c in os.listdir(os.path.join(project_directory, '.gimmecert', 'client')) if c.endswith('.cert.pem')])

    if certificate_files:
        for certificate_file in certificate_files:
            certificate = gimmecert.storage.read_certificate(os.path.join(project_directory, '.gimmecert', 'client', certificate_file))

            # Separator.
            print("", file=stdout)

            if certificate.not_valid_before > now:
                validity_status = " [NOT VALID YET]"
            elif certificate.not_valid_after < now:
                validity_status = " [EXPIRED]"
            else:
                validity_status = ""

            print(gimmecert.utils.dn_to_str(certificate.subject), file=stdout)
            print("    Validity: %s%s" % (gimmecert.utils.date_range_to_str(certificate.not_valid_before,
                                                                            certificate.not_valid_after),
                                          validity_status), file=stdout)
            print("    Private key: .gimmecert/client/%s" % certificate_file.replace('.cert.pem', '.key.pem'), file=stdout)
            print("    Certificate: .gimmecert/client/%s" % certificate_file, file=stdout)
    else:
        # Separator.
        print("", file=stdout)
        print("No client certificates have been issued.", file=stdout)

    # Separator. Helps separate terminal prompt from final line of output.
    print("", file=stdout)

    return ExitCode.SUCCESS
