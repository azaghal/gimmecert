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
import sys

import gimmecert.crypto
import gimmecert.storage
import gimmecert.utils


class ExitCode:
    """
    Convenience class for storing exit codes in central location.
    """

    SUCCESS = 0
    ERROR_ARGUMENTS = 2
    ERROR_ALREADY_INITIALISED = 10
    ERROR_NOT_INITIALISED = 11
    ERROR_CERTIFICATE_ALREADY_ISSUED = 12
    ERROR_UNKNOWN_ENTITY = 13


class InvalidCommandInvocation(Exception):
    """
    Exception thrown if command is invoked with invalid arguments.
    """
    pass


def init(stdout, stderr, project_directory, ca_base_name, ca_hierarchy_depth, key_specification):
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

    :param key_specification: Key specification to use when generating private keys for the hierarchy.
    :type key_specification: tuple(str, int)

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
    key_generator = gimmecert.crypto.KeyGenerator(key_specification[0], key_specification[1])
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy(ca_base_name, ca_hierarchy_depth, key_generator)

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

    print("CA hierarchy initialised using %s keys. Generated artefacts:" % str(key_generator), file=stdout)
    for level in range(1, ca_hierarchy_depth+1):
        print("    CA Level %d private key: .gimmecert/ca/level%d.key.pem" % (level, level), file=stdout)
        print("    CA Level %d certificate: .gimmecert/ca/level%d.cert.pem" % (level, level), file=stdout)

    print("    Full certificate chain: .gimmecert/ca/chain-full.cert.pem", file=stdout)

    return ExitCode.SUCCESS


