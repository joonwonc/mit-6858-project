#!/usr/bin/env python

"""
  A multi-trace concolic tester for the Zoobar application.
  It _employs_ a heuristic; it first gathers inputs for a
  single process and filter if each element is related to
  multi-trace features. (e.g., accessing shared resources)
"""

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

def test_bug2or3():
    time.sleep(0.1)
    username1 = fuzzy_smart.mk_str('u1')
    username2 = fuzzy_smart.mk_str('u2')
    transfer(username1,username2,1)

## Initialization functions
def init1():
    os.system("python init.py 1")

def init2():
    os.system("python init.py 2")

def init3():
    os.system("python init.py 3")

## Verification functions
def verify1():
    return True

def verify2or3():
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

## Filter functions
def filter1(inputs):
    return inputs

def filter2or3(inputs):
    return [input for input in inputs
            if "u1" in input and "u2" in input and not input["u1"] == input["u2"]]

## Actual test function
def do_concolic_test(ind):
    print "Multi-trace concolic test begins..."

    if ind == 1:
        # for bug test 1
        fuzzy_smart.concolic_test(test_bug1, initfunc=init1, verifyfunc=verify1,
                                  filterfunc=filter1, verbose=1)
    elif ind == 2:
        # for bug test 2
        fuzzy_smart.concolic_test(test_bug2or3, initfunc=init2,
                              verifyfunc=verify2or3, filterfunc=filter2or3,
                              verbose=1)
    elif ind == 3:
        # for bug test 3
        fuzzy_smart.concolic_test(test_bug2or3, initfunc=init3,
                                  verifyfunc=verify2or3, filterfunc=filter2or3,
                                  verbose=1)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        ind = int(sys.argv[1])
        do_concolic_test(ind)
