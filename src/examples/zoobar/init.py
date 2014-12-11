#!/usr/bin/env python

"""
  An initialization file for multi-trace concolic tests. It requires
  an argument to choose which initialization to perform by index.
"""

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *

import os
import sys
sys.path.append("./server/zoobar")
from zoodb import *

def init_db():
    os.system("make clean")
    person_setup()
    transfer_setup()

def init1():
    init_db()

def init2():
    init_db()

    persondb = person_setup()
    newperson1 = Person()
    newperson1.username = "u1"
    newperson2 = Person()
    newperson2.username = "u2"
    persondb.add(newperson1)
    persondb.add(newperson2)
    persondb.commit()

def init3():
    init_db()

    persondb = person_setup()
    newperson1 = Person()
    newperson1.username = "u1"
    newperson2 = Person()
    newperson2.username = "u2"
    newperson3 = Person()
    newperson3.username = "u3"
    persondb.add(newperson1)
    persondb.add(newperson2)
    persondb.add(newperson3)
    persondb.commit()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        ind = int(sys.argv[1])

        if ind == 1:
            init1()
        elif ind == 2:
            init2()
        elif ind == 3:
            init3()


