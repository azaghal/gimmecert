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


import collections
import io

import gimmecert
import gimmecert.crypto
import gimmecert.storage

import pytest


@pytest.fixture
def key_with_csr(tmpdir):
    """
    Fixture that generates a private key and CSR within tmpdir, and
    provides information about them.

    The following artefacts are generated in the directory:

        - custom_csr/mycustom.key.pem (private key in OpenSSL-style PEM format)
        - custom_csr/mycustom.csr.pem (CSR in OpenSSL-style PEM format)

    :param tmpdir: Temporary directory (normally pytest tmpdir fixture) created for running the test.
    :type tmpdir: py.path.local

    :returns: Named tuple that describes the generated private key and CSR. The following properties are made available:
      private_key (cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey) - private key object.
      private_key_path (str) - path to generated private key.
      private_key_pem (str) - private key in OpenSSL-style PEM format.
      csr (cryptography.x509.CertificateSigningRequest) - CSR object.
      csr_path (str) - path to generated CSR.
      csr_pem (str) - CSR in OpenSSL-style PEM format.
    :rtype: collections.namedtuple
    """

    # Convenience named tuple for accessing generated artefacts.
    TestKeyWithCSR = collections.namedtuple('TestKeyWithCSR', 'private_key, private_key_path, private_key_pem, csr, csr_path, csr_pem')

    # Set-up directory for holding custom CSRs.
    custom_csr_dir = tmpdir.ensure('custom_csr', dir=True)

    # Set-up naming and some files.
    name = "mycustom"
    private_key_file = custom_csr_dir.join("%s.key.pem" % name)
    csr_file = custom_csr_dir.join("%s.csr.pem" % name)

    # Generate private key and CSR, and output them.
    private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
    csr = gimmecert.crypto.generate_csr(name, private_key)

    gimmecert.storage.write_private_key(private_key, private_key_file.strpath)
    gimmecert.storage.write_csr(csr, csr_file.strpath)

    private_key_pem = private_key_file.read()
    csr_pem = csr_file.read()

    return TestKeyWithCSR(private_key, private_key_file.strpath, private_key_pem, csr, csr_file.strpath, csr_pem)


