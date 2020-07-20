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


import argparse
import os
import sys

from cryptography.hazmat.primitives.asymmetric import ec

from .decorators import subcommand_parser, get_subcommand_parser_setup_functions
from .commands import client, help_, init, renew, server, status, usage, ExitCode


ERROR_ARGUMENTS = 2
ERROR_GENERIC = 10


DESCRIPTION = """\
Issues server and client X.509 certificates using a local CA hierarchy.

Examples:

    # Set-up and switch to directory - you can switch to existing directory too.
    mkdir myproject/
    cd myproject/

    # Initialise the local CA hierarchy and all the necessary directories.
    gimmecert init

    # Initialise the local CA hierarchy while generating secp256r1 ECDSA keys.
    gimmecert init --key-specification ecdsa:secp256r1

    # Issue a TLS server certificate with only the server name in DNS subject alternative name.
    gimmecert server myserver

    # Issue a TLS server certificate with additional DNS subject alternative names.
    gimmecert server myserver extradns1.local extradns2.example.com

    # Issue a TLS server certificate by using public key from the CSR (naming/extensions are ignored).
    gimmecert server myserver --csr /tmp/myserver.csr.pem

    # Issue a TLS server certificate while generating 3072-bit RSA key.
    gimmecert server myserver --key-specification rsa:3072

    # Issue a TLS client certificate.
    gimmecert client myclient

    # Issue a TLS client certificate by using public key from the CSR (naming/extensions are ignored).
    gimmecert client myclient --csr /tmp/myclient.csr.pem

    # Issue a TLS client certificate while generating 1024-bit RSA key.
    gimmecert client myclient --key-specification rsa:1024

    # Renew a TLS server certificate, preserving naming and private key.
    gimmecert renew server myserver

    # Renew a TLS server certificate, generating a new private key using specified key algorithm/parameters.
    gimmecert renew server myserver --new-private-key --key-specification ecdsa:secp224r1

    # Renew a TLS server certificate, replacing the extra DNS names, but keeping the private key.
    gimmecert server myserver wrongdns.local
    gimmecert renew server myserver --update-dns-names "correctdns1.local,correctdns2.local"

    # Renew a TLS server certificate, removing extra DNS subject alternative names, but keeping the private key.
    gimmecert server myserver dontneedthisname.local
    gimmecert renew server myserver --update-dns-names ""

    # Renew a TLS client certificate, preserving naming and private key.
    gimmecert renew client myclient

    # Renew a TLS client certificate, generating a new private key using specified key algorithm/parameters.
    gimmecert renew client myclient --new-private-key --key-specification ecdsa:secp521r1

    # Show information about CA hierarchy and issued certificates.
    gimmecert status
"""


class ArgumentHelp:
    """
    Convenience class for storing help strings for common arguments.
    """

    key_specification_format = '''Specification/parameters to use for private key generation. \
                                  For RSA keys, use format rsa:BIT_LENGTH. For ECDSA keys, use format ecdsa:CURVE_NAME. \
                                  Supported curves: secp192r1, secp224r1, secp256k1, secp256r1, secp384r1, secp521r1.'''


def key_specification(specification):
    """
    Verifies and parses the passed-in key specification. This is a
    small utility function for use with the Python argument parser.

    :param specification: Key specification. Currently supported formats are: "rsa:KEY_SIZE" and "ecdsa:CURVE_NAME".
    :type specification: str

    :returns: Parsed key algorithm and parameter(s) for the algorithm. For RSA, parameter is the RSA key size.
    :rtype: tuple(str, int or cryptography.hazmat.primitives.asymmetric.ec.EllipticCurve)

    :raises ValueError: If passed-in specification is invalid.
    """

    available_curves = {
        "secp192r1": ec.SECP192R1,
        "secp224r1": ec.SECP224R1,
        "secp256k1": ec.SECP256K1,
        "secp256r1": ec.SECP256R1,
        "secp384r1": ec.SECP384R1,
        "secp521r1": ec.SECP521R1,
    }

    try:
        algorithm, parameters = specification.split(":", 2)
        algorithm = algorithm.lower()

        if algorithm == "rsa":
            parameters = int(parameters)
        elif algorithm == "ecdsa":
            parameters = str(parameters).lower()
            parameters = available_curves[parameters]
        else:
            raise ValueError()

    except (ValueError, KeyError):
        raise ValueError("Invalid key specification: '%s'" % specification)

    return algorithm, parameters


@subcommand_parser
def setup_init_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('init', description='Initialise CA hierarchy.')
    subparser.add_argument('--ca-base-name', '-b', help="Base name to use for CA naming. Default is to use the working directory base name.")
    subparser.add_argument('--ca-hierarchy-depth', '-d', type=int, help="Depth of CA hierarchy to generate. Default is 1", default=1)
    subparser.add_argument('--key-specification', '-k', type=key_specification,
                           help=ArgumentHelp.key_specification_format + " Default is rsa:2048.", default="rsa:2048")

    def init_wrapper(args):
        project_directory = os.getcwd()
        if args.ca_base_name is None:
            args.ca_base_name = os.path.basename(project_directory)

        return init(sys.stdout, sys.stderr, project_directory, args.ca_base_name, args.ca_hierarchy_depth, args.key_specification)

    subparser.set_defaults(func=init_wrapper)

    return subparser


@subcommand_parser
def setup_help_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('help', description='shows help')

    def help_wrapper(args):
        return help_(sys.stdout, sys.stderr, parser)

    subparser.set_defaults(func=help_wrapper)

    return subparser


