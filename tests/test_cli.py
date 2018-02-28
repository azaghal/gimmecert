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

import gimmecert.cli
import gimmecert.decorators

from unittest import mock


def test_get_parser_returns_parser():
    parser = gimmecert.cli.get_parser()

    assert isinstance(parser, argparse.ArgumentParser)


@mock.patch('gimmecert.cli.get_parser')
def test_main_invokes_get_parser(mock_get_parser):

    gimmecert.cli.main()

    mock_get_parser.assert_called_once_with()


@mock.patch('gimmecert.cli.get_parser')
def test_main_invokes_argument_parsing(mock_get_parser):
    mock_parser = mock.Mock()
    mock_get_parser.return_value = mock_parser

    gimmecert.cli.main()

    mock_parser.parse_args.assert_called_once_with()


def test_cli_parser_has_description():
    parser = gimmecert.cli.get_parser()

    assert parser.description


def test_parser_sets_up_default_callback_function():
    parser = gimmecert.cli.get_parser()

    assert callable(parser.get_default('func'))


@mock.patch('gimmecert.cli.argparse.ArgumentParser.print_usage')
def test_parser_default_callback_function_calls_print_usage(mock_print_usage):
    parser = gimmecert.cli.get_parser()
    func = parser.get_default('func')
    func(mock.Mock())

    assert mock_print_usage.called


@mock.patch('gimmecert.cli.get_parser')
def test_main_invokes_parser_function(mock_get_parser):
    mock_parser = mock.Mock()
    mock_args = mock.Mock()

    mock_parser.parse_args.return_value = mock_args
    mock_get_parser.return_value = mock_parser

    gimmecert.cli.main()

    mock_args.func.assert_called_once_with(mock_args)


def test_parser_help_contains_examples():
    parser = gimmecert.cli.get_parser()

    assert 'Examples' in parser.description


def test_setup_help_subcommand_parser_registered():
    registered_functions = gimmecert.decorators.get_subcommand_parser_setup_functions()

    assert gimmecert.cli.setup_help_subcommand_parser in registered_functions


@mock.patch('gimmecert.cli.get_subcommand_parser_setup_functions')
def test_get_parser_calls_setup_subcommand_parser_functions(mock_get_subcommand_parser_setup_functions):
    mock_setup1 = mock.Mock()
    mock_setup2 = mock.Mock()
    mock_get_subcommand_parser_setup_functions.return_value = [mock_setup1, mock_setup2]

    gimmecert.cli.get_parser()

    assert mock_setup1.called
    assert mock_setup2.called


def test_setup_help_subcommand_parser_adds_parser():
    mock_parser = mock.Mock()
    mock_subparsers = mock.Mock()

    gimmecert.cli.setup_help_subcommand_parser(mock_parser, mock_subparsers)

    assert mock_subparsers.add_parser.called


def test_help_subcommand_returns_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_help_subcommand_parser(parser, subparsers)

    assert isinstance(subparser, argparse.ArgumentParser)


def test_help_subcommand_sets_function_callback():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_help_subcommand_parser(parser, subparsers)

    assert callable(subparser.get_default('func'))


def test_setup_init_subcommand_parser_registered():
    registered_functions = gimmecert.decorators.get_subcommand_parser_setup_functions()

    assert gimmecert.cli.setup_init_subcommand_parser in registered_functions


def test_setup_init_subcommand_returns_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_init_subcommand_parser(parser, subparsers)

    assert isinstance(subparser, argparse.ArgumentParser)


def test_setup_init_subcommand_sets_function_callback():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_init_subcommand_parser(parser, subparsers)

    assert callable(subparser.get_default('func'))


@mock.patch('sys.argv', ['gimmecert', 'init'])
def test_init_subcommand_generates_ca_private_key(tmpdir):
    tmpdir.chdir()

    gimmecert.cli.main()

    print(tmpdir.listdir())

    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.key.pem').strpath)


@mock.patch('sys.argv', ['gimmecert', 'init'])
def test_init_subcommand_generates_ca_certificate(tmpdir):
    tmpdir.chdir()

    gimmecert.cli.main()

    print(tmpdir.listdir())

    assert os.path.exists(tmpdir.join('.gimmecert', 'ca', 'level1.cert.pem').strpath)
