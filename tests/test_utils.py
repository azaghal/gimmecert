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


import datetime
import io

import cryptography.x509
import cryptography.hazmat.backends

import gimmecert.crypto
import gimmecert.utils

import pytest


def test_certificate_to_pem_returns_valid_pem():
    dn = gimmecert.crypto.get_dn('My test 1')
    private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
    not_before, not_after = gimmecert.crypto.get_validity_range()
    certificate = gimmecert.crypto.issue_certificate(dn, dn, private_key, private_key.public_key(), not_before, not_after)

    certificate_pem = gimmecert.utils.certificate_to_pem(certificate)

    assert isinstance(certificate_pem, str)
    certificate_from_pem = cryptography.x509.load_pem_x509_certificate(bytes(certificate_pem, encoding='UTF-8'),
                                                                       cryptography.hazmat.backends.default_backend())  # Should not throw
    assert certificate_from_pem.subject == certificate.subject
    assert certificate_from_pem.issuer == certificate.issuer


def test_dn_to_str_with_cn():
    dn = gimmecert.crypto.get_dn('My test 1')

    dn_str = gimmecert.utils.dn_to_str(dn)

    assert isinstance(dn_str, str)
    assert dn_str == "CN=My test 1"


def test_dn_to_str_raises_for_unsupported_field_type():

    dn = cryptography.x509.Name([cryptography.x509.NameAttribute(cryptography.x509.oid.NameOID.COUNTRY_NAME, "RS")])

    with pytest.raises(gimmecert.utils.UnsupportedField):

        gimmecert.utils.dn_to_str(dn)


def test_date_range_to_str():
    begin = datetime.datetime(2017, 1, 2, 3, 4, 5)
    end = datetime.datetime(2018, 6, 7, 8, 9, 10)

    representation = gimmecert.utils.date_range_to_str(begin, end)

    assert isinstance(representation, str)
    assert representation == "2017-01-02 03:04:05 UTC - 2018-06-07 08:09:10 UTC"


def test_get_dns_names_returns_empty_list_if_no_dns_names():
    issuer_private_key, issuer_certificate = gimmecert.crypto.generate_ca_hierarchy('My Test', 1, gimmecert.crypto.KeyGenerator("rsa", 2048))[0]
    private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()

    certificate = gimmecert.crypto.issue_client_certificate(
        'myclient', private_key.public_key(),
        issuer_private_key, issuer_certificate
    )

    dns_names = gimmecert.utils.get_dns_names(certificate)

    assert isinstance(dns_names, list)
    assert dns_names == []


def test_get_dns_names_returns_list_of_dns_names():

    issuer_private_key, issuer_certificate = gimmecert.crypto.generate_ca_hierarchy('My Test', 1, gimmecert.crypto.KeyGenerator("rsa", 2048))[0]
    private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()

    certificate = gimmecert.crypto.issue_server_certificate(
        'myserver', private_key.public_key(),
        issuer_private_key, issuer_certificate,
        extra_dns_names=['myservice1.example.com', 'myservice2.example.com']
    )

    dns_names = gimmecert.utils.get_dns_names(certificate)

    assert isinstance(dns_names, list)
    assert dns_names == ['myserver', 'myservice1.example.com', 'myservice2.example.com']


def test_read_long_input():

    provided_input = """\
This is my input string that
spans multiple
lines.
"""

    input_stream = io.StringIO()
    prompt_stream = io.StringIO()

    # End the input with Ctrl-D.
    input_stream.write(provided_input)
    input_stream.seek(0)

    returned_input = gimmecert.utils.read_input(input_stream, prompt_stream, "My prompt")

    prompt = prompt_stream.getvalue()

    assert prompt == "My prompt (finish with Ctrl-D on an empty line):\n\n"
    assert isinstance(returned_input, str)
    assert returned_input == provided_input


def test_csr_from_pem(key_with_csr):

    csr = gimmecert.utils.csr_from_pem(key_with_csr.csr_pem)

    assert isinstance(csr, cryptography.x509.CertificateSigningRequest)
    assert csr.public_key().public_numbers() == key_with_csr.csr.public_key().public_numbers()
    assert csr.subject == key_with_csr.csr.subject
