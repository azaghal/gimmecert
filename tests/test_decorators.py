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


import collections.abc

import gimmecert.decorators

import pytest


def test_get_subcommand_parser_setup_functions_returns_list():

    registered_functions = gimmecert.decorators.get_subcommand_parser_setup_functions()

    assert isinstance(registered_functions, collections.abc.Iterable)


def test_subcommand_parser_decorator_registers_function():

    @gimmecert.decorators.subcommand_parser
    def myfunction1(parser, subparsers):
        pass

    @gimmecert.decorators.subcommand_parser
    def myfunction2(parser, subparsers):
        pass

    registered_functions = gimmecert.decorators.get_subcommand_parser_setup_functions()

    assert myfunction1 in registered_functions
    assert myfunction2 in registered_functions


def test_subcommand_parser_decorator_ensures_function_has_correct_signature():

    with pytest.raises(gimmecert.decorators.SetupSubcommandParserInvalidSignature):

        @gimmecert.decorators.subcommand_parser
        def invalid_signature_no_arguments():
            pass

    with pytest.raises(gimmecert.decorators.SetupSubcommandParserInvalidSignature):

        @gimmecert.decorators.subcommand_parser
        def invalid_signature_too_many_arguments(parser, subparsers, extra):
            pass
