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

import cryptography.hazmat.primitives.asymmetric.rsa
import cryptography.x509
from dateutil.relativedelta import relativedelta

import gimmecert.crypto

from freezegun import freeze_time


def test_generate_private_key_returns_private_key():
    private_key = gimmecert.crypto.generate_private_key()

    assert isinstance(private_key, cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey)


def test_get_dn():
    dn = gimmecert.crypto.get_dn('My test')
    assert isinstance(dn, cryptography.x509.Name)
    assert len(dn) == 1
    assert isinstance(list(dn)[0], cryptography.x509.NameAttribute)
    assert list(dn)[0].oid == cryptography.x509.oid.NameOID.COMMON_NAME
    assert list(dn)[0].value == 'My test'


def test_get_validity_range_returns_datetime_tuple():
    not_before, not_after = gimmecert.crypto.get_validity_range()

    assert isinstance(not_before, datetime.datetime)
    assert isinstance(not_after, datetime.datetime)


@freeze_time('2018-01-01 00:15:00')
def test_get_validity_range_not_before_is_within_15_minutes_of_now():
    not_before, _ = gimmecert.crypto.get_validity_range()

    assert not_before == datetime.datetime(2018, 1, 1, 0, 0)


@freeze_time('2018-01-01 00:15:00')
def test_get_validity_range_is_one_year_and_15_minutes():
    not_before, not_after = gimmecert.crypto.get_validity_range()
    difference = relativedelta(not_after, not_before)

    assert difference == relativedelta(years=1, minutes=15)


@freeze_time('2018-01-01 00:15:00.100')
def test_get_validity_range_drops_microseconds():
    not_before, not_after = gimmecert.crypto.get_validity_range()

    assert not_before.microsecond == 0
    assert not_after.microsecond == 0


def test_issue_certificate_returns_certificate():

    issuer_dn = gimmecert.crypto.get_dn('My test 1')
    subject_dn = gimmecert.crypto.get_dn('My test 2')
    issuer_private_key = gimmecert.crypto.generate_private_key()
    subject_private_key = gimmecert.crypto.generate_private_key()
    not_before, not_after = gimmecert.crypto.get_validity_range()

    certificate = gimmecert.crypto.issue_certificate(issuer_dn, subject_dn, issuer_private_key, subject_private_key.public_key(), not_before, not_after)

    assert isinstance(certificate, cryptography.x509.Certificate)


def test_issue_certificate_has_correct_content():
    issuer_dn = gimmecert.crypto.get_dn('My test 1')
    subject_dn = gimmecert.crypto.get_dn('My test 2')
    issuer_private_key = gimmecert.crypto.generate_private_key()
    subject_private_key = gimmecert.crypto.generate_private_key()
    not_before, not_after = gimmecert.crypto.get_validity_range()

    certificate = gimmecert.crypto.issue_certificate(issuer_dn, subject_dn, issuer_private_key, subject_private_key.public_key(), not_before, not_after)

    assert certificate.issuer == issuer_dn
    assert certificate.subject == subject_dn
    assert certificate.not_valid_before == not_before
    assert certificate.not_valid_after == not_after


def test_generate_ca_hierarchy_returns_list_with_3_elements_for_depth_3():
    base_name = 'My Project'
    depth = 3

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    assert isinstance(hierarchy, list)
    assert len(hierarchy) == depth


def test_generate_ca_hierarchy_returns_list_with_1_element_for_depth_1():
    base_name = 'My Project'
    depth = 1

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    assert isinstance(hierarchy, list)
    assert len(hierarchy) == depth


def test_generate_ca_hierarchy_returns_list_of_private_key_certificate_pairs():
    base_name = 'My Project'
    depth = 3

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    for private_key, certificate in hierarchy:
        assert isinstance(private_key, cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey)
        assert isinstance(certificate, cryptography.x509.Certificate)


def test_generate_ca_hierarchy_subject_dns_have_correct_value():
    base_name = 'My Project'
    depth = 3

    level1, level2, level3 = [certificate for _, certificate in gimmecert.crypto.generate_ca_hierarchy(base_name, depth)]

    assert level1.subject == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 1 CA'))
    assert level2.subject == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 2 CA'))
    assert level3.subject == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 3 CA'))


def test_generate_ca_hierarchy_issuer_dns_have_correct_value():
    base_name = 'My Project'
    depth = 3

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    level1_key, level1_certificate = hierarchy[0]
    level2_key, level2_certificate = hierarchy[1]
    level3_key, level3_certificate = hierarchy[2]

    assert level1_certificate.issuer == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 1 CA'))
    assert level2_certificate.issuer == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 1 CA'))
    assert level3_certificate.issuer == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 2 CA'))


