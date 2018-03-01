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
