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

import cryptography.hazmat.primitives.serialization


def initialise_storage(project_directory):
    """
    Initialises certificate storage in the given project directory.

    Storage initialisation consists of creating the necessary
    directory structure. Directories created under the passed-in
    project directory are:

    - .gimmcert/
    - .gimmcert/ca/

    :param project_directory: Path to directory under which the storage should be initialised.
    :type project_directory: str
    """

    os.mkdir(os.path.join(project_directory, '.gimmecert'))
    os.mkdir(os.path.join(project_directory, '.gimmecert', 'ca'))


def write_private_key(private_key, path):
    """
    Writes the passed-in private key to designated path in
    OpenSSL-style PEM format.

    The private key is written without any encryption.

    :param private_key: Private key that should be written.
    :type private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey

    :param path: File path where the key should be written.
    :type path: str
    """

    private_key_pem = private_key.private_bytes(
        encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
        format=cryptography.hazmat.primitives.serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=cryptography.hazmat.primitives.serialization.NoEncryption()
    )

    with open(path, 'wb') as key_file:
        key_file.write(private_key_pem)


def write_certificate(certificate, path):
    """
    Writes the passed-in certificate to designated path in
    OpenSSL-style PEM format.

    :param certificate: Certificate that should be writtent-out.
    :type certificate: cryptography.x509.Certificate

    :param path: File path where the certificate should be written.
    :type path: str
    """

    certificate_pem = certificate.public_bytes(encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM)

    with open(path, 'wb') as certificate_file:
        certificate_file.write(certificate_pem)
