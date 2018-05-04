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


@pytest.mark.parametrize("setup_subcommand_parser", gimmecert.decorators.get_subcommand_parser_setup_functions())
def test_setup_subcommand_parser_returns_parser(setup_subcommand_parser):
    """
    Tests if functions registered to return a subcommand parser return
    a valid parser object.

    Test is parametrised in order to avoid code duplication, and it
    will automatically fetch registered functions, making it
    unnecessary to list them here explicitly.
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = setup_subcommand_parser(parser, subparsers)

    assert isinstance(subparser, argparse.ArgumentParser)


@pytest.mark.parametrize("setup_subcommand_parser", gimmecert.decorators.get_subcommand_parser_setup_functions())
def test_setup_subcommand_parser_sets_function_callback(setup_subcommand_parser):
    """
    Tests if functions registered to return a subcommand parser will
    set a default function to be called (as command invocation).

    Test is parametrised in order to avoid code duplication, and it
    will automatically fetch registered functions, making it
    unnecessary to list them here explicitly.
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = setup_subcommand_parser(parser, subparsers)

    assert callable(subparser.get_default('func'))


@pytest.mark.parametrize(
    "setup_subcommand_parser",
    [
        gimmecert.cli.setup_help_subcommand_parser,
        gimmecert.cli.setup_init_subcommand_parser,
        gimmecert.cli.setup_server_subcommand_parser,
        gimmecert.cli.setup_client_subcommand_parser,
        gimmecert.cli.setup_renew_subcommand_parser,
        gimmecert.cli.setup_status_subcommand_parser
    ]
)
def test_setup_subcommand_parser_registered(setup_subcommand_parser):
    """
    Tests if functions registered to return a subcommand parser have
    been registered correctly using a decorator.

    Test is parametrised in order to avoid code duplication. New
    functions should simply be added to the list of functions.
    """

    registered_functions = gimmecert.decorators.get_subcommand_parser_setup_functions()

    assert setup_subcommand_parser in registered_functions


# List of valid CLI invocations to use in
# test_parser_commands_and_options_are_available.
#
# Each element in this list should be a tuple where first element is
# the command function (relative to CLI module) that should be mocked,
# while second element is list of CLI arguments for invoking the
# command from CLI. See test documentation for more details.
VALID_CLI_INVOCATIONS = [
    # help, no options
    ("gimmecert.cli.help_", ["gimmecert", "help"]),

    # init, no options
    ("gimmecert.cli.init", ["gimmecert", "init"]),

    # init, CA base name long and short option
    ("gimmecert.cli.init", ["gimmecert", "init", "--ca-base-name", "My Project"]),
    ("gimmecert.cli.init", ["gimmecert", "init", "-b", "My Project"]),

    # init, CA hierarchy depth long and short option
    ("gimmecert.cli.init", ["gimmecert", "init", "--ca-hierarchy-depth", "3"]),
    ("gimmecert.cli.init", ["gimmecert", "init", "-d", "3"]),

    # server, no options
    ("gimmecert.cli.server", ["gimmecert", "server", "myserver"]),

    # server, multiple DNS names, no options
    ("gimmecert.cli.server", ["gimmecert", "server", "myserver",
                              "myserver.example.com"]),
    ("gimmecert.cli.server", ["gimmecert", "server", "myserver",
                              "myserver1.example.com", "myserver2.example.com",
                              "myserver3.example.com", "myserver4.example.com"]),

    # server, CSR long and short option
    ("gimmecert.cli.server", ["gimmecert", "server", "--csr", "myserver.csr.pem", "myserver"]),
    ("gimmecert.cli.server", ["gimmecert", "server", "-c", "myserver.csr.pem", "myserver"]),

    # client, no options
    ("gimmecert.cli.client", ["gimmecert", "client", "myclient"]),

    # client, CSR long and short option
    ("gimmecert.cli.client", ["gimmecert", "client", "--csr", "myclient.csr.pem", "myclient"]),
    ("gimmecert.cli.client", ["gimmecert", "client", "-c", "myclient.csr.pem", "myclient"]),

    # renew, no options
    ("gimmecert.cli.renew", ["gimmecert", "renew", "server", "myserver"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "client", "myclient"]),

    # renew, server, update dns names long and short option
    ("gimmecert.cli.renew", ["gimmecert", "renew", "--update-dns-names", "myservice.example.com", "server", "myserver"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "--update-dns-names", "", "server", "myserver"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "-u", "myservice.example.com", "server", "myserver"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "-u", "", "server", "myserver"]),

    # renew, generate new private key long and short option
    ("gimmecert.cli.renew", ["gimmecert", "renew", "--new-private-key", "server", "myserver"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "--new-private-key", "client", "myclient"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "-p", "server", "myserver"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "-p", "client", "myclient"]),

    # renew, CSR long and short option
    ("gimmecert.cli.renew", ["gimmecert", "renew", "--csr", "myserver.csr.pem", "server", "myserver"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "--csr", "myclient.csr.pem", "client", "myclient"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "-c", "myserver.csr.pem", "server", "myserver"]),
    ("gimmecert.cli.renew", ["gimmecert", "renew", "-c", "myclient.csr.pem", "client", "myclient"]),

    # status, no options
    ("gimmecert.cli.status", ["gimmecert", "status"]),
]


