#!/usr/bin/python

import sys
sys.path.append("../../symex")
import fuzzy
import __builtin__
import inspect
import importwrapper as importwrapper
import rewriter as rewriter

importwrapper.rewrite_imports(rewriter.rewriter)

import symsql
import symflask
import symeval

import time
import random

import os

sys.path.append("./server")
import zoobar
from zoobar.bank import *
from zoobar.zoodb import *
from zoobar.auth import *

def startresp(status, headers):
    return

def test_bug():
    time.sleep(0.1)
    username1 = fuzzy.mk_str('u1')
    username2 = fuzzy.mk_str('u2')
    transfer(username1,username2,1)

def adduser(pdb, username, token):
  u = Person()
  u.username = username
  u.token = token
  pdb.add(u)

def init():
    # initialization
    pdb = person_setup()
    pdb.query(Person).delete()
    adduser(pdb, 'u1', 'u1ok')
    adduser(pdb, 'u2', 'u2ok')
    pdb.commit()
    
    tdb = transfer_setup()
    tdb.query(Transfer).delete()
    tdb.commit()

def test_zoobar():
    time.sleep(0.1)
    environ = {}
    environ['wsgi.url_scheme'] = 'http'
    environ['wsgi.input'] = 'xxx'
    environ['SERVER_NAME'] = 'zoobar'
    environ['SERVER_PORT'] = '80'
    environ['SCRIPT_NAME'] = 'script'
    environ['QUERY_STRING'] = 'query'
    environ['HTTP_REFERER'] = fuzzy.mk_str('referrer')
    environ['HTTP_COOKIE'] = fuzzy.mk_str('cookie')

    ## In two cases, we over-restrict the inputs in order to reduce the
    ## number of paths that "make check" explores, so that it finishes
    ## in a reasonable amount of time.  You could pass unconstrained
    ## concolic values for both REQUEST_METHOD and PATH_INFO, but then
    ## zoobar generates around 2000 distinct paths, and that takes many
    ## minutes to check.

    # environ['REQUEST_METHOD'] = fuzzy.mk_str('method')
    # environ['PATH_INFO'] = fuzzy.mk_str('path')
    environ['REQUEST_METHOD'] = 'GET'
    environ['PATH_INFO'] = 'trans' + fuzzy.mk_str('path')

    if environ['PATH_INFO'].startswith('//'):
      return

    try:
      resp = zoobar.app(environ, startresp)
    except RequireMismatch:
      pass

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

def filter(inputs):
    return [input for input in inputs
            if "u1" in input and "u2" in input and not input["u1"] == input["u2"]]

def do_concolic_test():
    print "Concolic test begins..."
    fuzzy.concolic_test(test_zoobar, initfunc=init, verifyfunc=verify_result,
                              filterfunc=filter, verbose=1)

if __name__ == "__main__":
    do_concolic_test()
