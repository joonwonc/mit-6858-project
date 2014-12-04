from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *

import sys
import os

Base = declarative_base()

class Number(Base):
    __tablename__ = "number"
    username = Column(String(128), primary_key=True)
    number = Column(Integer, nullable=False, default=0)

def setup(name, base):
    thisdir = os.path.dirname(os.path.abspath(__file__))
    dbdir = os.path.join(thisdir, "db", name)
    if not os.path.exists(dbdir):
        os.makedirs(dbdir)

    dbfile = os.path.join(dbdir, "%s.db" % name)
    engine = create_engine('sqlite:///%s' % dbfile, isolation_level='SERIALIZABLE')
    base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    return session()

if __name__ == "__main__":
    print "__main__ from db.py"
    setup("number", Base)
