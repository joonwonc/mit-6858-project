from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *

import sys
sys.path.append("./server/zoobar")
from zoodb import *

if __name__ == "__main__":
    print "__main__ from __init__.py"
    persondb = person_setup()
    # newperson1 = Person()
    # newperson1.username = "u1"
    # newperson2 = Person()
    # newperson2.username = "u2"
    # newperson3 = Person()
    # newperson3.username = "u3"

    # persondb.add(newperson1)
    # persondb.add(newperson2)
    # persondb.add(newperson3)

    # persondb.commit()
