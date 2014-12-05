import sys
sys.path.append("../../symex")

from multiprocessing import *
# from test import *
from test_bug import *

def dummy_snapshot():
    return None

def multi_test(target_func, num_proc, ss):
    p = [None] * num_proc

    for n in range(num_proc):
        p[n] = Process(target=target_func)

    for n in range(num_proc):
        p[n].start()

    return ss()

if __name__ == "__main__":
    res = multi_test(do_concolic_test, 5, verify_result)

    if (not res):
        print "Gotcha!"
