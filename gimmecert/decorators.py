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


import inspect


subcommand_parser_functions = []


class SetupSubcommandParserInvalidSignature(Exception):
    """
    Exception thrown if the registred subcommand parser setup
    functions has invalid signature.
    """
    pass


def subcommand_parser(func):
    """
    Decorator used for registering subcommand parser functions. By
    utilising this decorator it is possible to more easily register
    new subcommands as they are implemented, and to not depend on
    having multiple code paths that deal with instantion and set-up of
    subcommand parsers.

    The registered functions are expected to accept two arguments:

    - parser (ArgumentParser), instance of parent parser to which the
      subcommand (sub)parser belongs to.
    - subparsers, which has been previously obtained through a
      parser.get_subparsers() method on parent parser. The function
      should instantiate a subparser through it by calling the
      standard subparsers.add_parser() method.

    The registered functions are expeceted to return the subparser
    itself.

    It is expected that each subcomand parser will set a default
    function to be invoked with parsed arguments by doing a call to
    set_defaults(func=subcommand_function).

    Example usage:

    def mysubcommand(args):
        print("I received args: %s" % args)

    @subcommand_parser
    def mysubcommand_parser(parser, subparsers):
        subparser = subparsers.add_parser('mysubcommand', description='Does stuff!')

        subparser.set_defaults(func=mysubcommand)

        return subparser

    Later on the registered setup functions should be retrieved
    through get_subcommand_parser_setup_functions() function.

    :param func: Function (or callable) that should be registered for setting-up a subparser.
    :type func: callable
    :returns: func -- unchanged decorated function.
    """

    signature = inspect.signature(func)

    if len(signature.parameters) != 2:
        raise SetupSubcommandParserInvalidSignature("Function %s must accept two arguments" % func)

    subcommand_parser_functions.append(func)

    return func


def get_subcommand_parser_setup_functions():
    """
    Returns list of registered subcommand parser setup functions.

    :returns: List of registered subcommand parser setup functions.
    :rtype: list[callable]
    """

    return subcommand_parser_functions
