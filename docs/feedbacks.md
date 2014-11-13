Summary
=======

* test cases support - all submissions of 6.858
* potentially long for C/C++ - dealing with primitives
* how to deal with multiple processes - scheduling / nondeterminism / state-space explosion
* should focus on security

Original Comments
=================

* Sounds great. If you want some test cases for your concolic execution
framework, we could potentially arrange for you to run your code over
all of the student submissions; they should all have fairly similar
RPC systems, so you might be able to find interesting bugs.

* Instrumenting C/C++ programs could be potentially a long project,
since you won't have the ability to capture accesses to primitives. I'd
also be careful about what your scheduling looks like when you have
multiple processes. You should probably also mention a bit about how
some of the IPC is outside of your control, and could be affected by
programs or things that you aren't directly instrumenting.

* This is a nice idea! How do you plan to deal with nondeterminism across
different processes, such that you can do a systematic exploration
of the state space? For example, will you force processes to generate
and receive RPC messages in a particular order?

* It's difficult to estimate how much work this project is, as you
will be expanding upon an existing concolic execution system. This
project is also in danger of failing out of scope of the class. While
concolic execution was taught in lecture, it was covered because it
can be used to find security bugs in programs. I'm a little worried
that should you choose to test your system on LCM, your project won't
really have to do with security.

* The proposal looks great!  I'd like to use it to test our zoobar
web server.  One concern is how to handle non-determinism during RPC.
For example, some bugs might appear only when one message arrives
earlier than the other.  Do you plan to symbolically run both cases?

* On the surface, it seems like treating an RPC as strictly an abstract
function call could avoid your worries about cycles in the execution
tree. Even if "processes usually tend to transmit data to each other"
this would just correspond to mutually recursive functions.
