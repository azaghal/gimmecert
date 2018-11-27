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


import io
import subprocess

import pexpect


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


def run_interactive_command(prompt_answers, command, *args):
    """
    Helper function that runs the specified command, and takes care of
    providing answers to interactive prompts.

    This is a convenience wrapper around the pexpect library.

    Unlikes the run_command helper, this helper is not capable of
    separating the standard output from standard error
    (unfortunately).

    The failure message returned describes only issues related to
    command not providing the expected prompt for answer, or if
    command gets stuck in a prompt after all expected prompts were
    processed.

    :param prompt_answers: List of prompts and their correspnding answers. To send a control character, start the answer with 'Ctrl-' (for example 'Ctrl-d').
    :type prompt_answers: list[(str, str)]

    :param command: Command that should be run.
    :type command: str

    :param *args: Zero or more arguments to pass to the command.
    :type *args: str

    :returns: (failure, output, exit_code) -- Prompt failure message, combined standard output and error, and exit code (None if prompt failure happened).
    :rtype: (str or None, str, int)
    """

    # Assume that all prompts/answers worked as expected.
    failure = None

    # Spawn the process, use dedicated stream for capturin command
    # stdout/stderr.
    output_stream = io.StringIO()
    send_stream = io.StringIO()
    process = pexpect.spawnu(command, list(args), timeout=4)
    process.logfile_read = output_stream
    process.logfile_send = send_stream

    # Try to feed the interactive process with answers. Stop iteration
    # at first prompt that was not reached.
    for prompt, answer in prompt_answers:
        try:
            process.expect(prompt)
            if answer.startswith('Ctrl-'):
                process.sendcontrol(answer.lstrip('Ctrl-'))
            else:
                process.sendline(answer)
        except pexpect.TIMEOUT:
            failure = "Command never prompted us with: %s" % prompt
            process.terminate()
            break

    # If we were successful until now, wait for the process to exit.
    if failure is None:
        try:
            process.expect(pexpect.EOF)
        except pexpect.TIMEOUT:
            failure = "Command got stuck waiting for input."
            process.terminate()

    process.close()
    output = output_stream.getvalue()
    exit_code = process.exitstatus

    return failure, output, exit_code