@subcommand_parser
def setup_server_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('server', description='Issues server certificate.')
    subparser.add_argument('entity_name', help='Name of the server entity.')
    subparser.add_argument('dns_name', nargs='*', help='Additional DNS names to include in subject alternative name.')
    key_specification_or_csr_group = subparser.add_mutually_exclusive_group()
    key_specification_or_csr_group.add_argument('--csr', '-c', type=str, default=None,
                                                help='''Do not generate server private key locally, and use the passed-in \
    certificate signing request (CSR) instead. Use dash (-) to read from standard input. Only the public key is taken from the CSR.''')
    key_specification_or_csr_group.add_argument('--key-specification', '-k', type=key_specification, default=None,
                                                help=ArgumentHelp.key_specification_format +
                                                " Default is to use same algorithm/parameters as used by CA hierarchy.")

    def server_wrapper(args):
        project_directory = os.getcwd()

        return server(sys.stdout, sys.stderr, project_directory, args.entity_name, args.dns_name, args.csr, args.key_specification)

    subparser.set_defaults(func=server_wrapper)

    return subparser


@subcommand_parser
def setup_client_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('client', description='Issue client certificate.')
    subparser.add_argument('entity_name', help='Name of the client entity.')
    key_specification_or_csr_group = subparser.add_mutually_exclusive_group()
    key_specification_or_csr_group.add_argument('--csr', '-c', type=str, default=None,
                                                help='''Do not generate client private key locally, and use the passed-in \
    certificate signing request (CSR) instead. Use dash (-) to read from standard input. Only the public key is taken from the CSR.''')
    key_specification_or_csr_group.add_argument('--key-specification', '-k', type=key_specification, default=None,
                                                help=ArgumentHelp.key_specification_format +
                                                " Default is to use same algorithm/parameters as used by CA hierarchy.")

    def client_wrapper(args):
        project_directory = os.getcwd()

        return client(sys.stdout, sys.stderr, project_directory, args.entity_name, args.csr, args.key_specification)

    subparser.set_defaults(func=client_wrapper)

    return subparser


@subcommand_parser
def setup_renew_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('renew', description='Renews existing certificates.')
    subparser.add_argument('entity_type', help='Type of entity to renew.', choices=['server', 'client'])
    subparser.add_argument('entity_name', help='Name of the entity')

    def csv_list(csv):
        """
        Small helper that converts CSV string into a list.
        """

        if csv:
            return csv.split(",")

        return []

    subparser.add_argument('--update-dns-names', '-u', dest="dns_names", default=None, type=csv_list,
                           help='''Replace the DNS subject alternative names with new values. \
    Valid only for server certificate renewals. Multiple DNS names can be passed-in as comma-separated list. \
    Passing-in an empty string will result in all additional DNS subject alternative names being removed. \
    The entity name is kept as DNS subject alternative name in either case.''')

    new_private_key_or_csr_group = subparser.add_mutually_exclusive_group()

    new_private_key_or_csr_group.add_argument('--new-private-key', '-p', action='store_true', help='''Generate new private key for renewal. \
    Default is to keep the existing key. Mutually exclusive with the --csr option.''')
    new_private_key_or_csr_group.add_argument('--csr', '-c', type=str, default=None, help='''Do not use local private key and public key information from \
    existing certificate, and use the passed-in certificate signing request (CSR) instead. Use dash (-) to read from standard input. \
    If private key exists, it will be removed. Mutually exclusive with the --new-private-key option. Only the public key is taken from the CSR.''')

    subparser.add_argument('--key-specification', '-k', type=key_specification,
                           help=ArgumentHelp.key_specification_format + " Default is to use same specification as used for current certificate.", default=None)

    def renew_wrapper(args):
        # This is a workaround for having the key specification option
        # be dependant on new private key option, since argparse
        # cannot provide such verification on its own.
        if args.key_specification and not args.new_private_key:
            subparser.error("argument --key-specification/-k: must be used with --new-private-key/-p")

        project_directory = os.getcwd()

        return renew(sys.stdout, sys.stderr, project_directory, args.entity_type, args.entity_name, args.new_private_key, args.csr, args.dns_names,
                     args.key_specification)

    subparser.set_defaults(func=renew_wrapper)

    return subparser


@subcommand_parser
def setup_status_subcommand_parser(parser, subparsers):

    subparser = subparsers.add_parser(name="status", description="Shows status information about issued certificates.")

    def status_wrapper(args):
        project_directory = os.getcwd()

        status(sys.stdout, sys.stderr, project_directory)

        return ExitCode.SUCCESS

    subparser.set_defaults(func=status_wrapper)

    return subparser


def get_parser():
    """
    Sets-up and returns a CLI argument parser.

    :returns: argparse.ArgumentParser -- argument parser for CLI.
    """

    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)

    def usage_wrapper(args):
        return usage(sys.stdout, sys.stderr, parser)

    parser.set_defaults(func=usage_wrapper)

    subparsers = parser.add_subparsers()

    for setup_subcommad_parser in get_subcommand_parser_setup_functions():
        setup_subcommad_parser(parser, subparsers)

    return parser


def main():
    """
    This function is a CLI entry point for the tool. It is a thin
    wrapper around the argument parser, and underlying command
    implementation.

    In order for this to work, the parser needs to register the
    callback function as a default parameter for attribute
    'func'. This attribute is then invoked by the main function,
    passing-in all the parsed arguments while at it.
    """

    parser = get_parser()
    args = parser.parse_args()

    status_code = args.func(args)

    if status_code != ExitCode.SUCCESS:
        exit(status_code)
