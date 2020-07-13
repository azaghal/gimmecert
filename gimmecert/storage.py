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

import cryptography.x509
import cryptography.hazmat.primitives.serialization

import gimmecert.utils


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
    os.mkdir(os.path.join(project_directory, '.gimmecert', 'server'))
    os.mkdir(os.path.join(project_directory, '.gimmecert', 'client'))


def write_private_key(private_key, path):
    """
    Writes the passed-in private key to designated path in
    OpenSSL-style PEM format.

    The private key is written without any encryption.

    :param private_key: Private key that should be written.
    :type private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                       cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey

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


def write_certificate_chain(certificate_chain, path):
    """
    Writes the passed-in certificate chain to designated path in
    OpenSSL-style PEM format. Certificates are separated with
    newlines.

    :param certificate_chain: List of certificates to output to the file.
    :type certificate_chain: list[cryptography.x509.Certificate]

    :param path: File path where the chain should be written.
    :type path: str
    """

    chain_pem = "\n".join(
        [gimmecert.utils.certificate_to_pem(certificate) for certificate in certificate_chain]
    )

    with open(path, 'w') as certificate_chain_file:
        certificate_chain_file.write(chain_pem)


def is_initialised(project_directory):
    """
    Checks if Gimmecert has been initialised in designated project
    directory.

    :param project_directory: Path to project directory to check.
    :type project_directory: str
    """

    if os.path.exists(os.path.join(project_directory, '.gimmecert')):
        return True

    return False


def read_ca_hierarchy(ca_directory):
    """
    Reads an entirye CA hierarchy from the directory, and returns the
    CA private key/certificate pairs in hierarchy order.

    Only private key and certificate files that conform to naming
    pattern 'levelN.key.pem' and 'levelN.cert.pem' will be read.

    :param ca_directory: Path to directory containing the CA artifacts (private keys and certificates).
    :type ca_directory: str

    :returns: List of private key/certificate pairs, starting with the level 1 CA and moving down the chain to leaf CA.
    :rtype: list[(cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                  cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey, cryptography.x509.Certificate)]
    """

    ca_hierarchy = []

    level = 1
    while os.path.exists(os.path.join(ca_directory, "level%d.key.pem" % level)) and os.path.exists(os.path.join(ca_directory, "level%d.cert.pem" % level)):
        private_key = read_private_key(os.path.join(ca_directory, 'level%d.key.pem' % level))
        certificate = read_certificate(os.path.join(ca_directory, 'level%d.cert.pem' % level))
        ca_hierarchy.append((private_key, certificate))
        level = level + 1

    return ca_hierarchy


def read_private_key(private_key_path):
    """
    Reads RSA private key from the designated path. The key should be
    provided in OpenSSL-style PEM format, unencrypted.

    :param private_key_path: Path to private key to read.
    :type private_key_path: str

    :returns: Private key object read from the specified file.
    :rtype: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
            cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey
    """

    with open(private_key_path, 'rb') as private_key_file:
        private_key = cryptography.hazmat.primitives.serialization.load_pem_private_key(
            private_key_file.read(),
            None,  # no password
            cryptography.hazmat.backends.default_backend()
        )

    return private_key


def read_certificate(certificate_path):
    """
    Reads X.509 certificate from the designated file path. The
    certificate is expected to be provided in OpenSSL-style PEM
    format.

    :param certificate_path: Path to certificate file.
    :type certificate_path: str

    :returns: Certificate object read from the specified file.
    :rtype: cryptography.x509.Certificate
    """
    with open(certificate_path, 'rb') as certificate_file:
        certificate = cryptography.x509.load_pem_x509_certificate(
            certificate_file.read(),
            cryptography.hazmat.backends.default_backend()
        )

    return certificate


def write_csr(csr, path):
    """
    Writes the passed-in certificate signing request to designated
    path in OpenSSL-style PEM format.

    :param certificate: CSR that should be writtent-out.
    :type certificate: cryptography.x509.CertificateSigningRequest

    :param path: File path where the CSR should be written.
    :type path: str
    """

    csr_pem = csr.public_bytes(encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM)

    with open(path, 'wb') as csr_file:
        csr_file.write(csr_pem)


def read_csr(csr_path):
    """
    Reads X.509 certificate signing request from the designated file
    path. The CSR is expected to be provided in OpenSSL-style PEM
    format.

    :param csr_path: Path to CSR file.
    :type csr_path: str

    :returns: CSR object read from the specified file.
    :rtype: cryptography.x509.CertificateSigningRequest
    """

    with open(csr_path, 'rb') as csr_file:
        csr = cryptography.x509.load_pem_x509_csr(
            csr_file.read(),
            cryptography.hazmat.backends.default_backend()
        )

    return csr
