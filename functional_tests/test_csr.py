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


def test_commands_report_csr_option_as_available():
    # John is in the process of testing a new project deployment. As
    # part of the process, he generates private keys on the servers,
    # and needs to issue corresponding certificates.

    # John knows that he can generate both private key and certificate
    # using Gimmecert, but in this particular case he would like to
    # keep his private keys on the server side intact. John goes ahead
    # and checks if the issuance commands support passing-in a CSR
    # instead of using locally generated private key.

    # He checks help for the server command.
    stdout, stderr, exit_code = run_command("gimmecert", "server", "-h")

    # John notcies the option for passing-in a CSR.
    assert " --csr " in stdout
    assert " -c " in stdout

    # He checks help for the client command.
    stdout, stderr, exit_code = run_command("gimmecert", "client", "-h")

    # John notcies the option for passing-in a CSR.
    assert " --csr " in stdout
    assert " -c " in stdout

    # He checks help for the renew command.
    stdout, stderr, exit_code = run_command("gimmecert", "renew", "-h")

    # John notcies the option for passing-in a CSR.
    assert " --csr " in stdout
    assert " -c " in stdout
