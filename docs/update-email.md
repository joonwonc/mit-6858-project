Updated proposal and schedule
=============================

First, we thank the staff for detailed feedback and concerns
about the weaknesses in the previously submitted proposal. In this
update, we would like to present the following.

1. Discuss the feedback and address the concerns raised
2. Present the updates made to the proposal based on the feedback
3. Preliminary work in exploring the problem
   - New bugs found in zoobar code
   - Attack scripts to confirm the bugs
   - Discuss the remaining work and give a brief timeline

Discussing the feedback
-----------------------

To review the feedback received:

1. Modifying concolic execution to support IPC is not directly related
   to security or in the scope of the 6.858 class
2. It would be interesting to run an updated concolic execution on the
   code submitted by our classmates.
3. The most interesting and challenging aspect of incorporating IPC
   in concolic execution is the non-determinism introduced.

First, we agree that symbolic execution alone is not directly related
to security. We have further extended the scope of the project to also
check for critical bugs through symbolic execution, create attack
scripts that can exploit the bugs, and present fixes for the bug
discovered.

Secondly, we are excited to try our concolic execution on the code
submitted by our classmates. We would like to further discuss how we
can receive these submissions.

We brainstormed how non-determinism could be introduced through IPC
between processes. We discovered that in the case of zoobar, the
work-flow of the system is too simple and sequential that there will
not be non-deterministic aspects introduced when IPC is implemented.
To elaborate on this thought, zoobar can function without IPC -- the
sole purpose of IPC was to separate privileges when accessing external
resources. Thus, there is no additional complexity added through
asynchronous communication between multiple processes, users, etc.

Thus, if IPC is used only to separate privileges of external
resources, there will not be any non-determinism or bugs introduced to
the overall system, assuming that IPC itself is implemented correctly.
We spent several hours on inspecting the implementation of the IPC in
zoobar, and concluded that it is likely to be bug-free.

Then we discussed the functionalities that actually introduced to
non-determinism to zoobar, and realized that it is the multi-client
aspect of the system. If multiple users are connected and interacting
with the zoobar server, from the point of view of a single user, it is
not guaranteed that the same operation repeated several times would
always yield the same results therefore observing a non-deterministic
behavior from his/her point of view.

To further elaborate on this thought, concolic execution on the zoobar
site implicitly assumes that covering all branching conditions of a
program can capture all the states the program can be in. While this
is true for a single-client model, if there are multiple clients
connected to the server, the state of a single user is dependent on
the states of all the other users interacting with the server. In
order to truly cover all the states of a server that can accept
multiple clients, a concolic execution must account for the actions of
the other users.

Updated proposal
----------------

Thus, we would like to update the problem statement of the proposal as
follows:

We propose to modify the current concolic execution system to
support a multi-client model by introducing a "multi-trace concolic
execution" system.
   
The idea is to run several concolic execution threads in parallel with
each thread simulating a single user. This would allow a concolic
execution system to capture the nature of dependency on other users
sharing the same resources.

We would like to demonstrate our multi-trace concolic execution
framework by using it to capture any security problems in the zoobar
application when several users are using it at the same time.

Preliminary work in exploring the problem
-----------------------------------------

To verify our hypothesis that the same action performed by a single
user is also dependent on the actions of other users, we analyzed the
zoobar code for locations where resources are shared between clients.
We have discovered 3 potential bugs in the zoobar code that are caused
by multiple clients interacting with the server. We have developed
attack scripts to confirm that the multi-client bugs actually exist
and can cause the client's web browser to crash or have a user lose
zoobars. Following are the summary of the bugs found:

### Bugs found

#### bug #1: registering two users at once

Function with the bug:

    def register(username, password):
        db = person_setup()
        person = db.query(Person).get(username)
        if person:
            return None
        newperson = Person()
        newperson.username = username
        newperson.password = password
        db.add(newperson)
        db.commit()
        return newtoken(db, newperson)

