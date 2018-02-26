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


DESCRIPTION = """\
Issues server and client X.509 certificates using a local CA
hierarchy.

Examples:
"""


def get_parser():
    """
    Sets-up and returns a CLI argument parser.

    :returns: argparse.ArgumentParser -- argument parser for CLI.
    """

    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.set_defaults(func=lambda args: parser.print_usage())

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
