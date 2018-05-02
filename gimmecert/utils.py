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


class UnsupportedField(Exception):
    """
    Exception thrown when trying to process an unsupported field in
    subject or issuer DN.
    """
    pass


def certificate_to_pem(certificate):
    """
    Converts certificate object to OpenSSL-style PEM format.

    :param certificate: Certificate that should be convered to OpenSSL-style PEM format.
    :type certificate: cryptography.x509.Certificate

    :returns: Certificate in OpenSSL-style PEM format.
    :rtype: str
    """

    certificate_pem = certificate.public_bytes(encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM)

    return certificate_pem.decode()


def dn_to_str(dn):
    """
    Converts passed-in DN to a human-readable OpenSSL-style string
    representation.

    Currently supported fields:

    - Common name.

    :param dn: DN for which to generate string representation.
    :type dn: cryptography.x509.Name

    :returns: OpenSSL-style string representation of passed-in DN.
    :rtype: str
    """

    fields = []

    for field in dn:
        if field.oid == cryptography.x509.oid.NameOID.COMMON_NAME:
            fields.append("CN=%s" % field.value)
        else:
            raise UnsupportedField("Unable to generate string representation for: %s" % field.oid)

    return ",".join(fields)


def date_range_to_str(start, end):
    """
    Converts the provided validity range (with starting and end date),
    into a human-readable string.

    :param begin: Start date in UTC.
    :type begin: datetime.datetime

    :param end: End date in UTC.
    :type end: datetime.datetime

    :returns: String representation of date range, up to a second granularity.
    :rtype: str
    """

    date_format = "%Y-%m-%d %H:%M:%S UTC"

    return "%s - %s" % (start.strftime(date_format), end.strftime(date_format))


def get_dns_names(certificate):
    """
    Retrieves list of DNS subject alternative names from certificate.

    :param certificate: Certificate to process.
    :type certificate: cryptography.x509.Certificate

    :returns: List of DNS subject alternative names extracted from the certificate.
    :rtype: list[str]
    """

    try:
        subject_alternative_name = certificate.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName).value
        dns_names = subject_alternative_name.get_values_for_type(cryptography.x509.DNSName)
    except cryptography.x509.extensions.ExtensionNotFound:
        dns_names = []

    return dns_names


def read_input(input_stream, prompt_stream, prompt):
    """
    Reads input from the passed-in input stream until Ctrl-D sequence
    is reached, while also providing a meaningful prompt to the user.

    The prompt will be extended with short information telling the
    user to end input with Ctrl-D.

    :param input_stream: Input stream to read from.
    :type input_stream: io.IOBase

    :param prompt_stream: Output stream where the prompt should be written-out.
    :type prompt_stream: io.IOBase

    :param prompt: Prompt message to show to the user.
    :type prompt: str
    """

    print("%s (finish with Ctrl-D on an empty line):\n" % prompt, file=prompt_stream)

    user_input = ""

    c = input_stream.read(1)
    while c != '':
        user_input += c
        c = input_stream.read(1)

    return user_input


def csr_from_pem(csr_pem):
    """
    Converts passed-in CSR in OpenSSL-style PEM format into a CSR
    object.

    :param csr_pem: CSR in OpenSSL-style PEM format.
    :type csr_pem: str

    :returns: CSR object.
    :rtype: cryptography.x509.CertificateSigningRequest
    """

    csr = cryptography.x509.load_pem_x509_csr(
        bytes(csr_pem, encoding='utf8'),
        cryptography.hazmat.backends.default_backend()
    )

    return csr
