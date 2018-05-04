.. Copyright (C) 2018 Branko Majic

   This file is part of Gimmecert documentation.

   This work is licensed under the Creative Commons Attribution-ShareAlike 3.0
   Unported License. To view a copy of this license, visit
   http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to Creative
   Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.


Usage
=====

Gimmecert provides a simple and clean CLI interface for all actions.

Description of all available commands, manadatory arguments, and
optional arguments is also made available via CLI by either using the
help flag (``-h`` / ``--help``) or help command.

Running the tool without any command or argument will output short
usage instructions listing available commands.

To get more detailed general help on tool usage, and list of available
commands with short description on what they do, run one of the
following::

  gimmecert -h
  gimmecert --help
  gimmecert help

To get more details on specific command, along what mandatory and
positional arguments are available, simply provide the help flag when
running them. For example::

  gimmecert init -h
  gimmecert init --help


Quickstart
----------

Gimmecert stores all of its artefacts within the ``.gimmecert``
sub-directory (relative to where the command is run).

Start off by switching to your project directory::

  cd ~/myproject/

Initialise the necessary directories and CA hierarchy::

  gimmecert init

This will create a single CA, providing the following artifacts:

- ``.gimmecert/ca/level1.key.pem`` (private key)
- ``.gimmecert/ca/level1.cert.pem`` (certificate)
- ``.gimmecert/ca/chain-full.cert.pem`` (full CA chain, in this case
  same as ``level1.cert.pem``)

Issue a server certificate::

  gimmecert server myserver1

This will create the following artifacts for the server:

- ``.gimmecert/server/myserver1.key.pem`` (private key)
- ``.gimmecert/server/myserver1.cert.pem`` (certificate)

Resulting certificate will include its own name as one of the DNS
subject alternative names.

Issue a client certificate::

  gimmecert client myclient1

This will create the following artifacts for the client:

- ``.gimmecert/client/myclient1.key.pem`` (private key)
- ``.gimmecert/client/myclient1.cert.pem`` (certificate)

Issue a server certificate with additional DNS subject alternative
names::

  gimmecert server myserver2 myserver2.local service.example.com

This will create the following artifacts for the server:

- ``.gimmecert/server/myserver2.key.pem`` (private key)
- ``.gimmecert/server/myserver2.cert.pem`` (certificate)

This time around, the ``myserver2`` certificate will include
``myserver2``, ``myserver2.local``, and ``service.example.com`` as DNS
subject alternative names.

Issue a server certificate by passing-in certificate signing request
(CSR) from which the public key should be extracted::

  openssl req -new -newkey rsa:2048 -nodes -keyout "/tmp/myserver3.key.pem" -subj "/CN=ignoredname" -out "/tmp/myserver3.csr.pem"
  gimmecert server --csr /tmp/myserver3.csr.pem myserver3

This will create the following artifacts for the server:

- ``.gimmecert/server/myserver3.csr.pem`` (CSR)
- ``.gimmecert/server/myserver3.cert.pem`` (certificate)

Renew existing certificates, keeping the same private key and naming::

  gimmecert renew server myserver1
  gimmecert renew server myclient1

Show information about CA hierarchy and issued certificates::

  gimmecert status


Initialisation
--------------

Initialisation has to be run one before being being able to issue
server and client certificates. This is done with::

  gimmecert init

Initialisation will:

- Set-up a local directory.
- Initialise the CA hierarchy used for issuing server and client
  certificates. This includes creation of CA private keys (RSA 2048),
  as well as issuance of corresponding certificates.

If you attempt to run initialisation from the same directory twice,
Gimmecert will refuse to do so. Should you need to recreate the
hierarchy, simply remove the ``.gimmcert/`` directory, and start
over. Keep in mind you will need to throw away all of generated key
material and certificates.

The following directories are created as part of initialisation
process:

- ``.gimmecert/``, base directory.
- ``.gimmecert/ca/``, used for storing CA private keys and
  certificates.
- ``.gimmecert/server/``, used for storing server private keys and
  certificates.
- ``.gimmecert/client/``, used for storing client private keys and
  certificates.

Both CA private keys and certificates are stored as OpenSSL-style PEM
files. The naming convention for keys is ``levelN.key.pem``, while for
certificates it is ``levelN.cert.pem``. ``N`` corresponds to CA
level. Level 1 is the root/self-signed CA, level 2 is CA signed by
level 1 CA and so forth.

In addition to individual CA certificates, Gimmecert will also store
the full certificate chain (including the level 1 CA certificate) in
file ``chain-full.cert.pem``.

Subject DN naming convention for all CAs is ``CN=BASENAME Level N
CA``. ``N`` is the CA level, while ``BASENAME`` is by default equal to
current (working) directory name.

By defualt the tool will initialise a one-level CA hierarchy
(i.e. just the root CA).

Both the base name and CA hierarchy depth can be easily overridden by
providing options (both long and short forms are available)::

  gimmecert init --ca-base-name "My Project" --ca-hierarchy-depth 3
  gimmecert init -b "My Project" -d 3

The above examples would both result in creation of the following CA
artifacts:

- ``.gimmecert/ca/level1.key.pem``
- ``.gimmecert/ca/level1.cert.pem`` (subject DN ``My Project Level 1 CA``)
- ``.gimmecert/ca/level2.key.pem``
- ``.gimmecert/ca/level2.cert.pem`` (subject DN ``My Project Level 2 CA``)
- ``.gimmecert/ca/level3.key.pem``
- ``.gimmecert/ca/level3.cert.pem`` (subject DN ``My Project Level 3 CA``)
- ``.gimmecert/ca/chain-full.cert.pem``


Issuing server certificates
---------------------------

