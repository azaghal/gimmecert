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

    assert level1.subject == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 1'))
    assert level2.subject == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 2'))
    assert level3.subject == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 3'))


def test_generate_ca_hierarchy_issuer_dns_have_correct_value():
    base_name = 'My Project'
    depth = 3

    hierarchy = gimmecert.crypto.generate_ca_hierarchy(base_name, depth)

    level1_key, level1_certificate = hierarchy[0]
    level2_key, level2_certificate = hierarchy[1]
    level3_key, level3_certificate = hierarchy[2]

    assert level1_certificate.issuer == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 1'))
    assert level2_certificate.issuer == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 1'))
    assert level3_certificate.issuer == cryptography.x509.Name(gimmecert.crypto.get_dn('My Project Level 2'))


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