Explanation: before `db.commit()` is called, `register()` is invoked
twice which will add the same user twice with `db.add()` this will
cause the second `add()` to crash the second user's browser.

#### bug #2: A sending zoobar twice to B

Function with the bug:

    def transfer(sender, recipient, zoobars):
        persondb = person_setup()
        senderp = persondb.query(Person).get(sender)
        recipientp = persondb.query(Person).get(recipient)
        
        sender_balance = senderp.zoobars - zoobars
        recipient_balance = recipientp.zoobars + zoobars
        
        if sender_balance < 0 or recipient_balance < 0:
            raise ValueError()

        senderp.zoobars = sender_balance
        recipientp.zoobars = recipient_balance
        persondb.commit()
        
        transfer = Transfer()
        transfer.sender = sender
        transfer.recipient = recipient
        transfer.amount = zoobars
        transfer.time = time.asctime()
        
        transferdb = transfer_setup()
        transferdb.add(transfer)
        transferdb.commit()

Explanation: A invokes two `transfer()` functions before
`persondb.commit()` is called. persondb gets written with the same
value twice and transfer will record two transfers when only one took
place. For example, A invokes transfer of 5 zoobars twice. B receives
only 5, but transfer log will show two instances of sending 5 which
means A can claim he/she has sent 10 zoobars to B while he had only
sent 5 zoobars.

#### bug #3: A and B sending C zoobar

Function with the bug:

    def transfer(sender, recipient, zoobars):
        persondb = person_setup()
        senderp = persondb.query(Person).get(sender)
        recipientp = persondb.query(Person).get(recipient)
        
        sender_balance = senderp.zoobars - zoobars
        recipient_balance = recipientp.zoobars + zoobars
        
        if sender_balance < 0 or recipient_balance < 0:
            raise ValueError()

        senderp.zoobars = sender_balance
        recipientp.zoobars = recipient_balance
        persondb.commit()
        
        transfer = Transfer()
        transfer.sender = sender
        transfer.recipient = recipient
        transfer.amount = zoobars
        transfer.time = time.asctime()
        
        transferdb = transfer_setup()
        transferdb.add(transfer)
        transferdb.commit()

Explanation: A starts with 100 zoobars, B starts with 10 zoobars, and
C starts with 10 zoobars. A sends C 100 zoobars. Right before
`persondb.commit()` is called B finishes `get(sender)` and
`get(recipient)` which returns 10 zoobars for C and B. Now, A finishes
`persondb.commit()`, which causes C to be at 110 and A at 0. Now, B
calls `persondb.commit()` which causes B to go down to 0, AND cause C
to go down to 20 zoobars instead of 130. Thus, the resulting zoobar
counts would be:
- A: 0 zoobars
- B: 0 zoobars
- C: 20 zoobars

### Attack scripts

We have developed attack scripts (please check our
[github page](https://github.com/joonwonc/mit-6858-project) for
details) to confirm these bugs can actually be triggered. The
screenshots of the results are as follows:

![Attack screenshot 1](https://github.com/joonwonc/mit-6858-project/blob/master/docs/bug1-client.png)
![Attack screenshot 2](https://github.com/joonwonc/mit-6858-project/blob/master/docs/bug1-server.png)
![Attack screenshot 3](https://github.com/joonwonc/mit-6858-project/blob/master/docs/bug2.png)

Remaining work
--------------

Now that we have successfully confirmed the multi-client bugs
in zoobar, we would like to detect these automatically using
a concolic execution framework.
We plan to implement this by having a higher-level framework that
forks off several concolic execution instances similar to the one
used in Lab 3. Then, we plan to suggest fixes for the bugs found.

We plan to implement the above as follows:

- Dec 3: Finish implementing multi-trace concolic execution framework
- Dec 5: Suggest fixes for the bugs found
- Dec 8: Explore the theoretical meaning of our framework