Server certificates can be issued once the initialisation is
complete. Command supports passing-in additional DNS subject
alternative names as additional positional arguments::

  gimmecert server NAME [DNS_NAME [DNS_NAME ...]]

The command will:

- Generate a 2048-bit RSA private key.
- Issue a certificate associated with the generated private key using
  the leaf CA (the one deepest in hierachy).

Resulting private keys and certificates are stored within directory
``.gimmecert/server/``. Private key naming convention is
``NAME.key.pem``, while certificates are stored as
``NAME.cert.pem``. In both cases the OpenSSL-style PEM format is used
for storage.

Subject DN naming convention for server certificates is ``CN=NAME``,
where ``NAME`` is passed-in via positional argument.

By default the certificate will include the passed-in server name as
one of its DNS subject alternative names, but additional DNS names can
be passed-in as well. For example::

  gimmecert server myserver myserver.local service.example.com

Key usage and extended key usage in certificate are set typical TLS
server use (e.g. *digital signature* + *key encipherment* for KU, and
*TLS WWW server authentication* for EKU).

Rerunning the command will not overwrite existing data.

.. note::
   For changing the list of additional subject alternative names
   included in already issued server certificates, see the
   ``--update-dns-names`` option in the ``gimmecert renew`` command.

In addition to generating a private key, it is also possible to
pass-in a certificate signing request (CSR). If specified path is a
dash (``-``), CSR is read from standard input. The resulting
certificate will contain public key from the CSR. All other
information stored in the CSR (naming, extensions) is ignored. For
example::

  # Issue server certificate by passing-in path to a generated CSR.
  gimmecert server --csr /tmp/myown.csr.pem myserver

  # Issue server certificate by reading the CSR from standard input.
  gimmecert server --csr - myserver

  # Issue server certificate by reading the CSR from standard input,
  # using redirection.
  gimmecert server --csr - myserver < /tmp/myown.csr.pem

The passed-in CSR will be stored alongside certificate, under
``.gimmecert/server/NAME.csr.pem``.


Issuing client certificates
---------------------------

Client certificates can be issued once the initialisation is
complete. Command accepts a single positional argument::

  gimmecert client NAME

The command will:

- Generate a 2048-bit RSA private key.
- Issue a certificate associated with the generated private key using
  the leaf CA (the one deepest in hierachy).

Rerunning the command will not overwrite existing data.

Resulting private keys and certificates are stored within directory
``.gimmecert/client/``. Private key naming convention is
``NAME.key.pem``, while certificates are stored as
``NAME.cert.pem``. In both cases the OpenSSL-style PEM format is used
for storage.

Subject DN naming convention for client certificates is ``CN=NAME``,
where ``NAME`` is passed-in via positional argument.

Key usage and extended key usage in certificate are set typical TLS
client use (e.g. *digital signature* + *key encipherment* for KU, and
*TLS WWW client authentication* for EKU).

In addition to generating a private key, it is also possible to
pass-in a certificate signing request (CSR). If specified path is a
dash (``-``), CSR is read from standard input. The resulting
certificate will contain public key from the CSR. All other
information stored in the CSR (naming, extensions) is ignored. For
example::

  # Issue client certificate by passing-in path to a generated CSR.
  gimmecert client --csr /tmp/myown.csr.pem myclient

  # Issue client certificate by reading the CSR from standard input.
  gimmecert client --csr - myclient

  # Issue client certificate by reading the CSR from standard input,
  # using redirection.
  gimmecert client --csr - myclient < /tmp/myown.csr.pem

The passed-in CSR will be stored alongside certificate, under
``.gimmecert/client/NAME.csr.pem``.


Renewing certificates
---------------------

Both client and server certificates can be renewed by simply providing
the type and name. This is useful when a certificate has expired, and
it should be renewed with identical naming and private key. Command
requires two positional argumensts::

  gimmecert renew (server|client) NAME

The command will:

- By default keep the existing private key generated for end entity
  (new one can be requested as well).
- Re-use naming and any extensions stored in existing certificate.
- Overwrite the existing certificate with a new one.
- Show information where the artifacts can be grabbed from.

To also generate a new private key during renewal, use the
``--new-private-key`` or ``-p`` option. For example::

  gimmecert renew --new-private-key server myserver
  gimmecert renew -p server my server

To replace the existing private key or CSR during renewal with a new
CSR, use the ``--csr`` option and pass along path to the file. If
specified path is a dash (``-``), CSR is read from standard input. For
example::

  gimmecert renew --csr /tmp/myserver.csr.pem server myserver
  gimmecert renew --csr - server myserver < /tmp/myserver.csr.pem
  gimmecert renew --csr - client myclient

If you initially made a mistake when providing additional DNS subject
alternative names for a server certificate, you can easily fix this
with the ``--update-dns-names`` or ``-u`` option::

  # Replace existing additional names with just one name.
  gimmecert renew server --update-dns-names "correctname.example.com" myserver

  # Replace existing additional names with mutliple names.
  gimmecert renew server --update-dns-names "correctname1.example.com,correctname2.example.com" myserver 

  # Remove additional names altogether.
  gimmecert renew server --update-dns-names "" myserver


Getting information about CA hierarchy and issued certificates
--------------------------------------------------------------

In order to show information about the CA hierarchy and issued
certificates simply run the status command::

  gimmecert status

The command will:

- Show information about every CA in generated hierarchy (subject DN,
  validity, certificate paths, whether the CA is used for issuing end
  entity certificates).
- Show information about all issued server certificates (subject DN,
  DNS subject alternative names, validity, private key or CSR path,
  certificate path).
- Show information about all issued client certificates (subject DN,
  validity, private key or CSR path, certificate path).

Validity of all certificates is shown in UTC.

Command can also be used for checking if Gimmecert has been
initialised in local directory or not.