def test_generate_ca_hierarchy_private_keys_match_with_public_keys_in_certificates():
    base_name = 'My Project'
    depth = 3

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    level1_private_key, level1_certificate = hierarchy[0]
    level2_private_key, level2_certificate = hierarchy[1]
    level3_private_key, level3_certificate = hierarchy[2]

    assert level1_private_key.public_key().public_numbers() == level1_certificate.public_key().public_numbers()
    assert level2_private_key.public_key().public_numbers() == level2_certificate.public_key().public_numbers()
    assert level3_private_key.public_key().public_numbers() == level3_certificate.public_key().public_numbers()


def test_generate_ca_hierarchy_cas_have_differing_keys():
    base_name = 'My Project'
    depth = 3

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    level1_private_key, _ = hierarchy[0]
    level2_private_key, _ = hierarchy[1]
    level3_private_key, _ = hierarchy[2]

    level1_public_numbers = level1_private_key.public_key().public_numbers()
    level2_public_numbers = level2_private_key.public_key().public_numbers()
    level3_public_numbers = level3_private_key.public_key().public_numbers()

    assert level1_public_numbers != level2_public_numbers
    assert level1_public_numbers != level3_public_numbers
    assert level2_public_numbers != level3_public_numbers


def test_generate_ca_hierarchy_certificates_have_same_validity():
    base_name = 'My Project'
    depth = 3

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    _, level1_certificate = hierarchy[0]
    _, level2_certificate = hierarchy[1]
    _, level3_certificate = hierarchy[2]

    assert level1_certificate.not_valid_before == level2_certificate.not_valid_before == level3_certificate.not_valid_before
    assert level1_certificate.not_valid_after == level2_certificate.not_valid_after == level3_certificate.not_valid_after


def test_issue_certificate_sets_extensions():
    dn = gimmecert.crypto.get_dn('My test 1')
    private_key = gimmecert.crypto.generate_private_key()
    not_before, not_after = gimmecert.crypto.get_validity_range()
    basic_constraints = cryptography.x509.BasicConstraints(ca=True, path_length=None)
    ocsp_no_check = cryptography.x509.OCSPNoCheck()
    extensions = [
        (basic_constraints, True),
        (ocsp_no_check, False),
    ]

    certificate = gimmecert.crypto.issue_certificate(dn, dn, private_key, private_key.public_key(), not_before, not_after, extensions)

    assert len(certificate.extensions) == 2

    stored_extension = certificate.extensions.get_extension_for_class(cryptography.x509.BasicConstraints)
    assert stored_extension.value == basic_constraints
    assert stored_extension.critical is True

    stored_extension = certificate.extensions.get_extension_for_class(cryptography.x509.OCSPNoCheck)
    assert stored_extension.critical is False
    assert isinstance(stored_extension.value, cryptography.x509.OCSPNoCheck)


def test_issue_certificate_sets_no_extensions_if_none_are_passed():
    dn = gimmecert.crypto.get_dn('My test 1')
    private_key = gimmecert.crypto.generate_private_key()
    not_before, not_after = gimmecert.crypto.get_validity_range()

    certificate1 = gimmecert.crypto.issue_certificate(dn, dn, private_key, private_key.public_key(), not_before, not_after, None)
    certificate2 = gimmecert.crypto.issue_certificate(dn, dn, private_key, private_key.public_key(), not_before, not_after, [])

    assert len(certificate1.extensions) == 0
    assert len(certificate2.extensions) == 0


def test_generate_ca_hierarchy_produces_certificates_with_ca_basic_constraints():
    base_name = 'My test'
    depth = 3

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    for _, certificate in hierarchy:
        stored_extension = certificate.extensions.get_extension_for_class(cryptography.x509.BasicConstraints)
        value, critical = stored_extension.value, stored_extension.critical

        assert isinstance(value, cryptography.x509.BasicConstraints)
        assert critical is True
        assert value.ca is True
        assert value.path_length is None


def test_issue_server_certificate_returns_certificate():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert isinstance(certificate, cryptography.x509.Certificate)


