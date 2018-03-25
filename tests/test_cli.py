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
import sys

import gimmecert.cli
import gimmecert.decorators

import pytest
from unittest import mock


def test_get_parser_returns_parser():
    parser = gimmecert.cli.get_parser()

    assert isinstance(parser, argparse.ArgumentParser)


@mock.patch('gimmecert.cli.get_parser')
def test_main_invokes_get_parser(mock_get_parser, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    # Ignore system exit. Dirty hack to avoid mocking the default
    # function. We care only about whether the get_parser is invoked.
    try:
        gimmecert.cli.main()
    except SystemExit:
        pass

    mock_get_parser.assert_called_once_with()


@mock.patch('gimmecert.cli.get_parser')
def test_main_invokes_argument_parsing(mock_get_parser, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_parser = mock.Mock()
    mock_get_parser.return_value = mock_parser

    # Ignore system exit. Dirty hack to avoid mocking the default
    # function. We care only about whether the parsing of arguments
    # got called.x
    try:
        gimmecert.cli.main()
    except SystemExit:
        pass

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
def test_main_invokes_parser_function(mock_get_parser, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_parser = mock.Mock()
    mock_args = mock.Mock()

    # Avoid throws of SystemExit exception.
    mock_args.func.return_value = gimmecert.commands.ExitCode.SUCCESS

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
@mock.patch('gimmecert.cli.init')
def test_init_command_invoked_with_correct_parameters_no_options(mock_init, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_init.return_value = gimmecert.commands.ExitCode.SUCCESS

    default_depth = 1

    gimmecert.cli.main()

    mock_init.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, tmpdir.basename, default_depth)


@mock.patch('sys.argv', ['gimmecert', 'init', '-b', 'My Project'])
@mock.patch('gimmecert.cli.init')
def test_init_command_invoked_with_correct_parameters_with_options(mock_init, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_init.return_value = gimmecert.commands.ExitCode.SUCCESS

    default_depth = 1

    gimmecert.cli.main()

    mock_init.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'My Project', default_depth)


@mock.patch('sys.argv', ['gimmecert', 'init', '--ca-base-name', 'My Project'])
@mock.patch('gimmecert.cli.init')
def test_init_command_accepts_ca_base_name_option_long_form(mock_init, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_init.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'init', '-b', 'My Project'])
@mock.patch('gimmecert.cli.init')
def test_init_command_accepts_ca_base_name_option_short_form(mock_init, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_init.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'init', '--ca-hierarchy-depth', '3'])
@mock.patch('gimmecert.cli.init')
def test_init_command_accepts_ca_hierarchy_depth_option_long_form(mock_init, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_init.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'init', '-d', '3'])
@mock.patch('gimmecert.cli.init')
def test_init_command_accepts_ca_hierarchy_depth_option_short_form(mock_init, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_init.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'server', '-h'])
def test_server_command_exists_and_accepts_help_flag(tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert e_info.value.code == 0


def test_setup_server_subcommand_parser_registered():
    registered_functions = gimmecert.decorators.get_subcommand_parser_setup_functions()

    assert gimmecert.cli.setup_server_subcommand_parser in registered_functions


def test_setup_server_subcommand_parser_returns_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_server_subcommand_parser(parser, subparsers)

    assert isinstance(subparser, argparse.ArgumentParser)


@mock.patch('sys.argv', ['gimmecert', 'server'])
def test_setup_server_subcommand_fails_without_arguments(tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert e_info.value.code != 0


@mock.patch('sys.argv', ['gimmecert', 'server', 'myserver'])
@mock.patch('gimmecert.cli.server')
def test_setup_server_subcommand_succeeds_with_just_entity_name_argument(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    # We are just testing the parsing here.
    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise.


@mock.patch('sys.argv', ['gimmecert', 'server', 'myserver', 'myserver.example.com'])
@mock.patch('gimmecert.cli.server')
def test_setup_server_subcommand_succeeds_with_entity_name_argument_and_one_dns_name(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    # We are just testing the parsing here.
    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise.


@mock.patch('sys.argv', ['gimmecert', 'server', 'myserver', 'myserver1.example.com', 'myserver2.example.com', 'myserver3.example.com', 'myserver4.example.com'])
@mock.patch('gimmecert.cli.server')
def test_setup_server_subcommand_succeeds_with_entity_name_argument_and_four_dns_names(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    # We are just testing the parsing here.
    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise.


def test_setup_server_subcommand_sets_function_callback():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_server_subcommand_parser(parser, subparsers)

    assert callable(subparser.get_default('func'))


@mock.patch('sys.argv', ['gimmecert', 'server', 'myserver'])
@mock.patch('gimmecert.cli.server')
def test_server_command_invoked_with_correct_parameters_without_extra_dns_names(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_server.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'myserver', [], False)


@mock.patch('sys.argv', ['gimmecert', 'server', 'myserver', 'service.local', 'service.example.com'])
@mock.patch('gimmecert.cli.server')
def test_server_command_invoked_with_correct_parameters_with_extra_dns_names(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_server.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'myserver', ['service.local', 'service.example.com'], False)


@mock.patch('sys.argv', ['gimmecert', 'help'])
@mock.patch('gimmecert.cli.help_')
def test_help_command_invoked_with_correct_parameters(mock_help_, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_help_.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    assert mock_help_.called
    assert mock_help_.call_count == 1


@mock.patch('sys.argv', ['gimmecert'])
@mock.patch('gimmecert.cli.usage')
def test_usage_command_invoked_with_correct_parameters(mock_usage, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_usage.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    # Can't test calling arguments, since we'd need to mask
    # get_parser, and if we do that we mask the set_defaults and
    # what-not.
    assert mock_usage.called
    assert mock_usage.call_count == 1


@mock.patch('sys.argv', ['gimmecert', 'testcommand'])
def test_main_does_not_exit_if_it_calls_function_that_returns_success(tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    @gimmecert.decorators.subcommand_parser
    def setup_testcommand_parser(parser, subparsers):
        subparser = subparsers.add_parser('testcommand', description='test command')

        def testcommand_wrapper(args):

            return gimmecert.commands.ExitCode.SUCCESS

        subparser.set_defaults(func=testcommand_wrapper)

        return subparser

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'testcommand'])
def test_main_exits_if_it_calls_function_that_returns_success(tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    @gimmecert.decorators.subcommand_parser
    def setup_testcommand_parser(parser, subparsers):
        subparser = subparsers.add_parser('testcommand', description='test command')

        def testcommand_wrapper(args):

            return gimmecert.commands.ExitCode.ERROR_ALREADY_INITIALISED

        subparser.set_defaults(func=testcommand_wrapper)

        return subparser

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert e_info.value.code == gimmecert.commands.ExitCode.ERROR_ALREADY_INITIALISED


@mock.patch('sys.argv', ['gimmecert', 'client', '-h'])
def test_client_command_exists_and_accepts_help_flag(tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert e_info.value.code == 0


def test_setup_client_subcommand_parser_registered():
    registered_functions = gimmecert.decorators.get_subcommand_parser_setup_functions()

    assert gimmecert.cli.setup_client_subcommand_parser in registered_functions


def test_setup_client_subcommand_parser_returns_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_client_subcommand_parser(parser, subparsers)

    assert isinstance(subparser, argparse.ArgumentParser)


@mock.patch('sys.argv', ['gimmecert', 'client'])
def test_setup_client_subcommand_fails_without_arguments(tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert e_info.value.code != 0


@mock.patch('sys.argv', ['gimmecert', 'client', 'myclient'])
@mock.patch('gimmecert.cli.client')
def test_setup_client_subcommand_succeeds_with_entity_name_argument(mock_client, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    # We are just testing the parsing here.
    mock_client.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise.


def test_setup_client_subcommand_sets_function_callback():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_client_subcommand_parser(parser, subparsers)

    assert callable(subparser.get_default('func'))


@mock.patch('sys.argv', ['gimmecert', 'client', 'myclient'])
@mock.patch('gimmecert.cli.client')
def test_client_command_invoked_with_correct_parameters(mock_client, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_client.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_client.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'myclient')


@mock.patch('sys.argv', ['gimmecert', 'server', '--update-dns-names', 'myserver'])
@mock.patch('gimmecert.cli.server')
def test_server_command_accepts_update_option_long_form(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'server', '-u', 'myserver'])
@mock.patch('gimmecert.cli.server')
def test_server_command_accepts_update_option_short_form(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'server', '--update-dns-names', 'myserver', 'service.local'])
@mock.patch('gimmecert.cli.server')
def test_server_command_invoked_with_correct_parameters_with_update_option(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_server.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'myserver', ['service.local'], True)


@mock.patch('sys.argv', ['gimmecert', 'renew', '-h'])
def test_renew_command_exists_and_accepts_help_flag(tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert e_info.value.code == 0


def test_setup_renew_subcommand_parser_registered():
    registered_functions = gimmecert.decorators.get_subcommand_parser_setup_functions()

    assert gimmecert.cli.setup_renew_subcommand_parser in registered_functions


def test_setup_renew_subcommand_parser_returns_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_renew_subcommand_parser(parser, subparsers)

    assert isinstance(subparser, argparse.ArgumentParser)


@mock.patch('sys.argv', ['gimmecert', 'renew'])
def test_renew_command_fails_without_arguments(tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert e_info.value.code != 0


@mock.patch('sys.argv', ['gimmecert', 'renew', 'server', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_accepts_entity_type_server_and_entity_name(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    # We are just testing the parsing here.
    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'renew', 'client', 'myclient'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_accepts_entity_type_client_and_entity_name(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    # We are just testing the parsing here.
    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


def test_setup_renew_subcommand_sets_function_callback():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = gimmecert.cli.setup_renew_subcommand_parser(parser, subparsers)

    assert callable(subparser.get_default('func'))


@mock.patch('sys.argv', ['gimmecert', 'renew', 'server', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_server(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'server', 'myserver', False)


@mock.patch('sys.argv', ['gimmecert', 'renew', 'client', 'myclient'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_client(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'client', 'myclient', False)


@mock.patch('sys.argv', ['gimmecert', 'renew', '--new-private-key', 'server', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_server_with_new_private_key_option(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'server', 'myserver', True)


@mock.patch('sys.argv', ['gimmecert', 'renew', '--new-private-key', 'client', 'myclient'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_client_with_new_private_key_option(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'client', 'myclient', True)


@mock.patch('sys.argv', ['gimmecert', 'renew', 'server', '--new-private-key', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_accepts_renew_private_key_option_long_form(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise


@mock.patch('sys.argv', ['gimmecert', 'renew', 'server', '-p', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_accepts_renew_private_key_option_short_form(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()  # Should not raise
