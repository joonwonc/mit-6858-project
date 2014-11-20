from db import *

def register(username):
    persondb = person_setup()
    person = persondb.query(Person).get(username)
    if person:
        return None
    newperson = Person()
    newperson.username = username
    db.add(newperson)
    db.commit()
    return
