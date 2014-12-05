import sys
sys.path.append("../../symex")

from multiprocessing import *
from test import *

def dummy_snapshot():
    return None

def multi_test(target_func, num_proc, ss1, ss2):
    snapshot1 = ss1()

    p = [None] * num_proc

    for n in range(num_proc):
        p[n] = Process(target=target_func)

    for n in range(num_proc):
        p[n].start()

    snapshot2 = ss2()

    return (ss1() == ss2())

if __name__ == "__main__":
    res = multi_test(do_concolic_test, 3, dummy_snapshot, dummy_snapshot)

    if (not res):
        print "Gotcha!"
