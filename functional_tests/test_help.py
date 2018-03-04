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


def test_cli_works():
    # John is a system integrator that in his line of work often needs
    # to issue certificates for testing. Just recently, he has heard
    # of a new tool called gimmecert that can be used for issuing
    # certificates in test environments that would make his life
    # easier.

    # John goes ahead and installs the tool on his local machine.

    # Before moving on, John decides to quickly test if the package
    # has been installed correctly. Assuming that the command is the
    # same as package name, he runs it.
    stdout, stderr, returncode = run_command("gimmecert")

    # John has a look at output, and notices that no error has been
    # reported. He also verifies the return code is non-zero, just to
    # be on the safe side.
    assert stderr == ''
    assert returncode == 0


def test_usage_help_shown():
    # Since John feels a bit lazy, he decides to skip reading the
    # documentation, and just run the tool to see if he gets any
    # useful help.
    stdout, stderr, returncode = run_command("gimmecert")

    # John is presented with short usage instructions.
    assert "usage: gimmecert [-h]" in stdout
    assert stderr == ''
    assert returncode == 0


def test_extended_help_shown():
    # John is still not quite sure how the tool works. Therefore he
    # decides to try out the -h flag to the command.
    stdout_h_flag, stderr_h_flag, returncode_h_flag = run_command("gimmecert", "-h")

    # In doing so, John is presented with much more extensive
    # instructions that provide him with better idea on how to use the
    # tool.
    assert stderr_h_flag == ''
    assert returncode_h_flag == 0
    assert "usage: gimmecert [-h]" in stdout_h_flag
    assert "Examples:" in stdout_h_flag
    assert "gimmecert init" in stdout_h_flag
    assert "gimmecert server myserver" in stdout_h_flag
    assert "gimmecert server myserver extradns1.local extradns2.example.com" in stdout_h_flag
    assert "optional arguments" in stdout_h_flag
    # Subcommands listed.
    assert "help" in stdout_h_flag
    # @TODO: Can't really test this without producing errors, but
    # possibly not needed.
    # assert "positional arguments" in stdout_h_flag

    # John also notices the help command in the list. He tries that
    # one out as well.
    stdout_help, stderr_help, returncode_help = run_command("gimmecert", "help")

    # John is presented with identical results as when running just
    # with the -h flag.
    assert returncode_help == 0
    assert stdout_help == stdout_h_flag
    assert stderr_help == stderr_h_flag
