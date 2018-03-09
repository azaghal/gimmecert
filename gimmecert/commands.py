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

import gimmecert.crypto
import gimmecert.storage


class ExitCode:
    """
    Convenience class for storing exit codes in central location.
    """

    SUCCESS = 0
    ERROR_ALREADY_INITIALISED = 10
    ERROR_NOT_INITIALISED = 11
    ERROR_CERTIFICATE_ALREADY_ISSUED = 12


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


def server(stdout, stderr, project_directory, entity_name, extra_dns_names):
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

    :returns: Status code, one from gimmecert.commands.ExitCode.
    :rtype: int
    """

    private_key_path = os.path.join('.gimmecert', 'server', '%s.key.pem' % entity_name)
    certificate_path = os.path.join('.gimmecert', 'server', '%s.cert.pem' % entity_name)

    if not gimmecert.storage.is_initialised(project_directory):
        print("CA hierarchy must be initialised prior to issuing server certificates. Run the gimmecert init command first.", file=stderr)
        return ExitCode.ERROR_NOT_INITIALISED

    if os.path.exists(private_key_path) or os.path.exists(certificate_path):
        print("Refusing to overwrite existing data. Certificate has already been issued for server myserver.", file=stderr)
        return ExitCode.ERROR_CERTIFICATE_ALREADY_ISSUED

    print("""Server certificate issued.\n
    Server private key: .gimmecert/server/%s.key.pem
    Server certificate: .gimmecert/server/%s.cert.pem""" % (entity_name, entity_name), file=stdout)

    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(os.path.join(project_directory, '.gimmecert', 'ca'))
    issuer_private_key, issuer_certificate = ca_hierarchy[-1]
    private_key = gimmecert.crypto.generate_private_key()
    certificate = gimmecert.crypto.issue_server_certificate(entity_name, private_key.public_key(), issuer_private_key, issuer_certificate, extra_dns_names)

    gimmecert.storage.write_private_key(private_key, private_key_path)
    gimmecert.storage.write_certificate(certificate, certificate_path)

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
