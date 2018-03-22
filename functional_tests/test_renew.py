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
