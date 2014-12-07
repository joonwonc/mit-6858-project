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
    time.sleep(0.1)

    try:
        username1 = fuzzy.mk_str('xxx')
        #username1 = 'xxx'
        register(username1)
    except:
        print >> sys.stderr, "Crashed!!!!"

def test_bug2():
    time.sleep(0.1)
    username1 = fuzzy.mk_str('sd')
    username2 = fuzzy.mk_str('rp')
    transfer(username1,username2,1)

def init():
    os.system("make init")  
        
def verify_result(concrete_value,delta):
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
        print >> sys.stderr, "Gotcha! delta : ", delta ," test_vec: ", concrete_value, " prostate: ", prostate
        #print >> sys.stderr, "Prestate: ", prestate
        #print >> sys.stderr, "Prostate: ", prostate
        #print >> sys.stderr, "Test Vectr: ", concrete_value
        return False

    return True

def do_concolic_test():
    #print len(sys.argv)
    print "Concolic test begins..."
    if(len(sys.argv)>1):
        fuzzy.concolic_test(test_bug2, initfunc=init, verifyfunc=verify_result, verbose=0, delta=float(sys.argv[1]))
    else: 
        fuzzy.concolic_test(test_bug2, initfunc=init, verifyfunc=verify_result, verbose=0)

if __name__ == "__main__":
  do_concolic_test()
