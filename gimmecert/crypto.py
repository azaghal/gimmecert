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


class KeyGenerator:
    """
    Provides abstract factory-like interface for generating private
    keys. Algorithm and parameters for the private key are provided
    during instance initialisation by passing-in a specification.

    Instances are callable objects that generate and return the
    private key according to key specification passed-in during the
    instance initialisation.
    """

    def __init__(self, algorithm, parameters):
        """
        Initialises an instance.

        :param algorithm: Algorithm to use. Supported algorithms: 'rsa', 'ecdsa'.
        :type algorithm: str

        :param parameters: Parameters for generating the keys using the specified algorithm. For RSA keys this is key size.
                           For ECDSA, this is an instance of cryptography.hazmat.primitives.asymmetric.ec.EllipticCurve.
        :type parameters: int or cryptography.hazmat.primitives.asymmetric.ec.EllipticCurve
        """

        self._algorithm = algorithm
        self._parameters = parameters

    def __str__(self):
        """
        Returns string (human-readable) representation of stored algorithm
        and parameters.

        :returns: String representation of object.
        :rtype: str
        """

        if self._algorithm == "rsa":

            return "%d-bit RSA" % self._parameters

        elif self._algorithm == "ecdsa":

            return "%s ECDSA" % self._parameters.name

    def __call__(self):
        """
        Generates private key. Key algorithm and parameters are
        deterimened by instance's key specification (passed-in during
        instance creation).

        :returns: Private key.
        :rtype: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey
        """

        if self._algorithm == "rsa":

            rsa_public_exponent = 65537

            private_key = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
                public_exponent=rsa_public_exponent,
                key_size=self._parameters,
                backend=cryptography.hazmat.backends.default_backend()
            )
        else:
            private_key = cryptography.hazmat.primitives.asymmetric.ec.generate_private_key(
                curve=self._parameters,
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


def issue_certificate(issuer_dn, subject_dn, signing_key, public_key, not_before, not_after, extensions=None):
    """
    Issues a certificate using the passed-in data.

    :param issuer_dn: Issuer DN to use in issued certificate.
    :type issuer_dn: cryptography.x509.Name

    :param subject_dn: Subject DN to use in issued certificate.
    :type subject_dn: cryptography.x509.Name

    :param signing_key: Private key belonging to entity associated with passed-in issuer_dn. Used for signing the certificate data.
    :type signing_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                       cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey

    :param public_key: Public key belonging to entity associated with passed-in subject_dn. Used as part of certificate to denote its owner.
    :type public_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey or
                      cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey

    :param not_before: Beginning of certifiate validity.
    :type datetime.datetime.:

    :param not_after: End of certificate validity.
    :type datetime.datetime:

    :param extensions: List of certificate extensions with their criticality to add to resulting certificate object. List of (extension, criticality) pairs.
    :type extensions: list[(cryptography.x509.Extension, bool)]

    :returns: Issued certificate with requested content.
    :rtype: cryptography.x509.Certificate
    """

    if extensions is None:
        extensions = []

    builder = cryptography.x509.CertificateBuilder()
    builder = builder.subject_name(cryptography.x509.Name(subject_dn))
    builder = builder.issuer_name(cryptography.x509.Name(issuer_dn))
    builder = builder.not_valid_before(not_before)
    builder = builder.not_valid_after(not_after)
    builder = builder.serial_number(cryptography.x509.random_serial_number())
    builder = builder.public_key(public_key)

    for extension in extensions:
        builder = builder.add_extension(extension[0], critical=extension[1])

    certificate = builder.sign(
        private_key=signing_key,
        algorithm=cryptography.hazmat.primitives.hashes.SHA256(),
        backend=cryptography.hazmat.backends.default_backend()
    )

    return certificate


def generate_ca_hierarchy(base_name, depth, key_generator):
    """
    Generates CA hierarchy with specified depth, using the provided
    naming as basis for the DNs.

    :param base_name: Base name for constructing the CA DNs. Resulting DNs are of format 'BASE Level N'.
    :type base_name: str

    :param key_generator: Callable for generating private keys.
    :type key_generator: callable[[], cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                                      cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey]

    :returns: List of CA private key and certificate pairs, starting with the level 1 (root) CA, and ending with the leaf CA.
    :rtype: list[(cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                  cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey, cryptography.x509.Certificate)]
    """

    hierarchy = []

    not_before, not_after = get_validity_range()

    extensions = [
        (cryptography.x509.BasicConstraints(ca=True, path_length=None), True)
    ]

    # We have not issued yet any certificate.
    issuer_dn = None
    issuer_private_key = None

    for level in range(1, depth+1):
        # Generate info for the new CA.
        dn = get_dn("%s Level %d CA" % (base_name, level))
        private_key = key_generator()

        # First certificate issued needs to be self-signed.
        issuer_dn = issuer_dn or dn
        issuer_private_key = issuer_private_key or private_key

        certificate = issue_certificate(issuer_dn, dn, issuer_private_key, private_key.public_key(), not_before, not_after, extensions)
        hierarchy.append((private_key, certificate))

        # Current entity becomes issuer for next one in chain.
        issuer_dn, issuer_private_key = dn, private_key

    return hierarchy


def issue_server_certificate(name, public_key, issuer_private_key, issuer_certificate, extra_dns_names=None):
    """
    Issues a server certificate. The resulting certificate will use
    the passed-in name for subject DN, as well as DNS subject
    alternative name.

    The server certificate key usages and extended key usages are set
    to comply with requirements for using such certificates as TLS
    server certificates.

    Server certificate validity will not exceed the CA validity.

    :param name: Name of the server end entity. Name will be part of subject DN CN field.
    :type name: str

    :param public_key: Public key of the server end entity.
    :type public_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey or
                      cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey

    :param issuer_private_key: Private key of the issuer to use for signing the server certificate structure.
    :type issuer_private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                              cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey

    :param issuer_certificate: Certificate of certificate issuer. Naming and validity constraints will be applied based on its content.
    :type issuer_certificate: cryptography.x509.Certificate

    :param extra_dns_names: Additional DNS names to include in subject alternative name. Set to None (default) to not include anything.
    :type extra_dns_names: list[str] or None

    :returns: Server certificate issued by designated issuer.
    :rtype: cryptography.x509.Certificate
    """

    dns_names = [name]

    if extra_dns_names is not None:
        dns_names.extend(extra_dns_names)

    dn = get_dn(name)
    not_before, not_after = get_validity_range()
    extensions = [
        (cryptography.x509.BasicConstraints(ca=False, path_length=None), True),
        (
            cryptography.x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ), True
        ),
        (cryptography.x509.ExtendedKeyUsage([cryptography.x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), True),
        (cryptography.x509.SubjectAlternativeName([cryptography.x509.DNSName(dns_name) for dns_name in dns_names]), False)
    ]

    if not_before < issuer_certificate.not_valid_before:
        not_before = issuer_certificate.not_valid_before

    if not_after > issuer_certificate.not_valid_after:
        not_after = issuer_certificate.not_valid_after

    certificate = issue_certificate(issuer_certificate.subject, dn, issuer_private_key, public_key, not_before, not_after, extensions)

    return certificate


def issue_client_certificate(name, public_key, issuer_private_key, issuer_certificate):
    """
    Issues a client certificate. The resulting certificate will use
    the passed-in name for subject DN.

    The client certificate key usages and extended key usages are set
    to comply with requirements for using such certificates as TLS
    server certificates.

    Client certificate validity will not exceed the CA validity.

    :param name: Name of the client end entity. Name will be part of subject DN CN field.
    :type name: str

    :param public_key: Public key of the server end entity.
    :type public_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey or
                      cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey

    :param issuer_private_key: Private key of the issuer to use for signing the client certificate structure.
    :type issuer_private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                              cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey

    :param issuer_certificate: Certificate of certificate issuer. Naming and validity constraints will be applied based on its content.
    :type issuer_certificate: cryptography.x509.Certificate

    :returns: Client certificate issued by designated issuer.
    :rtype: cryptography.x509.Certificate
    """

    dn = get_dn(name)
    not_before, not_after = get_validity_range()
    extensions = [
        (cryptography.x509.BasicConstraints(ca=False, path_length=None), True),
        (
            cryptography.x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ), True
        ),
        (cryptography.x509.ExtendedKeyUsage([cryptography.x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]), True),
    ]

    if not_before < issuer_certificate.not_valid_before:
        not_before = issuer_certificate.not_valid_before

    if not_after > issuer_certificate.not_valid_after:
        not_after = issuer_certificate.not_valid_after

    certificate = issue_certificate(issuer_certificate.subject, dn, issuer_private_key, public_key, not_before, not_after, extensions)

    return certificate


