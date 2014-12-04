from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *

from db import *

if __name__ == "__main__":
    print "__main__ from __init__.py"
    numberdb = setup("number", Base)

    newuser = Base()
    newuser.username = "user"
    numberdb.add(newuser)
