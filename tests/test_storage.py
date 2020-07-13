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
import io

import cryptography

import gimmecert.commands
import gimmecert.crypto
import gimmecert.storage
import gimmecert.utils

import pytest


def test_initialise_storage(tmpdir):
    tmpdir.chdir()

    gimmecert.storage.initialise_storage(tmpdir.strpath)

    assert os.path.exists(tmpdir.join('.gimmecert').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'ca').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'server').strpath)
    assert os.path.exists(tmpdir.join('.gimmecert', 'client').strpath)


@pytest.mark.parametrize("key_specification, key_type_representation", [
    [("rsa", 2048), "RSA"],
    [("ecdsa", cryptography.hazmat.primitives.asymmetric.ec.SECP192R1), "EC"],
])
def test_write_private_key(tmpdir, key_specification, key_type_representation):
    tmpdir.chdir()

    private_key = gimmecert.crypto.KeyGenerator(*key_specification)()
    key_path = tmpdir.join('test.key.pem').strpath

    gimmecert.storage.write_private_key(private_key, key_path)

    assert os.path.exists(key_path)

    with open(key_path, 'r') as key_file:
        content = key_file.read()
        assert 'BEGIN %s PRIVATE KEY' % key_type_representation in content
        assert 'END %s PRIVATE KEY' % key_type_representation in content


def test_write_certificate(tmpdir):
    tmpdir.chdir()

    issuer_dn = gimmecert.crypto.get_dn('My test 1')
    subject_dn = gimmecert.crypto.get_dn('My test 2')
    issuer_private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
    subject_private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
    not_before, not_after = gimmecert.crypto.get_validity_range()
    certificate = gimmecert.crypto.issue_certificate(issuer_dn, subject_dn, issuer_private_key, subject_private_key.public_key(), not_before, not_after)

    certificate_path = tmpdir.join('test.key.pem').strpath

    gimmecert.storage.write_certificate(certificate, certificate_path)

    assert os.path.exists(certificate_path)

    with open(certificate_path, 'r') as certificate_file:
        content = certificate_file.read()
        assert 'BEGIN CERTIFICATE' in content
        assert 'END CERTIFICATE' in content


def test_write_certificate_chain(tmpdir):
    output_file = tmpdir.join('chain.cert.pem')
    certificate_chain = [certificate for _, certificate in gimmecert.crypto.generate_ca_hierarchy('My Project', 3, gimmecert.crypto.KeyGenerator("rsa", 2048))]
    level1_pem, level2_pem, level3_pem = [gimmecert.utils.certificate_to_pem(certificate) for certificate in certificate_chain]

    gimmecert.storage.write_certificate_chain(certificate_chain, output_file.strpath)
    content = output_file.read(mode='r')
    expected_content = "%s\n%s\n%s" % (level1_pem, level2_pem, level3_pem)

    assert content == expected_content


def test_is_initialised_returns_true_if_directory_is_initialised(tmpdir):
    tmpdir.chdir()

    gimmecert.storage.initialise_storage(tmpdir.strpath)

    assert gimmecert.storage.is_initialised(tmpdir.strpath) is True


def test_is_initialised_returns_false_if_directory_is_not_initialised(tmpdir):
    tmpdir.chdir()

    assert gimmecert.storage.is_initialised(tmpdir.strpath) is False


@pytest.mark.parametrize("key_specification, private_key_instance_type", [
    [("rsa", 1024), cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey],
    [("ecdsa", cryptography.hazmat.primitives.asymmetric.ec.SECP192R1), cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey],
])
def test_read_ca_hierarchy_returns_list_of_ca_private_key_and_certificate_pairs_for_single_ca(tmpdir, key_specification, private_key_instance_type):
    tmpdir.chdir()
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, 'My Project', 1, key_specification)

    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(tmpdir.join('.gimmecert', 'ca').strpath)

    assert len(ca_hierarchy) == 1

    private_key, certificate = ca_hierarchy[0]

    assert isinstance(private_key, private_key_instance_type)
    assert isinstance(certificate, cryptography.x509.Certificate)