def server(stdout, stderr, project_directory, entity_name, extra_dns_names, custom_csr_path, key_specification):
    """
    Issues a server certificate using the CA hierarchy initialised
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

    :param entity_name: Name of the server entity. Name will be used in subject DN and DNS subject alternative name.
    :type entity_name: str

    :param extra_dns_names: List of additional DNS names to include in the subject alternative name.
    :type extra_dns_names: list[str]

    :param custom_csr_path: Path to custom certificate signing request to use for issuing server certificate. Set to None or "" to generate private key.
                            Always overrides passed-in key specification.
    :type custom_csr_path: str or None

    :param key_specification: Key specification to use when generating private keys for the server. Ignored if custom_csr_path is specified. Set to None to
                              default to issuing CA hiearchy algorithm and parameters.
    :type key_specification: tuple(str, int) or None

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    # Set-up some paths for outputting artefacts.
    private_key_path = os.path.join(project_directory, '.gimmecert', 'server', '%s.key.pem' % entity_name)
    certificate_path = os.path.join(project_directory, '.gimmecert', 'server', '%s.cert.pem' % entity_name)
    csr_path = os.path.join(project_directory, '.gimmecert', 'server', '%s.csr.pem' % entity_name)

    # Ensure hierarchy is initialised.
    if not gimmecert.storage.is_initialised(project_directory):
        print("CA hierarchy must be initialised prior to issuing server certificates. Run the gimmecert init command first.", file=stderr)
        return ExitCode.ERROR_NOT_INITIALISED

    # Ensure artefacts do not exist already.
    if os.path.exists(private_key_path) or os.path.exists(certificate_path) or os.path.exists(csr_path):
        print("Refusing to overwrite existing data. Certificate has already been issued for server %s." % entity_name, file=stderr)
        return ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED

    # Grab the issuing CA private key and certificate.
    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(os.path.join(project_directory, '.gimmecert', 'ca'))
    issuer_private_key, issuer_certificate = ca_hierarchy[-1]

    # Grab the private key or CSR, and extract public key.
    if custom_csr_path == "-":
        csr_pem = gimmecert.utils.read_input(sys.stdin, stderr, "Please enter the CSR")
        csr = gimmecert.utils.csr_from_pem(csr_pem)
        public_key = csr.public_key()
        private_key = None
    elif custom_csr_path:
        csr = gimmecert.storage.read_csr(custom_csr_path)
        public_key = csr.public_key()
        private_key = None
    else:
        if not key_specification:
            key_specification = gimmecert.crypto.key_specification_from_public_key(issuer_private_key.public_key())
        key_generator = gimmecert.crypto.KeyGenerator(key_specification[0], key_specification[1])
        private_key = key_generator()
        public_key = private_key.public_key()
        csr = None

    # Issue the certificate.
    certificate = gimmecert.crypto.issue_server_certificate(entity_name, public_key, issuer_private_key, issuer_certificate, extra_dns_names)

    # Output CSR or private key depending on what has been passed-in.
    if csr:
        gimmecert.storage.write_csr(csr, csr_path)
    else:
        gimmecert.storage.write_private_key(private_key, private_key_path)

    gimmecert.storage.write_certificate(certificate, certificate_path)

    # Show user information about generated artefacts.
    print("Server certificate issued.", file=stdout)

    if csr:
        print("Server CSR: .gimmecert/server/%s.csr.pem" % entity_name, file=stdout)
    else:
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


def client(stdout, stderr, project_directory, entity_name, custom_csr_path, key_specification):
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
                            Always overrides passed-in key specification.
    :type custom_csr_path: str or None

    :param key_specification: Key specification to use when generating private keys for the client. Ignored if custom_csr_path is specified. Set to None to
                              default to issuing CA hiearchy algorithm and parameters.
    :type key_specification: tuple(str, int) or None

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
    if custom_csr_path == "-":
        csr_pem = gimmecert.utils.read_input(sys.stdin, stderr, "Please enter the CSR")
        csr = gimmecert.utils.csr_from_pem(csr_pem)
        public_key = csr.public_key()
    elif custom_csr_path:
        csr = gimmecert.storage.read_csr(custom_csr_path)
        public_key = csr.public_key()
    else:
        if not key_specification:
            key_specification = gimmecert.crypto.key_specification_from_public_key(issuer_private_key.public_key())
        key_generator = gimmecert.crypto.KeyGenerator(key_specification[0], key_specification[1])
        private_key = key_generator()
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


def renew(stdout, stderr, project_directory, entity_type, entity_name, generate_new_private_key, custom_csr_path, dns_names, key_specification):
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

    :param generate_new_private_key: Specify if a new private key should be generated. Cannot be used together with custom_csr_path.
    :type generate_new_private_key: bool

    :param custom_csr_path: Path to custom CSR for issuing client certificate. Cannot be used together with generate_new_private_key.
    :type custom_csr_path: str or None

    :param dns_names: List of additional DNS names to use as replacement when renewing a server certificate. To remove additional DNS names,
        set the value to empty list. To keep the existing DNS names, set the value to None. Valid only for server certificates.
    :type dns_names: list[str] or None

    :param key_specification: Key specification to use when generating new private key. Ignored if custom_csr_path is specified. Set to None to
                              default to same algorithm and parameters currently used for the entity.
    :type key_specification: tuple(str, int) or None

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    # Ensure we are not called with conflicting request.
    if generate_new_private_key and custom_csr_path:
        raise InvalidCommandInvocation("Only one of the following two parameters should be specified: generate_new_private_key, custom_csr_path.")

    if dns_names is not None and entity_type != "server":
        raise InvalidCommandInvocation("Updating DNS subject alternative names can be done only for server certificates.")

    # Set-up paths to possible artefacts.
    private_key_path = os.path.join(project_directory, '.gimmecert', entity_type, '%s.key.pem' % entity_name)
    csr_path = os.path.join(project_directory, '.gimmecert', entity_type, '%s.csr.pem' % entity_name)
    certificate_path = os.path.join(project_directory, '.gimmecert', entity_type, '%s.cert.pem' % entity_name)

    # Ensure the hierarchy has been previously initialised.
    if not gimmecert.storage.is_initialised(project_directory):
        print("No CA hierarchy has been initialised yet. Run the gimmecert init command and issue some certificates first.", file=stderr)

        return ExitCode.ERROR_NOT_INITIALISED

    # Ensure certificate has already been issued.
    if not os.path.exists(certificate_path):
        print("Cannot renew certificate. No existing certificate found for %s %s." % (entity_type, entity_name), file=stderr)

        return ExitCode.ERROR_UNKNOWN_ENTITY

    # Grab the signing CA private key and certificate.
    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(os.path.join(project_directory, '.gimmecert', 'ca'))
    issuer_private_key, issuer_certificate = ca_hierarchy[-1]

    # Information will be extracted from the old certificate.
    old_certificate = gimmecert.storage.read_certificate(certificate_path)

    # Generate new private key and use its public key for new
    # certificate. Otherwise just reuse existing public key in
    # certificate.
    if generate_new_private_key:

        # Use key specification identical to the old key.
        if not key_specification:
            key_specification = gimmecert.crypto.key_specification_from_public_key(old_certificate.public_key())

        key_generator = gimmecert.crypto.KeyGenerator(key_specification[0], key_specification[1])
        private_key = key_generator()
        gimmecert.storage.write_private_key(private_key, private_key_path)
        public_key = private_key.public_key()
    elif custom_csr_path == '-':
        csr_pem = gimmecert.utils.read_input(sys.stdin, stderr, "Please enter the CSR")
        csr = gimmecert.utils.csr_from_pem(csr_pem)
        gimmecert.storage.write_csr(csr, csr_path)
        public_key = csr.public_key()
    elif custom_csr_path:
        csr = gimmecert.storage.read_csr(custom_csr_path)
        gimmecert.storage.write_csr(csr, csr_path)
        public_key = csr.public_key()
    else:
        public_key = old_certificate.public_key()

    # Issue and write out the new certificate.
    if entity_type == 'server' and dns_names is not None:
        certificate = gimmecert.crypto.issue_server_certificate(entity_name, public_key, issuer_private_key, issuer_certificate, dns_names)
    else:
        certificate = gimmecert.crypto.renew_certificate(old_certificate, public_key, issuer_private_key, issuer_certificate)
    gimmecert.storage.write_certificate(certificate, certificate_path)

    # Replace private key with CSR.
    if custom_csr_path and os.path.exists(private_key_path):
        os.remove(private_key_path)
        private_key_replaced_with_csr = True
    else:
        private_key_replaced_with_csr = False

    # Replace CSR with private key.
    if generate_new_private_key and os.path.exists(csr_path):
        os.remove(csr_path)
        csr_replaced_with_private_key = True
    else:
        csr_replaced_with_private_key = False

    # Type of artefacts reported depending on whether the private key
    # or CSR are present.
    if generate_new_private_key:
        print("Generated new private key and renewed certificate for %s %s." % (entity_type, entity_name), file=stdout)
    else:
        print("Renewed certificate for %s %s.\n" % (entity_type, entity_name), file=stdout)

    if dns_names is not None:
        print("DNS subject alternative names have been updated.", file=stdout)

    if private_key_replaced_with_csr:
        print("Private key used for issuance of previous certificate has been removed, and replaced with the passed-in CSR.", file=stdout)

    if csr_replaced_with_private_key:
        print("CSR used for issuance of previous certificate has been removed, and a private key has been generated in its place.", file=stdout)

    # Output information about private key or CSR path.
    if os.path.exists(csr_path):
        print("{entity_type_titled} CSR: .gimmecert/{entity_type}/{entity_name}.csr.pem"
              .format(entity_type_titled=entity_type.title(),
                      entity_type=entity_type,
                      entity_name=entity_name),
              file=stdout)
    elif os.path.exists(private_key_path):
        print("{entity_type_titled} private key: .gimmecert/{entity_type}/{entity_name}.key.pem"
              .format(entity_type_titled=entity_type.title(),
                      entity_type=entity_type,
                      entity_name=entity_name),
              file=stdout)

    # Output information about generate certificate.
    print("{entity_type_titled} certificate: .gimmecert/{entity_type}/{entity_name}.cert.pem".
          format(entity_type_titled=entity_type.title(),
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

    # Derive key specification from the issuing CA certificate.
    key_specification = gimmecert.crypto.key_specification_from_public_key(ca_hierarchy[-1][1].public_key())
    key_algorithm = gimmecert.crypto.KeyGenerator(key_specification[0], key_specification[1])
    print("", file=stdout)  # Separator
    print("Default key algorithm: %s" % key_algorithm, file=stdout)

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
            private_key_path = os.path.join(project_directory, '.gimmecert', 'server', certificate_file.replace('.cert.pem', '.key.pem'))
            csr_path = os.path.join(project_directory, '.gimmecert', 'server', certificate_file.replace('.cert.pem', '.csr.pem'))
            key_algorithm = str(gimmecert.crypto.KeyGenerator(*gimmecert.crypto.key_specification_from_public_key(certificate.public_key())))

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

            print("    Key algorithm: %s" % key_algorithm, file=stdout)
            if os.path.exists(private_key_path):
                print("    Private key: .gimmecert/server/%s" % certificate_file.replace('.cert.pem', '.key.pem'), file=stdout)
            elif os.path.exists(csr_path):
                print("    CSR: .gimmecert/server/%s" % certificate_file.replace('.cert.pem', '.csr.pem'), file=stdout)

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
            private_key_path = os.path.join(project_directory, '.gimmecert', 'client', certificate_file.replace('.cert.pem', '.key.pem'))
            csr_path = os.path.join(project_directory, '.gimmecert', 'client', certificate_file.replace('.cert.pem', '.csr.pem'))
            key_algorithm = str(gimmecert.crypto.KeyGenerator(*gimmecert.crypto.key_specification_from_public_key(certificate.public_key())))

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

            print("    Key algorithm: %s" % key_algorithm, file=stdout)
            if os.path.exists(private_key_path):
                print("    Private key: .gimmecert/client/%s" % certificate_file.replace('.cert.pem', '.key.pem'), file=stdout)
            elif os.path.exists(csr_path):
                print("    CSR: .gimmecert/client/%s" % certificate_file.replace('.cert.pem', '.csr.pem'), file=stdout)

            print("    Certificate: .gimmecert/client/%s" % certificate_file, file=stdout)
    else:
        # Separator.
        print("", file=stdout)
        print("No client certificates have been issued.", file=stdout)

    # Separator. Helps separate terminal prompt from final line of output.
    print("", file=stdout)

    return ExitCode.SUCCESS