def renew_certificate(old_certificate, public_key, issuer_private_key, issuer_certificate):
    """
    Renews an existing certificate, while preserving issuer and
    subject DNs, as well as extensions from the old certificate.

    :param old_certificate: Previously issued certificate.
    :type old_certificate: cryptography.x509.Certificate

    :param public_key: Public key to use in resulting certificate. Allows replacement of public key in new certificate.
    :type public_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey or
                      cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey

    :param issuer_private_key: Private key of the issuer to use for signing the certificate structure.
    :type issuer_private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                              cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey

    :param issuer_certificate: Certificate of certificate issuer. Naming and validity constraints will be applied based on its content.
    :type issuer_certificate: cryptography.x509.Certificate

    :returns: New certificate, which preserves naming, extensions, and public key of the old one.
    :rtype: cryptography.x509.Certificate
    """

    not_before, not_after = get_validity_range()

    if not_before < issuer_certificate.not_valid_before:
        not_before = issuer_certificate.not_valid_before

    if not_after > issuer_certificate.not_valid_after:
        not_after = issuer_certificate.not_valid_after

    new_certificate = issue_certificate(issuer_certificate.subject,
                                        old_certificate.subject,
                                        issuer_private_key,
                                        public_key,
                                        not_before,
                                        not_after,
                                        [(e.value, e.critical) for e in old_certificate.extensions])

    return new_certificate


