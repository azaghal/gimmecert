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