def test_issue_server_certificate_sets_correct_extensions():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    expected_basic_constraints = cryptography.x509.BasicConstraints(ca=False, path_length=None)
    expected_key_usage = cryptography.x509.KeyUsage(
        digital_signature=True,
        key_encipherment=True,
        content_commitment=False,
        data_encipherment=False,
        key_agreement=False,
        key_cert_sign=False,
        crl_sign=False,
        encipher_only=False,
        decipher_only=False
    )
    expected_extended_key_usage = cryptography.x509.ExtendedKeyUsage(
        [
            cryptography.x509.oid.ExtendedKeyUsageOID.SERVER_AUTH
        ]
    )
    expected_subject_alternative_name = cryptography.x509.SubjectAlternativeName(
        [
            cryptography.x509.DNSName('myserver')
        ]
    )

    certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert len(certificate.extensions) == 4
    assert certificate.extensions.get_extension_for_class(cryptography.x509.BasicConstraints).critical is True
    assert certificate.extensions.get_extension_for_class(cryptography.x509.BasicConstraints).value == expected_basic_constraints

    assert certificate.extensions.get_extension_for_class(cryptography.x509.KeyUsage).critical is True
    assert certificate.extensions.get_extension_for_class(cryptography.x509.KeyUsage).value == expected_key_usage

    assert certificate.extensions.get_extension_for_class(cryptography.x509.ExtendedKeyUsage).critical is True
    assert certificate.extensions.get_extension_for_class(cryptography.x509.ExtendedKeyUsage).value == expected_extended_key_usage

    assert certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).critical is False
    assert certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).value == expected_subject_alternative_name


def test_issue_server_certificate_has_correct_issuer_and_subject():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.issuer == issuer_certificate.subject
    assert certificate.subject == gimmecert.crypto.get_dn('myserver')


def test_issue_server_certificate_has_correct_public_key():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.public_key().public_numbers() == private_key.public_key().public_numbers()


@freeze_time('2018-01-01 00:15:00')
def test_issue_server_certificate_not_before_is_15_minutes_in_past():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.not_valid_before == datetime.datetime(2018, 1, 1, 0, 0)


def test_issue_server_certificate_not_before_does_not_exceed_ca_validity():
    with freeze_time('2018-01-01 00:15:00'):
        ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)

    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    with freeze_time(issuer_certificate.not_valid_before - datetime.timedelta(seconds=1)):
        certificate1 = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate1.not_valid_before == issuer_certificate.not_valid_before


def test_issue_server_certificate_not_after_does_not_exceed_ca_validity():
    with freeze_time('2018-01-01 00:15:00'):
        ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)

    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    with freeze_time(issuer_certificate.not_valid_after + datetime.timedelta(seconds=1)):
        certificate1 = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate1.not_valid_after == issuer_certificate.not_valid_after


def test_issue_server_certificate_incorporates_additional_dns_subject_alternative_names():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    expected_subject_alternative_name = cryptography.x509.SubjectAlternativeName(
        [
            cryptography.x509.DNSName('myserver'),
            cryptography.x509.DNSName('service.local'),
            cryptography.x509.DNSName('service.example.com')
        ]
    )

    extra_dns_names = ['service.local', 'service.example.com']
    certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate, extra_dns_names)

    assert certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).critical is False
    assert certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).value == expected_subject_alternative_name


