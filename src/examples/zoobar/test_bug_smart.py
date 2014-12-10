#!/usr/bin/python

import sys
sys.path.append("../../symex")
import fuzzy_smart
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
        username = fuzzy_smart.mk_str('username')
        password = '1234'
        register(username, password)
    except sqlalchemy.exc.IntegrityError:
        print "Verification: Gotcha!"

def test_bug2():
    time.sleep(0.1)
    username1 = fuzzy_smart.mk_str('u1')
    username2 = fuzzy_smart.mk_str('u2')
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

def filter1(inputs):
    return inputs

def filter2(inputs):
    return [input for input in inputs
            if "u1" in input and "u2" in input and not input["u1"] == input["u2"]]

def do_concolic_test():
    print "Multi-trace concolic test begins..."
    fuzzy_smart.concolic_test(test_bug1, initfunc=init1, verifyfunc=verify1,
                              filterfunc=filter1, verbose=1)

if __name__ == "__main__":
  do_concolic_test()
