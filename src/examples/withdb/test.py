import sys
sys.path.append("../../symex")
import fuzzy
import symsql

from db import *
from inc import *

def test():
    username = fuzzy.mk_str('username')
    inc(username)

    numberdb = setup("number", NumberBase)
    user = numberdb.query(Number).get(username)
    
    if (user == None):
        return

    usernum = user.number

    if (usernum > 10):
        print "Gotcha!"
        return

def do_concolic_test():
    try:
        print "Concolic test begins..."
        fuzzy.concolic_test(test, maxiter=2000, verbose=1)
    except:
        print "Crash Gotcha!"

