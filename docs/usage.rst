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

Renew existing certificates, keeping the same private key and naming::

  gimmecert renew server myserver1
  gimmecert renew server myclient1


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

Rerunning the command will not overwrite existing data. However, if
you made a mistake with additional DNS subject alternative names, you
can easily fix this with the ``--update-dns-names`` option::

  # Replace existing additional names.
  gimmecert server --update-dns-names myserver correctname.example.com

  # Remove additional names altogether.
  gimmecert server --update-dns-names myserver

The ``--update-dns-command`` will keep the private key intact - only
the certificate will be renewed. If you haven't issued any certificate
for this server entity before, though, the option is ignored, and the
command behaves as if it was not specified (so you still get a private
key and certificate).


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


Renewing certificates
---------------------

Both client and server certificates can be renewed by simply providing
the type and name. This is useful when a certificate has expired, and
it should be renewed with identical naming and private key. Command
requires two positional argumensts::

  gimmecert renew (server|client) NAME

The command will:

- Keep the existing private key generated for end entity.
- Re-use naming, public key, and any extensions stored in existing
  certificate.
- Overwrite the existing certificate with a new one.
- Show information where the artifacts can be grabbed from.

.. note::
   For changing the list of additional subject alternative names
   included in server certificates, see the ``--update-dns-names`` for
   the ``gimmecert server`` command.
