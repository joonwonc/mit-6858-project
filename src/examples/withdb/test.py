import sys
sys.path.append("../../symex")
import fuzzy
import symsql

from inc import *

def test():
    username = fuzzy.mk_str('username')
    inc(username)

fuzzy.concolic_test(test, maxiter=2000, verbose=1)