@pytest.fixture
def sample_project_directory(tmpdir):
    """
    Fixture that initialises a sample Gimmecert project within tmpdir,
    and issues a couple of client and server certificates using
    different methods (internal private key generation + issuance via
    CSR).

    Initialised CA hierarchy is 1 level deep, with basename used being
    identical to temporary directory base name, and it uses 2048-bit
    RSA keys.

    The following server certificates are issued:

        - server-with-csr-1 (server certificate, issued using custom CSR)
        - server-with-csr-2 (server certificate, issued using custom CSR)
        - server-with-privkey-1 (server certificate, Gimmecert-generated private key)
        - server-with-privkey-2 (server certificate, Gimmecert-generated private key)
        - client-with-csr-1 (client certificate, issued using custom CSR)
        - client-with-csr-2 (client certificate, issued using custom CSR)
        - client-with-privkey-1 (client certificate, Gimmecert-generated private key)
        - client-with-privkey-2 (client certificate, Gimmecert-generated private key)

    The following artefacts are created "external" to Gimmecert
    standard usage, mainly for the purpose of issuing certificates
    using CSR:

        - custom_csr/server-with-csr-1.key.pem (private key in OpenSSL-style PEM format, generated for creating CSR for issuing server-with-csr-1 certificate)
        - custom_csr/server-with-csr-1.csr.pem (CSR in OpenSSL-style PEM format, used for issuing sever-with-csr-1 certificate)
        - custom_csr/server-with-csr-2.key.pem (private key in OpenSSL-style PEM format, generated for creating CSR for issuing server-with-csr-2 certificate)
        - custom_csr/server-with-csr-2.csr.pem (CSR in OpenSSL-style PEM format, used for issuing sever-with-csr-2 certificate)
        - custom_csr/client-with-csr-1.key.pem (private key in OpenSSL-style PEM format, generated for creating CSR for issuing client-with-csr-1 certificate)
        - custom_csr/client-with-csr-1.csr.pem (CSR in OpenSSL-style PEM format, used for issuing sever-with-csr-1 certificate)
        - custom_csr/client-with-csr-2.key.pem (private key in OpenSSL-style PEM format, generated for creating CSR for issuing client-with-csr-2 certificate)
        - custom_csr/client-with-csr-2.csr.pem (CSR in OpenSSL-style PEM format, used for issuing sever-with-csr-2 certificate)

    :param tmpdir: Temporary directory (normally pytest tmpdir fixture) created for running the test.
    :type tmpdir: py.path.local

    :returs: Parent directory where Gimmecert has been initialised. Essentially the tmpdir fixture.
    :rtype: py.path.local
    """

    # Total amount of each type certificate to issue.
    per_type_count = 2

    # Set-up directory for holding custom CSRs.
    custom_csr_dir = tmpdir.ensure('custom_csr', dir=True)

    # Set-up some custom CSRs.
    for i in range(1, per_type_count + 1):
        # Used in generated samples.
        name = "server-with-csr-%d" % i
        private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
        csr = gimmecert.crypto.generate_csr(name, private_key)
        gimmecert.storage.write_private_key(private_key, custom_csr_dir.join("%s.key.pem" % name).strpath)
        gimmecert.storage.write_csr(csr, custom_csr_dir.join("%s.csr.pem" % name).strpath)

        # Used in generated samples.
        name = "client-with-csr-%d" % i
        private_key = gimmecert.crypto.KeyGenerator('rsa', 2048)()
        csr = gimmecert.crypto.generate_csr(name, private_key)
        gimmecert.storage.write_private_key(private_key, custom_csr_dir.join("%s.key.pem" % name).strpath)
        gimmecert.storage.write_csr(csr, custom_csr_dir.join("%s.csr.pem" % name).strpath)

    # Initialise one-level deep hierarchy.
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, 1, ("rsa", 2048))

    # Issue a bunch of certificates.
    for i in range(1, per_type_count + 1):
        entity_name = "server-with-privkey-%d" % i
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, entity_name, None, None, None)

        entity_name = "server-with-csr-%d" % i
        custom_csr_path = custom_csr_dir.join("server-with-csr-%d.csr.pem" % i).strpath
        gimmecert.commands.server(io.StringIO(), io.StringIO(), tmpdir.strpath, entity_name, None, custom_csr_path, None)

        entity_name = "client-with-privkey-%d" % i
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, entity_name, None, None)

        entity_name = "client-with-csr-%d" % i
        custom_csr_path = custom_csr_dir.join("client-with-csr-%d.csr.pem" % i).strpath
        gimmecert.commands.client(io.StringIO(), io.StringIO(), tmpdir.strpath, entity_name, custom_csr_path, None)

    return tmpdir


@pytest.fixture
def gctmpdir(tmpdir):
    """
    Fixture that initialises Gimmecert project within tmpdir with a
    simple CA hierarchy.

    Initialised CA hierarchy is 1 level deep, with basename used being
    identical to temporary directory base name, and it uses 2048-bit
    RSA keys.

    The fixture is useful in testing of commands where the CA
    hierarchy does not matter (almost anything except init/status
    commands).

    :param tmpdir: Temporary directory (normally pytest tmpdir fixture) created for running the test.
    :type tmpdir: py.path.local

    :returs: Parent directory where Gimmecert has been initialised. Essentially the tmpdir fixture.
    :rtype: py.path.local
    """

    # Initialise one-level deep hierarchy.
    gimmecert.commands.init(io.StringIO(), io.StringIO(), tmpdir.strpath, tmpdir.basename, 1, ("rsa", 2048))

    return tmpdir