def test_issue_client_certificate_returns_certificate():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    certificate = gimmecert.crypto.issue_client_certificate('myclient', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert isinstance(certificate, cryptography.x509.Certificate)


def test_issue_client_certificate_has_correct_issuer_and_subject():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    certificate = gimmecert.crypto.issue_client_certificate('myclient', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.issuer == issuer_certificate.subject
    assert certificate.subject == gimmecert.crypto.get_dn('myclient')


def test_issue_client_certificate_sets_correct_extensions():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    expected_basic_constraints = cryptography.x509.BasicConstraints(ca=False, path_length=None)
    expected_key_usage = cryptography.x509.KeyUsage(
        digital_signature=True,
        key_encipherment=True,
        content_commitment=False,
        data_encipherment=False,
        key_agreement=False,
        key_cert_sign=False,
        crl_sign=False,
        encipher_only=False,
        decipher_only=False
    )
    expected_extended_key_usage = cryptography.x509.ExtendedKeyUsage(
        [
            cryptography.x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH
        ]
    )

    certificate = gimmecert.crypto.issue_client_certificate('myclient', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert len(certificate.extensions) == 3
    assert certificate.extensions.get_extension_for_class(cryptography.x509.BasicConstraints).critical is True
    assert certificate.extensions.get_extension_for_class(cryptography.x509.BasicConstraints).value == expected_basic_constraints

    assert certificate.extensions.get_extension_for_class(cryptography.x509.KeyUsage).critical is True
    assert certificate.extensions.get_extension_for_class(cryptography.x509.KeyUsage).value == expected_key_usage

    assert certificate.extensions.get_extension_for_class(cryptography.x509.ExtendedKeyUsage).critical is True
    assert certificate.extensions.get_extension_for_class(cryptography.x509.ExtendedKeyUsage).value == expected_extended_key_usage


def test_issue_client_certificate_has_correct_public_key():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    certificate = gimmecert.crypto.issue_client_certificate('myclient', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.public_key().public_numbers() == private_key.public_key().public_numbers()


@freeze_time('2018-01-01 00:15:00')
def test_issue_client_certificate_not_before_is_15_minutes_in_past():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    certificate = gimmecert.crypto.issue_client_certificate('myclient', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.not_valid_before == datetime.datetime(2018, 1, 1, 0, 0)


def test_issue_client_certificate_not_before_does_not_exceed_ca_validity():
    with freeze_time('2018-01-01 00:15:00'):
        ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)

    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    with freeze_time(issuer_certificate.not_valid_before - datetime.timedelta(seconds=1)):
        certificate1 = gimmecert.crypto.issue_client_certificate('myclient', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate1.not_valid_before == issuer_certificate.not_valid_before


def test_issue_client_certificate_not_after_does_not_exceed_ca_validity():
    with freeze_time('2018-01-01 00:15:00'):
        ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)

    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()

    with freeze_time(issuer_certificate.not_valid_after + datetime.timedelta(seconds=1)):
        certificate1 = gimmecert.crypto.issue_client_certificate('myclient', private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate1.not_valid_after == issuer_certificate.not_valid_after


def test_renew_certificate_returns_certificate():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()
    old_certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    new_certificate = gimmecert.crypto.renew_certificate(old_certificate, private_key.public_key(), issuer_private_key, issuer_certificate)

    assert isinstance(new_certificate, cryptography.x509.Certificate)


def test_renew_certificate_has_correct_content():
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
    issuer_private_key, issuer_certificate = ca_hierarchy[0]

    private_key = gimmecert.crypto.generate_private_key()
    old_certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)
    public_key = gimmecert.crypto.generate_private_key().public_key()

    new_certificate = gimmecert.crypto.renew_certificate(old_certificate, public_key, issuer_private_key, issuer_certificate)

    assert old_certificate != new_certificate  # make sure we didn't get identical certificate.
    assert old_certificate.issuer == new_certificate.issuer
    assert old_certificate.subject == new_certificate.subject
    assert new_certificate.public_key().public_numbers() == public_key.public_numbers()
    assert [e for e in old_certificate.extensions] == [e for e in new_certificate.extensions]


def test_renew_certificate_not_before_is_15_minutes_in_past():

    # Initial server certificate.
    with freeze_time('2018-01-01 00:15:00'):
        ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
        issuer_private_key, issuer_certificate = ca_hierarchy[0]

        private_key = gimmecert.crypto.generate_private_key()
        old_certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    # Renew certificate.
    with freeze_time('2018-06-01 00:15:00'):
        certificate = gimmecert.crypto.renew_certificate(old_certificate, private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.not_valid_before == datetime.datetime(2018, 6, 1, 0, 0)


def test_renew_certificate_not_before_does_not_exceed_ca_validity():

    # Initial server certificate.
    with freeze_time('2018-01-01 00:15:00'):
        ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
        issuer_private_key, issuer_certificate = ca_hierarchy[0]

        private_key = gimmecert.crypto.generate_private_key()
        old_certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    # Renew certificate.
    with freeze_time(issuer_certificate.not_valid_before - datetime.timedelta(seconds=1)):
        certificate = gimmecert.crypto.renew_certificate(old_certificate, private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.not_valid_before == issuer_certificate.not_valid_before


def test_renew_certificate_not_after_does_not_exceed_ca_validity():

    # Initial server certificate.
    with freeze_time('2018-01-01 00:15:00'):
        ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy('My Project', 1)
        issuer_private_key, issuer_certificate = ca_hierarchy[0]

        private_key = gimmecert.crypto.generate_private_key()
        old_certificate = gimmecert.crypto.issue_server_certificate('myserver', private_key.public_key(), issuer_private_key, issuer_certificate)

    # Renew certificate.
    with freeze_time(issuer_certificate.not_valid_after + datetime.timedelta(seconds=1)):
        certificate = gimmecert.crypto.renew_certificate(old_certificate, private_key.public_key(), issuer_private_key, issuer_certificate)

    assert certificate.not_valid_after == issuer_certificate.not_valid_after


def test_generate_csr_returns_csr_with_passed_in_dn():

    private_key = gimmecert.crypto.generate_private_key()
    subject_dn = gimmecert.crypto.get_dn('testcsr')

    csr = gimmecert.crypto.generate_csr(subject_dn, private_key)

    assert isinstance(csr, cryptography.x509.CertificateSigningRequest)
    assert csr.public_key().public_numbers() == private_key.public_key().public_numbers()
    assert csr.subject == subject_dn


def test_generate_csr_returns_csr_with_passed_in_name():

    private_key = gimmecert.crypto.generate_private_key()
    name = 'testcsr'

    expected_subject_dn = gimmecert.crypto.get_dn('testcsr')

    csr = gimmecert.crypto.generate_csr(name, private_key)

    assert csr.public_key().public_numbers() == private_key.public_key().public_numbers()
    assert csr.subject == expected_subject_dn