@pytest.mark.parametrize("key_specification, private_key_instance_type", [
    [("rsa", 1024), cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey],
    [("ecdsa", cryptography.hazmat.primitives.asymmetric.ec.SECP192R1), cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey],
])
def test_read_private_key_returns_private_key(tmpdir, key_specification, private_key_instance_type):
    private_key_path = tmpdir.join('private.key.pem').strpath
    private_key = gimmecert.crypto.KeyGenerator(*key_specification)()
    gimmecert.storage.write_private_key(private_key, private_key_path)

    my_private_key = gimmecert.storage.read_private_key(private_key_path)

    assert isinstance(my_private_key, private_key_instance_type)
    assert my_private_key.public_key().public_numbers() == private_key.public_key().public_numbers()  # Can't compare private keys directly.


def test_read_certificate_returns_certificate(tmpdir):
    certificate_path = tmpdir.join('certificate.cert.pem').strpath
    dn = gimmecert.crypto.get_dn('mycertificate')
    not_before, not_after = gimmecert.crypto.get_validity_range()

    private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
    certificate = gimmecert.crypto.issue_certificate(dn, dn, private_key, private_key.public_key(), not_before, not_after)
    gimmecert.storage.write_certificate(certificate, certificate_path)

    my_certificate = gimmecert.storage.read_certificate(certificate_path)

    assert isinstance(my_certificate, cryptography.x509.Certificate)
    assert my_certificate == certificate


@pytest.mark.parametrize("key_specification, private_key_instance_type", [
    [("rsa", 1024), cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey],
    [("ecdsa", cryptography.hazmat.primitives.asymmetric.ec.SECP192R1), cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey],
])
def test_read_ca_hierarchy_returns_list_of_ca_private_key_and_certificate_pairs_in_hierarchy_order_for_multiple_cas(tmpdir, key_specification,
                                                                                                                    private_key_instance_type):
    tmpdir.chdir()
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, 'My Project', 4, key_specification)

    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(tmpdir.join('.gimmecert', 'ca').strpath)

    assert len(ca_hierarchy) == 4

    private_key_1, certificate_1 = ca_hierarchy[0]
    private_key_2, certificate_2 = ca_hierarchy[1]
    private_key_3, certificate_3 = ca_hierarchy[2]
    private_key_4, certificate_4 = ca_hierarchy[3]

    assert isinstance(private_key_1, private_key_instance_type)
    assert isinstance(certificate_1, cryptography.x509.Certificate)
    assert certificate_1.subject == gimmecert.crypto.get_dn("My Project Level 1 CA")
    assert isinstance(private_key_2, private_key_instance_type)
    assert isinstance(certificate_2, cryptography.x509.Certificate)
    assert certificate_2.subject == gimmecert.crypto.get_dn("My Project Level 2 CA")
    assert isinstance(private_key_3, private_key_instance_type)
    assert isinstance(certificate_3, cryptography.x509.Certificate)
    assert certificate_3.subject == gimmecert.crypto.get_dn("My Project Level 3 CA")
    assert isinstance(private_key_4, private_key_instance_type)
    assert isinstance(certificate_4, cryptography.x509.Certificate)
    assert certificate_4.subject == gimmecert.crypto.get_dn("My Project Level 4 CA")


def test_write_csr(tmpdir):
    csr_file = tmpdir.join('test.csr.pem')

    private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
    csr = gimmecert.crypto.generate_csr('test', private_key)

    gimmecert.storage.write_csr(csr, csr_file.strpath)

    csr_file_content = csr_file.read()

    assert os.path.exists(csr_file.strpath)
    assert csr_file_content.startswith('-----BEGIN CERTIFICATE REQUEST-----')
    assert csr_file_content.endswith('-----END CERTIFICATE REQUEST-----\n')


def test_read_csr(tmpdir):
    csr_file = tmpdir.join('mycsr.csr.pem')

    private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
    original_csr = gimmecert.crypto.generate_csr('mycsr', private_key)

    gimmecert.storage.write_csr(original_csr, csr_file.strpath)

    csr = gimmecert.storage.read_csr(csr_file.strpath)

    assert isinstance(csr, cryptography.x509.CertificateSigningRequest)
    assert csr == original_csr
