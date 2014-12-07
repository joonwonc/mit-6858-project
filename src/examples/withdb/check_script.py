#!/usr/bin/python

import os
import sys
import time

def file_read(pn):
    with open(pn) as fp:
        return fp.read()

def sh(cmd, exit_onerr=True):
    os.system(cmd)

delta = [0.007, 0.0071, 0.0072, 0.0073, 0.0074, 0.0075, 0.0076, 0.0077, 0.0078, 0.0079, 0.008]

os.remove('result.out')
for d in delta:
    print "delta#", d
    counter = 0
    sh('echo \"delta# '+str(d)+' Started\" >>result.out')
    for i in range(5):
        print "try#", i
        sh('echo \"try# '+str(i)+' Started\" >> result.out')
        sh('python test_bug.py '+str(d)+' > /dev/null 2> temp.out')
        sh('grep \"Got\" temp.out > gotcha.out')
        with open('gotcha.out') as f:
            counter += sum(1 for _ in f)
        sh('cat gotcha.out >> result.out')
        print "try# "+str(i)+" Finished."
    sh('echo \"delta# '+str(d)+' Finished with counter='+str(counter)+'\" >> result.out')
    print "delta#", d, "counter:", counter, "Finished"

     
