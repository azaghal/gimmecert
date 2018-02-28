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

from .decorators import subcommand_parser, get_subcommand_parser_setup_functions
from .storage import initialise_storage, write_private_key, write_certificate
from .crypto import generate_private_key, issue_certificate, get_dn, get_validity_range


DESCRIPTION = """\
Issues server and client X.509 certificates using a local CA
hierarchy.

Examples:
"""


@subcommand_parser
def setup_init_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('init', description='Initialise CA hierarchy.')

    def init(args):
        project_directory = os.getcwd()
        base_directory = os.path.join(os.getcwd(), '.gimmecert')
        ca_directory = os.path.join(base_directory, 'ca')
        level1_private_key_path = os.path.join(ca_directory, 'level1.key.pem')
        level1_certificate_path = os.path.join(ca_directory, 'level1.cert.pem')
        full_chain_path = os.path.join(ca_directory, 'chain-full.cert.pem')
        level1_dn = get_dn("%s Level 1" % os.path.basename(project_directory))
        not_before, not_after = get_validity_range()

        initialise_storage(project_directory)
        level1_private_key = generate_private_key()
        level1_certificate = issue_certificate(level1_dn, level1_dn, level1_private_key, level1_private_key.public_key(), not_before, not_after)
        full_chain = level1_certificate

        write_private_key(level1_private_key, level1_private_key_path)
        write_certificate(level1_certificate, level1_certificate_path)
        write_certificate(full_chain, full_chain_path)

        print("CA hierarchy initialised. Generated artefacts:")
        print("    CA Level 1 private key: .gimmecert/ca/level1.key.pem")
        print("    CA Level 1 certificate: .gimmecert/ca/level1.cert.pem")
        print("    Full certificate chain: .gimmecert/ca/chain-full.cert.pem")

    subparser.set_defaults(func=init)

    return subparser


@subcommand_parser
def setup_help_subcommand_parser(parser, subparsers):
    subparser = subparsers.add_parser('help', description='shows help')

    subparser.set_defaults(func=lambda args: parser.print_help())

    return subparser


def get_parser():
    """
    Sets-up and returns a CLI argument parser.

    :returns: argparse.ArgumentParser -- argument parser for CLI.
    """

    parser = argparse.ArgumentParser(description=DESCRIPTION)

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
