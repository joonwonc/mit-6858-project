import sys
sys.path.append("../../symex")
import fuzzy
import symsql
import time
import random

import os

from bank import *
from db import *
from auth import *

def test_bug1():
    username1 = fuzzy.mk_str('xxx')
    #username1 = 'xxx'
    register(username1)

def test_bug2():
    username1 = fuzzy.mk_str('u1')
    username2 = fuzzy.mk_str('u2')
    transfer(username1,username2,1)

def init():
    os.system("make init")  
        
def verify_result():
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

def do_concolic_test():
    print "Concolic test begins..."
    fuzzy.concolic_test(test_bug2, initfunc=init, verifyfunc=verify_result, verbose=1)

if __name__ == "__main__":
  do_concolic_test()
