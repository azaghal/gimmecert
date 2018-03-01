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


import cryptography.hazmat


def certificate_to_pem(certificate):
    """
    Converts certificate object to OpenSSL-style PEM format.

    :param certificate: Certificate that should be convered to OpenSSL-style PEM format.
    :type certificate: cryptography.x509.Certificate

    :returns: Certificate in OpenSSL-style PEM format.
    :rtype: bytes
    """

    certificate_pem = certificate.public_bytes(encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM)

    return certificate_pem
