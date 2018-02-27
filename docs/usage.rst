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