@pytest.mark.parametrize("command_function, cli_invocation", VALID_CLI_INVOCATIONS)
def test_parser_commands_and_options_are_available(tmpdir, command_function, cli_invocation):
    """
    Tests handling of valid CLI invocations by top-level and command
    parsers.

    This test helps greatly reduce duplication of code, at the expense
    of some flexibility.

    The passed-in command_function is mocked and set-up to return a
    success exit code, since the main point is to ensure the CLI
    supports specific commands and parameters.

    To add a new valid invocation of CLI, update the
    VALID_CLI_INVOCATIONS variable above.
    """

    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with mock.patch(command_function) as mock_command_function, mock.patch('sys.argv', cli_invocation):
        mock_command_function.return_value = gimmecert.commands.ExitCode.SUCCESS

        gimmecert.cli.main()  # Should not raise


@pytest.mark.parametrize("command", ["help", "init", "server", "client", "renew", "status"])
@pytest.mark.parametrize("help_option", ["--help", "-h"])
def test_command_exists_and_accepts_help_flag(tmpdir, command, help_option):
    """
    Tests availability of commands and whether they accept the help
    flag.

    Test is parametrised in order to avoid code duplication. The only
    thing necessary to add a new command is to extend the command
    parameter.

    Both short and long form of help flag is tested.
    """

    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with mock.patch('sys.argv', ['gimmecert', command, help_option]):
        with pytest.raises(SystemExit) as e_info:
            gimmecert.cli.main()

        assert e_info.value.code == 0


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
def test_server_command_invoked_with_correct_parameters_without_extra_dns_names(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_server.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'myserver', [], None)


@mock.patch('sys.argv', ['gimmecert', 'server', 'myserver', 'service.local', 'service.example.com'])
@mock.patch('gimmecert.cli.server')
def test_server_command_invoked_with_correct_parameters_with_extra_dns_names(mock_server, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_server.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_server.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'myserver', ['service.local', 'service.example.com'], None)


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
def test_client_command_invoked_with_correct_parameters(mock_client, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_client.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_client.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'myclient', None)


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
def test_renew_command_invoked_with_correct_parameters_for_server(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'server', 'myserver', False, None, None)


@mock.patch('sys.argv', ['gimmecert', 'renew', 'client', 'myclient'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_client(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'client', 'myclient', False, None, None)


@mock.patch('sys.argv', ['gimmecert', 'renew', '--new-private-key', 'server', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_server_with_new_private_key_option(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'server', 'myserver', True, None, None)


@mock.patch('sys.argv', ['gimmecert', 'renew', '--new-private-key', 'client', 'myclient'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_client_with_new_private_key_option(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'client', 'myclient', True, None, None)


@mock.patch('sys.argv', ['gimmecert', 'renew', '--csr', 'mycustom.csr.pem', 'server', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_server_with_csr_option(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'server', 'myserver', False, 'mycustom.csr.pem', None)


@mock.patch('sys.argv', ['gimmecert', 'renew', '--csr', 'mycustom.csr.pem', 'client', 'myclient'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_client_with_csr_option(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath, 'client', 'myclient', False, 'mycustom.csr.pem', None)


@mock.patch('sys.argv', ['gimmecert', 'renew', '--update-dns-names', 'myservice1.example.com,myservice2.example.com', 'server', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_invoked_with_correct_parameters_for_client_with_update_dns_option(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_renew.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_renew.assert_called_once_with(sys.stdout, sys.stderr,
                                       tmpdir.strpath,
                                       'server', 'myserver', False, None, ['myservice1.example.com', 'myservice2.example.com'])


@mock.patch('sys.argv', ['gimmecert', 'status'])
@mock.patch('gimmecert.cli.status')
def test_status_command_invoked_with_correct_parameters(mock_status, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    mock_status.return_value = gimmecert.commands.ExitCode.SUCCESS

    gimmecert.cli.main()

    mock_status.assert_called_once_with(sys.stdout, sys.stderr, tmpdir.strpath)


@mock.patch('sys.argv', ['gimmecert', 'renew', 'server', '--new-private-key', '--csr', 'myserver.csr.pem', 'myserver'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_fails_if_both_new_private_key_and_csr_options_are_specified_for_server(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert mock_renew.called is False
    assert e_info.value.code != 0


@mock.patch('sys.argv', ['gimmecert', 'renew', 'client', '--new-private-key', '--csr', 'myclient.csr.pem', 'myclient'])
@mock.patch('gimmecert.cli.renew')
def test_renew_command_fails_if_both_new_private_key_and_csr_options_are_specified_for_client(mock_renew, tmpdir):
    # This should ensure we don't accidentally create artifacts
    # outside of test directory.
    tmpdir.chdir()

    with pytest.raises(SystemExit) as e_info:
        gimmecert.cli.main()

    assert mock_renew.called is False
    assert e_info.value.code != 0
