import sys
sys.path.append("../../symex")
import fuzzy
import symsql
import time
import random

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
        print prestate
        print prostate
        return False

    return True

def do_concolic_test():
    # try:
        print "Concolic test begins..."
        #time.sleep(random.random()/1000.0)
        fuzzy.concolic_test(test_bug2, maxiter=2000, verbose=1)
    # except:
    #     print "Crash Gotcha!"

#    numberdb = setup("number", NumberBase)
#    user = numberdb.query(Number).get(username)
#
#    if (user == None):
#        return
#
#    usernum = user.number
#
#    if (usernum > 10):
#        print "Gotcha!"
#        return

# __init__.py (db setup/user initialization)
# state1 = dict (ex alice=10, kyelok=0)
# fuzzy
# state2 ?= state1 + trasfer_log

