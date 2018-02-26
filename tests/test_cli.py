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


import argparse

import gimmecert.cli

from unittest import mock


def test_get_parser_returns_parser():
    parser = gimmecert.cli.get_parser()

    assert isinstance(parser, argparse.ArgumentParser)


@mock.patch('gimmecert.cli.get_parser')
def test_main_invokes_get_parser(mock_get_parser):

    gimmecert.cli.main()

    mock_get_parser.assert_called_once_with()


@mock.patch('gimmecert.cli.get_parser')
def test_main_invokes_argument_parsing(mock_get_parser):
    mock_parser = mock.Mock()
    mock_get_parser.return_value = mock_parser

    gimmecert.cli.main()

    mock_parser.parse_args.assert_called_once_with()
