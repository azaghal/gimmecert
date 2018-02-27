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


def run_command(command, *args):
    """
    Helper function that runs the specified command, and takes care of
    some tedious work, like converting the stdout and stderr to
    correct encoding etc.

    This is essentially a small wrapper around the subprocess.Popen.

    :param command: Command that should be run.
    :type command: str

    :param *args: Zero or more arguments to pass to the command.
    :type *args: str

    :returns: (stdout, stderr, exit_code) -- Standard output, error, and exit code captured from running the command.
    :rtype: (str, str, int)
    """

    invocation = [command]
    invocation.extend(args)

    process = subprocess.Popen(invocation, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    return stdout, stderr, process.returncode
