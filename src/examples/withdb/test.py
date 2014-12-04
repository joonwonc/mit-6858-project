import sys
sys.path.append("../../symex")
import fuzzy

from inc import *

def test():
    username = fuzzy.mk_str('username')
    inc(username)

fuzzy.concolic_test(equiv_test, maxiter=2000, verbose=1)
