.. Copyright (C) 2018 Branko Majic

   This file is part of Gimmecert documentation.

   This work is licensed under the Creative Commons Attribution-ShareAlike 3.0
   Unported License. To view a copy of this license, visit
   http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to Creative
   Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.


About Gimmecert
===============

Gimmecert is a simple CLI tool for quickly issuing X.509 server and
client certificates using locally-generated CA hierarchy with minimal
hassle.

The tool is useful for issuing certificates in:

- Local environment, when trying out a piece of new software that
  depends on use of certificates.
- Development environment, when it is necessary to issue certificates
  either for purpose of integration with other systems, or for ability
  to develop new feature that involves use of certificates.
- Testing/CI/CD environment, when it is necessary to deploy/configure
  tests to use certificates in order to ensure the tests are run
  properly and in full.

At time of this writing, Gimmecert is compatible with the following
Python versions:

- *Python 3.4*
- *Python 3.5*
- *Python 3.6*


Why was this tool created?
--------------------------

The tool was created to remove the pain of setting-up a CA hierarchy,
and then using this hierarchy to issue a couple of test certificates.

While there are existing tools that can be used to this end (in
particular the OpenSSL's CLI and GnuTLS' ``certtool``), the process of
using them is tedious, slow, and error-prone.

There are some more long-lived solutions out there, in form of
full-blown CAs, but those can be both an overkill and resource hog
when all a person needs is a couple of certificates that can be thrown
away.


Features
--------

Gimmecert provides the following features:

- It is very easy to use. Commands are intuitive, and require minimal
  input from the user.
- Initialisation of CA hierarchy for issuing certificates. CA
  hierarchy depth can be specified, letting you easily simulate your
  production environment.
- Issuance of TLS server certificates, with any number of DNS subject
  alternative names.
- Issuance of TLS client certificates.
- All generated artifacts stored within a single sub-directory
  (``.gimmecert``), relative to directory where command is
  invoked. This allows you to easily issue per-project testing
  certificates.


Support
-------

In case of problems with the tool, please do not hesitate to contact
the author at **gimmecert (at) majic.rs**. Known issues and planned
features are tracked on website:

- https://projects.majic.rs/gimmecert/

The tool is hosted on author's own server, alongside a mirror on
Github:

- https://code.majic.rs/gimmecert
- https://github.com/azaghal/gimmecert

Documentation is available on:

- https://gimmecert.readthedocs.io/


License
-------

Gimmecert *code* is licensed under the terms of GPLv3, or (at
your option) any later version. You should have received the full copy of the
GPLv3 license in the local file **LICENSE-GPLv3**, or you may read the full text
of the license at:

- https://www.gnu.org/licenses/gpl-3.0.txt

Gimmecert *documentation* is licensed under the terms of CC-BY-SA 3.0
Unported license. You should have received the full copy of the CC-BY-SA 3.0
Unported in the local file **LICENSE-CC-BY-SA-3.0-Unported**, or you may read
the full text of the license at:

- https://creativecommons.org/licenses/by-sa/3.0/
