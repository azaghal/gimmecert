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


import subprocess


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
    process = subprocess.Popen(["gimmecert"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    # John has a look at output, and notices that no error has been
    # reported. He also verifies the return code is non-zero, just to
    # be on the safe side.
    assert stderr == ''
    assert process.returncode == 0


def test_usage_help_shown():
    # Since John feels a bit lazy, he decides to skip reading the
    # documentation, and just run the tool to see if he gets any
    # useful help.
    process = subprocess.Popen(["gimmecert"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    # John is presented with short usage instructions.
    assert "usage: gimmecert [-h]" in stdout
    assert stderr == ''
    assert process.returncode == 0


def test_extended_help_shown():
    # John is still not quite sure how the tool works. Therefore he
    # decides to try out the -h flag to the command.
    process = subprocess.Popen(["gimmecert", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    # In doing so, John is presented with much more extensive
    # instructions that provide him with better idea on how to use the
    # tool.
    assert stderr == ''
    assert process.returncode == 0
    assert "usage: gimmecert [-h]" in stdout
    assert "Examples:" in stdout
    assert "optional arguments" in stdout
    # @TODO: Can't really test this without producing errors, but
    # possibly not needed.
    # assert "positional arguments" in stdout
    # @TODO: Can't test at the moment, should be added once the first
    # commands is implemented.
    # assert "command1|command2" in stdout
