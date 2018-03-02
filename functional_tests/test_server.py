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


def test_server_command_available_with_help():
    # John has finally finished initialising his CA hierarchy. What he
    # wants to do now is to issue a server certificate. He starts off
    # by having a look at the list of available commands.
    stdout, stderr, exit_code = run_command("gimmecert")

    # Looking at output, John notices the server command.
    assert exit_code == 0
    assert stderr == ""
    assert "server" in stdout

    # He goes ahead and has a look at the server command invocation to
    # check what kind of parameters he might need to provide.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "-h")

    # John can see that the command accepts an entity name, and an
    # optional list of DNS subject alternative names.
    assert exit_code == 0
    assert stderr == ""
    assert stdout.startswith("usage: gimmecert server")
    assert stdout.split('\n')[0].endswith(" entity_name [dns_name [dns_name ...]]")  # First line of help.
