#!/usr/bin/python

import sys
sys.path.append("../../symex")
import fuzzy
import symsql
import time
import random

import sqlalchemy
import os

sys.path.append("./server/zoobar")
from bank import *
from zoodb import *
from auth import *

## Test functions
def test_bug1():
    time.sleep(0.1)

    try:
        username = fuzzy.mk_str('username')
        password = '1234'
        register(username, password)
    except sqlalchemy.exc.IntegrityError:
        print "Verification: Gotcha!"

def test_bug2():
    time.sleep(0.1)
    username1 = fuzzy.mk_str('u1')
    username2 = fuzzy.mk_str('u2')
    transfer(username1,username2,1)

## Initialization functions
def init1():
    os.system("make init")

def init2():
    os.system("make init")

## Verification functions
def verify1():
    return True

def verify2():
    pdb = person_setup()
    tdb = transfer_setup()
    
    prestate = {}
    prostate = {}

    for p in pdb.query(Person).all():
        prestate[p.username] = 10
        prostate[p.username] = p.zoobars
    
    for t in tdb.query(Transfer).all():
        prestate[t.recipient] += t.amount
        prestate[t.sender] -= t.amount

    if (cmp(prestate,prostate) != 0):
        print "Verification: Gotcha!"
        print "Prestate: ", prestate
        print "Prostate: ", prostate
        return False

    return True

## Actual test function
def do_concolic_test():
    print "Multi-trace concolic test begins..."
    fuzzy.concolic_test(test_bug1, initfunc=init1, verifyfunc=verify1, verbose=1)

if __name__ == "__main__":
  do_concolic_test()
