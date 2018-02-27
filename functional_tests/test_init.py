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


def test_init_command_available_with_help():
    # John has decided it is time to try out the tool. He starts off
    # by running the short usage help.
    stdout, stderr, returncode = run_command("gimmecert", "-h")

    # Looking at output, John notices the init command.
    assert returncode == 0
    assert stderr == ""
    assert 'init' in stdout

    # John decides to look at a more detailed description of this
    # command before proceeding.
    stdout, stderr, returncode = run_command("gimmecert", "init", "-h")

    # John notices that this command has some useful usage
    # instructions, which allows him to study the available arguments.
    assert returncode == 0
    assert stderr == ""
    assert stdout.startswith("usage: gimmecert init")
