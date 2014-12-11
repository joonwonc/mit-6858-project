#!/usr/bin/env python

"""
  A simple function for checking the concolic test framework works
  well. "equiv_test" checks if two simple functions "func_a" and
  "func_b" are equivalent or not.
"""

import sys
sys.path.append("../symex")
import fuzzy

def func_a(i):
  if (i <= 1):
    return i
  elif (i == 2):
    return i
  elif (i == 4):
    return i
  else:
    return i*2

def func_b(i):
  if (i <= 4):
    return i
  else:
    return i*2

def equiv_test():
  i = fuzzy.mk_int('i')
  if (func_a(i) != func_b(i)):
    print "Not equivalent functions"

fuzzy.concolic_test(equiv_test, maxiter=2000, verbose=1)

