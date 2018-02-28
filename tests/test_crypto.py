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
