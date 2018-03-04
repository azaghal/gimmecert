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
from .commands import init, server


ERROR_GENERIC = 10


DESCRIPTION = """\
Issues server and client X.509 certificates using a local CA hierarchy.

Examples:

    # Set-up and switch to directory - you can switch to existing directory too.
    mkdir myproject/
    cd myproject/

    # Initialise the local CA hierarchy and all the necessary directories.
    gimmecert init
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

        if init(project_directory, args.ca_base_name, args.ca_hierarchy_depth):
            print("CA hierarchy initialised. Generated artefacts:")
            for level in range(1, args.ca_hierarchy_depth+1):
                print("    CA Level %d private key: .gimmecert/ca/level%d.key.pem" % (level, level))
                print("    CA Level %d certificate: .gimmecert/ca/level%d.cert.pem" % (level, level))
            print("    Full certificate chain: .gimmecert/ca/chain-full.cert.pem")
        else:
            print("CA hierarchy has already been initialised.")

    subparser.set_defaults(func=init_wrapper)

    return subparser


@subcommand_parser
def setup_help_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('help', description='shows help')

    subparser.set_defaults(func=lambda args: parser.print_help())

    return subparser


@subcommand_parser
def setup_server_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('server', description='Issues server certificate.')
    subparser.add_argument('entity_name', help='Name of the server entity.')
    subparser.add_argument('dns_name', nargs='*', help='Additional DNS names to include in subject alternative name.')

    def server_wrapper(args):
        project_directory = os.getcwd()

        status, message = server(project_directory, args.entity_name)

        if status is False:
            print(message, file=sys.stderr)
            exit(ERROR_GENERIC)
        else:
            print(message)

    subparser.set_defaults(func=server_wrapper)

    return subparser


def get_parser():
    """
    Sets-up and returns a CLI argument parser.

    :returns: argparse.ArgumentParser -- argument parser for CLI.
    """

    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.set_defaults(func=lambda args: parser.print_usage())

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
    args.func(args)
