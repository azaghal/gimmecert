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


import cryptography.x509
import cryptography.hazmat.backends

import gimmecert.crypto
import gimmecert.utils


def test_certificate_to_pem_returns_valid_pem():
    dn = gimmecert.crypto.get_dn('My test 1')
    private_key = gimmecert.crypto.generate_private_key()
    not_before, not_after = gimmecert.crypto.get_validity_range()
    certificate = gimmecert.crypto.issue_certificate(dn, dn, private_key, private_key.public_key(), not_before, not_after)

    certificate_pem = gimmecert.utils.certificate_to_pem(certificate)

    assert isinstance(certificate_pem, bytes)
    certificate_from_pem = cryptography.x509.load_pem_x509_certificate(certificate_pem, cryptography.hazmat.backends.default_backend())  # Should not throw
    assert certificate_from_pem.subject == certificate.subject
    assert certificate_from_pem.issuer == certificate.issuer
