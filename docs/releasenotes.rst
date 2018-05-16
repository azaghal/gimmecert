Release notes
=============


0.1.0
-----

First release of Gimmecert. Implements ability to set-up per-directory
CA hierarchy that can then be used to issue server and client
certificates.

Resolved issues:

- **User stories**:

  - `GC-4: As a system integrator, I want to easily issue server and client certificates so that I can quickly test software that requires them <https://projects.majic.rs/gimmecert/issues/GC-4>`_
  - `GC-5: As a system integrator, I want to initialise a CA hierarchy in project directory in order to use it within the project <https://projects.majic.rs/gimmecert/issues/GC-5>`_
  - `GC-6: As a system integrator, I want to issue server certificates so I can deploy them for use with server applications I use <https://projects.majic.rs/gimmecert/issues/GC-6>`_
  - `GC-7: As a system integrator, I want to issue client certificates so I can deploy them for use with client applications I use  <https://projects.majic.rs/gimmecert/issues/GC-7>`_
  - `GC-8: As a system integrator, I want to get status of current CA hierarchy and issued certificates so I could determine if I need to take an action <https://projects.majic.rs/gimmecert/issues/GC-8>`_
  - `GC-9: As a system integrator, I want to renew server or client certificate in order to change the additional naming or renew expigration date <https://projects.majic.rs/gimmecert/issues/GC-9>`_
  - `GC-10: As a system integrator, I want to be able to see tool's help in CLI so I can remind myself what commands are available <https://projects.majic.rs/gimmecert/issues/GC-10>`_
  - `GC-21: As a system integrator, I want to be able to issue certificates using a CSR so I can generate my own private key <https://projects.majic.rs/gimmecert/issues/GC-21>`_

- **Feature requests**:

  - `GC-2: Project skeleton <https://projects.majic.rs/gimmecert/issues/GC-2>`_
  - `GC-3: Ability to initialise CA hierarchy <https://projects.majic.rs/gimmecert/issues/GC-3>`_
  - `GC-11: Initial skeleton CLI implementation <https://projects.majic.rs/gimmecert/issues/GC-11>`_
  - `GC-12: Initial installation and usage instructions <https://projects.majic.rs/gimmecert/issues/GC-12>`_
  - `GC-15: Ability to issue server certificates <https://projects.majic.rs/gimmecert/issues/GC-15>`_
  - `GC-16: Ability to issue client certificates <https://projects.majic.rs/gimmecert/issues/GC-16>`_
  - `GC-19: Ability to update server certificate DNS subject alternative names <https://projects.majic.rs/gimmecert/issues/GC-19>`_
  - `GC-18: Ability to renew existing certificates <https://projects.majic.rs/gimmecert/issues/GC-18>`_
  - `GC-20: Ability to display status <https://projects.majic.rs/gimmecert/issues/GC-20>`_
  - `GC-22: Ability to provide CSR for issuing and renewing certificates <https://projects.majic.rs/gimmecert/issues/GC-22>`_

- **Enhancements**:

  - `GC-14: Clean-up test runtime configuration and imrpove usability  <https://projects.majic.rs/gimmecert/issues/GC-14>`_

- **Tasks**:

  - `GC-1: Set-up project infrastructure <https://projects.majic.rs/gimmecert/issues/GC-1>`_
  - `GC-17: Refactor CLI command handling and relevant tests <https://projects.majic.rs/gimmecert/issues/GC-17>`_
