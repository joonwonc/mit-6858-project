from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *

from db import *

def inc(username):
    numberdb = setup("number", Base)
    user = numberdb.query(Base).get(username)

    usernum = user.number

    if (usernum >= 10):
        return

    new_usernum = usernum + 1
    user.number = new_usernum
    numberdb.commit()

    print "Now [", user.username, "] has [", new_usernum, "]"

if __name__ == "__main__":
    print "__main__ from inc.py"
    numberdb = setup("number", Base)

    inc("user")

