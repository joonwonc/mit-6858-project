from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *

import sys
import os

NumberBase = declarative_base()
PersonBase = declarative_base()
TransferBase = declarative_base()

class Person(PersonBase):
    __tablename__ = "person"
    username = Column(String(128), primary_key=True)
    zoobars = Column(Integer, nullable=False, default=10)

class Number(NumberBase):
    __tablename__ = "number"
    username = Column(String(128), primary_key=True)
    number = Column(Integer, nullable=False, default=0)

class Transfer(TransferBase):
    __tablename__ = "transfer"
    id = Column(Integer, primary_key=True)
    sender = Column(String(128))
    recipient = Column(String(128))
    amount = Column(Integer)
    time = Column(String)

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

def person_setup():
    return setup("person",PersonBase)

def transfer_setup():
    return setup("transfer",TransferBase)

if __name__ == "__main__":
    print "__main__ from db.py"
    setup("number", NumberBase)
    setup("person", PersonBase)
    setup("transfer", TransferBase)
