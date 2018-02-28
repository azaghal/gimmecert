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


def generate_private_key():
    """
    Generates a 2048-bit RSA private key.

    :returns: RSA private key.
    :rtype: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey
    """

    rsa_public_exponent = 65537
    key_size = 2048

    private_key = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
        public_exponent=rsa_public_exponent,
        key_size=key_size,
        backend=cryptography.hazmat.backends.default_backend()
    )

    return private_key


def get_dn(name):
    """
    Generates a DN (distinguished name) using the passed-in name. The
    resulting DN will consist out of a single CN field, whose value
    will be set to the passed-in name. For example, if you pass-in
    name "My Name", the resulting DN will be "CN=My Name".

    :returns: Distinguished name with provided value.
    :rtype: cryptography.x509.Name
    """

    dn = cryptography.x509.Name([cryptography.x509.NameAttribute(cryptography.x509.oid.NameOID.COMMON_NAME, name)])

    return dn


def get_validity_range():
    """
    Returns validity range usable for issuing certificates. The time
    range between beginning and end is one year.

    The beginning will be current time minus 15 minutes (useful in
    case of drifting clocks), while ending will be one year ahead of
    15 minutes - for total duration of 1 year and 15 minutes.

    Resulting beginning and ending dates have precision of up to a
    second (microseconds are discarded).

    :returns: (not_before, not_after) -- Tuple defining the time range.
    :rtype: (datetime.datetime, datetime.datetime)
    """

    now = datetime.datetime.utcnow().replace(microsecond=0)
    not_before = now - datetime.timedelta(minutes=15)
    not_after = now + relativedelta(years=1)

    return not_before, not_after


def issue_certificate(issuer_dn, subject_dn, signing_key, public_key, not_before, not_after):
    """
    Issues a certificate using the passed-in data.

    :param issuer_dn: Issuer DN to use in issued certificate.
    :type issuer_dn: cryptography.x509.Name

    :param subject_dn: Subject DN to use in issued certificate.
    :type subject_dn: cryptography.x509.Name

    :param signing_key: Private key belonging to entity associated with passed-in issuer_dn. Used for signing the certificate data.
    :type signing_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey

    :param public_key: Public key belonging to entity associated with passed-in subject_dn. Used as part of certificate to denote its owner.
    :type cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey:

    :param not_before: Beginning of certifiate validity.
    :type datetime.datetime.:

    :param not_after: End of certificate validity.
    :type datetime.datetime:
    """

    builder = cryptography.x509.CertificateBuilder()
    builder = builder.subject_name(cryptography.x509.Name(subject_dn))
    builder = builder.issuer_name(cryptography.x509.Name(issuer_dn))
    builder = builder.not_valid_before(not_before)
    builder = builder.not_valid_after(not_after)
    builder = builder.serial_number(cryptography.x509.random_serial_number())
    builder = builder.public_key(public_key)

    certificate = builder.sign(
        private_key=signing_key,
        algorithm=cryptography.hazmat.primitives.hashes.SHA256(),
        backend=cryptography.hazmat.backends.default_backend()
    )

    return certificate
