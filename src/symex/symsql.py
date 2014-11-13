## This module wraps SQLalchemy's methods to be friendly to
## symbolic / concolic execution.

import fuzzy
import sqlalchemy.orm

oldget = sqlalchemy.orm.query.Query.get
def newget(query, primary_key):
  ## Exercise 5: your code here.
  r = oldget(query, primary_key)

  all = query.all()
  if len(all) == 0:
    return r

  pkey = all[0].__table__.primary_key.columns.keys()[0]
  for i in range(0, len(all)):
    if (primary_key == getattr(all[i], pkey)):
      pass

  return r

sqlalchemy.orm.query.Query.get = newget
