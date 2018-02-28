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


def init(project_directory, ca_base_name):
    """
    Initialises the necessary directory and CA hierarchies for use in
    the specified directory.

    :param project_directory: Path to directory where the structure should be initialised. Should be top-level project directory normally.
    :type project_directory: str

    :param ca_base_name: Base name to use for constructing CA subject DNs.
    :type ca_base_name: str

    :returns: False, if directory has been initialised in previous run, True if project has been initialised in this run.
    :rtype: bool
    """

    # Set-up various paths.
    base_directory = os.path.join(project_directory, '.gimmecert')
    ca_directory = os.path.join(base_directory, 'ca')
    level1_private_key_path = os.path.join(ca_directory, 'level1.key.pem')
    level1_certificate_path = os.path.join(ca_directory, 'level1.cert.pem')
    full_chain_path = os.path.join(ca_directory, 'chain-full.cert.pem')

    if os.path.exists(base_directory):
        return False

    # Initialise the directory.
    gimmecert.storage.initialise_storage(project_directory)

    # Generate private key and certificate.
    level1_dn = gimmecert.crypto.get_dn("%s Level 1" % ca_base_name)
    not_before, not_after = gimmecert.crypto.get_validity_range()
    level1_private_key = gimmecert.crypto.generate_private_key()
    level1_certificate = gimmecert.crypto.issue_certificate(level1_dn, level1_dn, level1_private_key, level1_private_key.public_key(), not_before, not_after)

    # Grab the full CA certificate chain.
    full_chain = level1_certificate

    # Write-out the artifacts.
    gimmecert.storage.write_private_key(level1_private_key, level1_private_key_path)
    gimmecert.storage.write_certificate(level1_certificate, level1_certificate_path)
    gimmecert.storage.write_certificate(full_chain, full_chain_path)

    return True
