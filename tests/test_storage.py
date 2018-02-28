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

import os

import gimmecert.crypto
import gimmecert.storage


def test_initialise_storage(tmpdir):
    tmpdir.chdir()

    gimmecert.storage.initialise_storage(tmpdir.strpath)

    assert os.path.exists(tmpdir.join('.gimmecert').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca').strpath)


def test_write_private_key(tmpdir):
    tmpdir.chdir()

    private_key = gimmecert.crypto.generate_private_key()
    key_path = tmpdir.join('test.key.pem').strpath

    gimmecert.storage.write_private_key(private_key, key_path)

    assert os.path.exists(key_path)

    with open(key_path, 'r') as key_file:
        content = key_file.read()
        assert 'BEGIN RSA PRIVATE KEY' in content
        assert 'END RSA PRIVATE KEY' in content


def test_write_certificate(tmpdir):
    tmpdir.chdir()

    issuer_dn = gimmecert.crypto.get_dn('My test 1')
    subject_dn = gimmecert.crypto.get_dn('My test 2')
    issuer_private_key = gimmecert.crypto.generate_private_key()
    subject_private_key = gimmecert.crypto.generate_private_key()
    not_before, not_after = gimmecert.crypto.get_validity_range()
    certificate = gimmecert.crypto.issue_certificate(issuer_dn, subject_dn, issuer_private_key, subject_private_key.public_key(), not_before, not_after)

    certificate_path = tmpdir.join('test.key.pem').strpath

    gimmecert.storage.write_certificate(certificate, certificate_path)

    assert os.path.exists(certificate_path)

    with open(certificate_path, 'r') as certificate_file:
        content = certificate_file.read()
        assert 'BEGIN CERTIFICATE' in content
        assert 'END CERTIFICATE' in content
