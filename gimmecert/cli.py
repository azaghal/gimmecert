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

from .decorators import subcommand_parser, get_subcommand_parser_setup_functions
from .commands import client, help_, init, renew, server, status, usage, ExitCode


ERROR_GENERIC = 10


DESCRIPTION = """\
Issues server and client X.509 certificates using a local CA hierarchy.

Examples:

    # Set-up and switch to directory - you can switch to existing directory too.
    mkdir myproject/
    cd myproject/

    # Initialise the local CA hierarchy and all the necessary directories.
    gimmecert init

    # Issue a TLS server certificate with only the server name in DNS subject alternative name.
    gimmecert server myserver

    # Issue a TLS server certificate with additional DNS subject alternative names.
    gimmecert server myserver extradns1.local extradns2.example.com

    # Issue a TLS client certificate.
    gimmecert client myclient

    # Renew a TLS server certificate with updated DNS subject alternative names. Keeps the private key if any.
    gimmecert server myserver wrongdns.local
    gimmecert server --update-dns-names myserver correctdns1.local correctdns2.local

    # Renew a TLS server certificate removing extra DNS subject alternative names. Keeps the private key if any.
    gimmecert server myserver dontneedthisname.local
    gimmecert server myserver --update-dns-names

    # Renew a TLS server certificate, preserving naming and private key.
    gimmecert renew server myserver

    # Renew a TLS client certificate, preserving naming and private key.
    gimmecert renew client myclient

    # Show information about CA hierarchy and issued certificates.
    gimmecert status
"""


@subcommand_parser
def setup_init_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('init', description='Initialise CA hierarchy.')
    subparser.add_argument('--ca-base-name', '-b', help="Base name to use for CA naming. Default is to use the working directory base name.")
    subparser.add_argument('--ca-hierarchy-depth', '-d', type=int, help="Depth of CA hierarchy to generate. Default is 1", default=1)

    def init_wrapper(args):
        project_directory = os.getcwd()
        if args.ca_base_name is None:
            args.ca_base_name = os.path.basename(project_directory)

        return init(sys.stdout, sys.stderr, project_directory, args.ca_base_name, args.ca_hierarchy_depth)

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
    subparser.add_argument('--update-dns-names', '-u', action='store_true', help='''Renew certificate for an existing server entity by reusing \
    the private key, but replacing the DNS subject alternative names with listed values (if any). \
    If entity does not exist, this option has no effect, and a new private key/certificate will be generated as usual.''')
    subparser.add_argument('--csr', '-c', type=str, default=None, help='''Do not generate server private key locally, and use the passed-in \
    certificate signing request (CSR) instead.''')

    def server_wrapper(args):
        project_directory = os.getcwd()

        return server(sys.stdout, sys.stderr, project_directory, args.entity_name, args.dns_name, args.update_dns_names)

    subparser.set_defaults(func=server_wrapper)

    return subparser


@subcommand_parser
def setup_client_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('client', description='Issue client certificate.')
    subparser.add_argument('entity_name', help='Name of the client entity.')
    subparser.add_argument('--csr', '-c', type=str, default=None, help='''Do not generate client private key locally, and use the passed-in \
    certificate signing request (CSR) instead.''')

    def client_wrapper(args):
        project_directory = os.getcwd()

        return client(sys.stdout, sys.stderr, project_directory, args.entity_name, args.csr)

    subparser.set_defaults(func=client_wrapper)

    return subparser


@subcommand_parser
def setup_renew_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('renew', description='Renews existing certificates.')
    subparser.add_argument('entity_type', help='Type of entity to renew.', choices=['server', 'client'])
    subparser.add_argument('entity_name', help='Name of the entity')

    new_private_key_or_csr_group = subparser.add_mutually_exclusive_group()

    new_private_key_or_csr_group.add_argument('--new-private-key', '-p', action='store_true', help='''Generate new private key for renewal. \
    Default is to keep the existing key. Mutually exclusive with the --csr option.''')
    new_private_key_or_csr_group.add_argument('--csr', '-c', type=str, help='''Do not use local private key and public key information from \
    existing certificate, and use the passed-in certificate signing request (CSR) instead. If private key exists, it will be removed. \
    Mutually exclusive with the --new-private-key option.''')

    def renew_wrapper(args):
        project_directory = os.getcwd()

        return renew(sys.stdout, sys.stderr, project_directory, args.entity_type, args.entity_name, args.new_private_key)

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
