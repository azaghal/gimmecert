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


from .base import run_command


def test_renew_command_available_with_help():
    # John has been issuing server and client certificates using
    # Gimmecert for a while now. The project has been in use for quite
    # some time, and John has realised the certificates might be about
    # to expire. Thinking how tedious it would be to generate
    # everything again from scratch, he tries to figure out if there
    # is an easier way to do it instead of providing information for
    # all of the entities instead.
    stdout, stderr, exit_code = run_command("gimmecert")

    # Looking at output, John notices the renew command.
    assert exit_code == 0
    assert stderr == ""
    assert "renew" in stdout

    # He goes ahead and has a look at command invocation to check what
    # kind of parameters he might need to provide.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # John can see that the command accepts two positional argument -
    # type of entity, and entity name.
    assert exit_code == 0
    assert stderr == ""
    assert stdout.startswith("usage: gimmecert renew")
    assert stdout.split('\n')[0].endswith("{server,client} entity_name")  # First line of help


def test_renew_command_requires_initialised_hierarchy(tmpdir):
    # John decides it's time to renew one of the certificates. He
    # switches to his project directory.
    tmpdir.chdir()

    # John tries to renew a server certificate.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "server", "myserver")

    # John has forgotten to initialise the CA hierarchy from within
    # this directory, and is instead presented with an error.
    assert exit_code != 0
    assert stdout == ""
    assert stderr == "No CA hierarchy has been initialised yet. Run the gimmecert init command and issue some certificates first.\n"

    # John gives the screen a weird look, and tries again, this time
    # with a client certificate renewal.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "client", "myclient")

    # John gets presented with the same error yet again. Suddenly, he
    # realizes he is in a wrong directory... Oh well...
    assert exit_code != 0
    assert stdout == ""
    assert stderr == "No CA hierarchy has been initialised yet. Run the gimmecert init command and issue some certificates first.\n"


def test_renew_command_reports_error_if_entity_does_not_exist(tmpdir):
    # John finally finds his way around to the project directory where
    # Gimmecert has already been used to set-up a hierarchy, and where
    # a couple of server and client certificates have been issued.
    tmpdir.chdir()
    run_command("gimmecert", "init")
    run_command("gimmecert", "server", "someserver")
    run_command("gimmecert", "client", "someclient")

    # He runs the command for renewing a server certificate.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'server', 'myserver')

    # Unfortunately for him, this server certificate has not been
    # issued before, and he is presented with an error.
    assert exit_code != 0
    assert stdout == ''
    assert stderr == "Cannot renew certificate. No existing certificate found for server myserver.\n"

    # This is going to be one of those days... He tries then to renew
    # a client certificate instead.
    stdout, stderr, exit_code = run_command('gimmecert', 'renew', 'client', 'myclient')

    # To his dismay, this results in error as well. He hasn't issued
    # such a certificate before either.
    assert exit_code != 0
    assert stdout == ''
    assert stderr == "Cannot renew certificate. No existing certificate found for client myclient.\n"
