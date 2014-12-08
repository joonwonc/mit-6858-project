Multi-trace Concolic Execution
==============================

* This project implements a multi-trace concolic execution framework,
  which is for exploring multi-dimensional input space where existing
  single-process-based concolic execution system cannot explore.

SYMEX
-----

* Symex is python API for the Z3 solver. For details, follow below
  links:
  - Z3 solver: http://z3.codeplex.com/
  - symex: http://g.csail.mit.edu/gitweb/?p=z3str.git

Examples
--------

* We tested our framework to the Zoobar application; you may check
  whether the framework works well or not by executing some commands,
  with the Makefile in the zoobar directory. For example, you can
  test with following commands in the zoobar directory:
  - make test1
  - make test_smart1

attack_bug2
-----------
* We made a attack script for bug 2 to actually emulate the bug in the
  real world browser. After running the script, you can actually log-in
  to zoobar (localhost:8080) with u2:u2 to see the transfer log and final
  zoobar value.
  - make check