def generate_csr(name, private_key):
    """
    Generates certificate signing request.

    :param name: Name of the end entity. If string, passed-in name is treated as value for CN in subject DN.
    :type name: str or cryptography.x509.Name

    :param private_key: Private key of end entity to use for signing the CSR.
    :type private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                       cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey

    :returns: Certificate signing request with specified naming signed with passed-in private key.
    :rtype: cryptography.x509.CertificateSigningRequest
    """

    if isinstance(name, cryptography.x509.Name):
        subject_dn = name
    else:
        subject_dn = get_dn(name)

    builder = cryptography.x509.CertificateSigningRequestBuilder()
    builder = builder.subject_name(subject_dn)

    csr = builder.sign(
        private_key,
        cryptography.hazmat.primitives.hashes.SHA256(),
        cryptography.hazmat.backends.default_backend()
    )

    return csr


def key_specification_from_public_key(public_key):
    """
    Derives key specification (algorithm and associated parameters)
    from the passed-in public key. Key specification can be used for
    generating the private keys via KeyGenerator instances.

    :param public_key: Public key from which to derive the key specification.
    :type public_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey or
                      cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey

    :returns: Key algorithm and parameter(s) for generating same type of keys as the passed-in public key.
    :rtype: tuple(str, int) or cryptography.hazmat.primitives.asymmetric.ec.EllipticCurve)

    :raises ValueError: If algorithm/parameters could not be derived from the passed-in public key.
    """

    if isinstance(public_key, cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey):
        return "rsa", public_key.key_size
    elif isinstance(public_key, cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey):
        return "ecdsa", type(public_key.curve)

    raise ValueError("Unsupported public key instance passed-in: \"%s\" (%s)" % (str(public_key), type(public_key)))
