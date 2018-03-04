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

import gimmecert.crypto
import gimmecert.storage


def init(project_directory, ca_base_name, ca_hierarchy_depth):
    """
    Initialises the necessary directory and CA hierarchies for use in
    the specified directory.

    :param project_directory: Path to directory where the structure should be initialised. Should be top-level project directory normally.
    :type project_directory: str

    :param ca_base_name: Base name to use for constructing CA subject DNs.
    :type ca_base_name: str

    :param ca_hierarchy_depth: Length/depths of CA hierarchy that should be initialised. E.g. total number of CAs in chain.
    :type ca_hierarchy_depth: int

    :returns: False, if directory has been initialised in previous run, True if project has been initialised in this run.
    :rtype: bool
    """

    # Set-up various paths.
    base_directory = os.path.join(project_directory, '.gimmecert')
    ca_directory = os.path.join(base_directory, 'ca')

    if os.path.exists(base_directory):
        return False

    # Initialise the directory.
    gimmecert.storage.initialise_storage(project_directory)

    # Generate the CA hierarchy.
    ca_hierarchy = gimmecert.crypto.generate_ca_hierarchy(ca_base_name, ca_hierarchy_depth)

    # Output the CA private keys and certificates.
    for level, (private_key, certificate) in enumerate(ca_hierarchy, 1):
        private_key_path = os.path.join(ca_directory, 'level%d.key.pem' % level)
        certificate_path = os.path.join(ca_directory, 'level%d.cert.pem' % level)
        gimmecert.storage.write_private_key(private_key, private_key_path)
        gimmecert.storage.write_certificate(certificate, certificate_path)

    # Output the certificate chain.
    full_chain = [certificate for _, certificate in ca_hierarchy]
    full_chain_path = os.path.join(ca_directory, 'chain-full.cert.pem')
    gimmecert.storage.write_certificate_chain(full_chain, full_chain_path)

    return True


def server(project_directory, entity_name):
    """
    Generates a server private key and issues a server certificate
    using the CA hierarchy initialised within the specified directory.

    :param project_directory: Path to project directory under which the CA artifacats etc will be looked-up.
    :type project_directory: str

    :param entity_name: Name of the server entity. Name will be used in subject DN and DNS subject alternative name.
    :type entity_name: str

    :returns: Tuple consisting out of status and message to show to user.
    :rtype: (bool, str)
    """

    private_key_path = os.path.join('.gimmecert', 'server', '%s.key.pem' % entity_name)
    certificate_path = os.path.join('.gimmecert', 'server', '%s.cert.pem' % entity_name)

    if not gimmecert.storage.is_initialised(project_directory):
        return False, "CA hierarchy must be initialised prior to issuing server certificates. Run the gimmecert init command first."

    message = """Server certificate issued.\n
    Server private key: .gimmecert/server/%s.key.pem
    Server certificate: .gimmecert/server/%s.cert.pem
""" % (entity_name, entity_name)

    ca_hierarchy = gimmecert.storage.read_ca_hierarchy(os.path.join(project_directory, '.gimmecert', 'ca'))
    issuer_private_key, issuer_certificate = ca_hierarchy[-1]
    private_key = gimmecert.crypto.generate_private_key()
    certificate = gimmecert.crypto.issue_server_certificate(entity_name, private_key.public_key(), issuer_private_key, issuer_certificate)

    gimmecert.storage.write_private_key(private_key, private_key_path)
    gimmecert.storage.write_certificate(certificate, certificate_path)

    return True, message
