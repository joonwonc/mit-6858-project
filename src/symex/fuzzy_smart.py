"""
  A concolic test function supporting multi-trace. (multi-threads)
  A heuristic is added to this version, compared with fuzzy.py.
  The original version comes from z3 python API.
  (http://g.csail.mit.edu/gitweb/?p=z3str.git)
"""

import z3str
import z3
import multiprocessing
import sys
import collections
import Queue
import signal
import operator
import inspect
import __builtin__

import os
import time
import threading

## Our AST structure

class sym_ast(object):
  def __str__(self):
    return str(self._z3expr(True))

class sym_func_apply(sym_ast):
  def __init__(self, *args):
    for a in args:
      if not isinstance(a, sym_ast):
        raise Exception("Passing a non-AST node %s %s as argument to %s" % \
                        (a, type(a), type(self)))
    self.args = args

  def __eq__(self, o):
    if type(self) != type(o):
      return False
    if len(self.args) != len(o.args):
      return False
    return all(sa == oa for (sa, oa) in zip(self.args, o.args))

  def __hash__(self):
    return reduce(operator.xor, [hash(a) for a in self.args], 0)

class sym_unop(sym_func_apply):
  def __init__(self, a):
    super(sym_unop, self).__init__(a)

  @property
  def a(self):
    return self.args[0]

class sym_binop(sym_func_apply):
  def __init__(self, a, b):
    super(sym_binop, self).__init__(a, b)

  @property
  def a(self):
    return self.args[0]

  @property
  def b(self):
    return self.args[1]

class sym_triop(sym_func_apply):
  def __init__(self, a, b, c):
    super(sym_triop, self).__init__(a, b, c)

  @property
  def a(self):
    return self.args[0]

  @property
  def b(self):
    return self.args[1]

  @property
  def c(self):
    return self.args[2]

def z3expr(o, printable = False):
  assert isinstance(o, sym_ast)
  return o._z3expr(printable)

class const_str(sym_ast):
  def __init__(self, v):
    self.v = v

  def __eq__(self, o):
    if not isinstance(o, const_str):
      return False
    return self.v == o.v

  def __hash__(self):
    return hash(self.v)

  def _z3expr(self, printable):
    ## z3str has a weird way of encoding string constants.
    ## for printing, we make strings look like nice constants,
    ## but otherwise we use z3str's encoding plan.
    if printable:
      return z3.Const('"%s"' % self.v, z3str.StringSort())

    enc = "__cOnStStR_" + "".join(["_x%02x" % ord(c) for c in self.v])
    return z3.Const(enc, z3str.StringSort())

class const_int(sym_ast):
  def __init__(self, i):
    self.i = i

  def __eq__(self, o):
    if not isinstance(o, const_int):
      return False
    return self.i == o.i

  def __hash__(self):
    return hash(self.i)

  def _z3expr(self, printable):
    return self.i

class const_bool(sym_ast):
  def __init__(self, b):
    self.b = b

  def __eq__(self, o):
    if not isinstance(o, const_bool):
      return False
    return self.b == o.b

  def __hash__(self):
    return hash(self.b)

  def _z3expr(self, printable):
    return self.b

def ast(o):
  if hasattr(o, '_sym_ast'):
    return o._sym_ast()
  if isinstance(o, bool):
    return const_bool(o)
  if isinstance(o, int):
    return const_int(o)
  if isinstance(o, str) or isinstance(o, unicode):
    return const_str(o)
  raise Exception("Trying to make an AST out of %s %s" % (o, type(o)))

## Logic expressions

class sym_eq(sym_binop):
  def _z3expr(self, printable):
    return z3expr(self.a, printable) == z3expr(self.b, printable)

class sym_and(sym_func_apply):
  def _z3expr(self, printable):
    return z3.And(*[z3expr(a, printable) for a in self.args])

class sym_or(sym_func_apply):
  def _z3expr(self, printable):
    return z3.Or(*[z3expr(a, printable) for a in self.args])

class sym_not(sym_unop):
  def _z3expr(self, printable):
    return z3.Not(z3expr(self.a, printable))

## Arithmetic

class sym_int(sym_ast):
  def __init__(self, id):
    self.id = id

  def __eq__(self, o):
    if not isinstance(o, sym_int):
      return False
    return self.id == o.id

  def __hash__(self):
    return hash(self.id)

  def _z3expr(self, printable):
    return z3.Int(self.id)

class sym_lt(sym_binop):
  def _z3expr(self, printable):
    return z3expr(self.a, printable) < z3expr(self.b, printable)

class sym_gt(sym_binop):
  def _z3expr(self, printable):
    return z3expr(self.a, printable) > z3expr(self.b, printable)

class sym_plus(sym_binop):
  def _z3expr(self, printable):
    return z3expr(self.a, printable) + z3expr(self.b, printable)

class sym_minus(sym_binop):
  def _z3expr(self, printable):
    return z3expr(self.a, printable) - z3expr(self.b, printable)

class sym_mul(sym_binop):
  def _z3expr(self, printable):
    return z3expr(self.a, printable) * z3expr(self.b, printable)

class sym_div(sym_binop):
  def _z3expr(self, printable):
    return z3expr(self.a, printable) / z3expr(self.b, printable)

## String operations

class sym_str(sym_ast):
  def __init__(self, id):
    self.id = id

  def __eq__(self, o):
    if not isinstance(o, sym_str):
      return False
    return self.id == o.id

  def __hash__(self):
    return hash(self.id)

  def _z3expr(self, printable):
    return z3.Const(self.id, z3str.StringSort())

class sym_concat(sym_binop):
  def _z3expr(self, printable):
    return z3str.Concat(z3expr(self.a, printable),
                        z3expr(self.b, printable))

class sym_length(sym_unop):
  def _z3expr(self, printable):
    return z3str.Length(z3expr(self.a, printable))

class sym_substring(sym_triop):
  def _z3expr(self, printable):
    return z3str.SubString(z3expr(self.a, printable),
                           z3expr(self.b, printable),
                           z3expr(self.c, printable))

class sym_indexof(sym_binop):
  def _z3expr(self, printable):
    return z3str.Indexof(z3expr(self.a, printable),
                         z3expr(self.b, printable))

class sym_contains(sym_binop):
  def _z3expr(self, printable):
    return z3str.Contains(z3expr(self.a, printable),
                          z3expr(self.b, printable))

class sym_startswith(sym_binop):
  def _z3expr(self, printable):
    return z3str.StartsWith(z3expr(self.a, printable),
                            z3expr(self.b, printable))

class sym_endswith(sym_binop):
  def _z3expr(self, printable):
    return z3str.EndsWith(z3expr(self.a, printable),
                          z3expr(self.b, printable))

class sym_replace(sym_triop):
  def _z3expr(self, printable):
    return z3str.Replace(z3expr(self.a, printable),
                         z3expr(self.b, printable),
                         z3expr(self.c, printable))

## Symbolic simplifications

class patname(sym_ast):
  def __init__(self, name, pattern = None):
    self.name = name
    self.pattern = pattern

simplify_patterns = [
  (sym_substring(patname("a",
                         sym_substring(patname("b"),
                                       patname("c"),
                                       sym_minus(sym_length(patname("b")),
                                                 patname("c")))),
                 patname("d"),
                 sym_minus(sym_length(patname("a")),
                           patname("d"))),
   sym_substring(patname("b"),
                 sym_plus(patname("c"), patname("d")),
                 sym_minus(sym_length(patname("b")),
                           sym_plus(patname("c"), patname("d"))))
  ),
  (sym_concat(patname("a"), const_str("")),
   patname("a")
  ),
]

def pattern_match(expr, pat, vars):
  if isinstance(pat, patname):
    if pat.name in vars:
      return expr == vars[pat.name]
    else:
      vars[pat.name] = expr
      if pat.pattern is None:
        return True
      return pattern_match(expr, pat.pattern, vars)

  if type(expr) != type(pat):
    return False

  if not isinstance(expr, sym_func_apply):
    return expr == pat

  if len(expr.args) != len(pat.args):
    return False

  return all(pattern_match(ea, pa, vars)
             for (ea, pa) in zip(expr.args, pat.args))

def pattern_build(pat, vars):
  if isinstance(pat, patname):
    return vars[pat.name]
  if isinstance(pat, sym_func_apply):
    args = [pattern_build(pa, vars) for pa in pat.args]
    return type(pat)(*args)
  return pat

def simplify(e):
  matched = True
  while matched:
    matched = False
    for (src, dst) in simplify_patterns:
      vars = {}
      if not pattern_match(e, src, vars):
        continue
      e = pattern_build(dst, vars)
      matched = True

  if isinstance(e, sym_func_apply):
    t = type(e)
    args = [simplify(a) for a in e.args]
    return t(*args)

  return e

## Current path constraint

procs_map = {}
cur_path_constr = {}

def get_caller():
  frame = inspect.currentframe()
  try:
    while True:
      info = inspect.getframeinfo(frame)
      ## Skip stack frames inside the symbolic execution engine,
      ## as well as in the rewritten replacements of dict, %, etc.
      if not info.filename.endswith('fuzzy.py') and\
         not info.filename.endswith('rewriter.py'):
        return (info.filename, info.lineno)
      frame = frame.f_back
  finally:
    del frame

def add_constr(e):
  global procs_map
  pidx = procs_map[threading.current_thread().ident]

  global cur_path_constr

  cur_path_constr[pidx].append(simplify(e))

## This exception is thrown when a required symbolic condition
## is not met; the symbolic execution engine should retry with
## a different input to go down another path instead.
class RequireMismatch(Exception):
  pass

def require(e):
  if not e:
    raise RequireMismatch()

## Creating new symbolic names

namectr = 0
def uniqname(id):
  global namectr
  namectr += 1
  return "%s_%d" % (id, namectr)

## Helper for printing Z3-indented expressions

def indent(s, spaces = '  '):
  return spaces + str(s).replace('\n', '\n' + spaces)

## Support for forking because z3str uses lots of global variables

## timeout for Z3, in seconds
z3_timeout = 5

def fork_and_check_worker(constr, conn):
  z3e = z3expr(constr)
  (ok, z3m) = z3str.check_and_model(z3e)
  m = {}
  if ok == z3.sat:
    for k in z3m:
      v = z3m[k]
      if v.sort() == z3.IntSort():
        m[str(k)] = v.as_long()
      elif v.sort() == z3str.StringSort():
        # print "Model string %s: %s" % (k, v)
        vs = str(v)
        if not vs.startswith('__cOnStStR_'):
          if not str(k).startswith('_t_'):
            print 'Undecodable string constant (%s): %s' % (k, vs)
          continue
        hexbytes = vs.split('_x')[1:]
        bytes = [int(h, 16) for h in hexbytes]
        m[str(k)] = ''.join(chr(x) for x in bytes)
      else:
        raise Exception("Unknown sort for %s=%s: %s" % (k, v, v.sort()))
  conn.send((ok, m))
  conn.close()

def fork_and_check(constr):
  constr = simplify(constr)

  parent_conn, child_conn = multiprocessing.Pipe()
  p = multiprocessing.Process(target=fork_and_check_worker,
                              args=(constr, child_conn))
  p.start()
  child_conn.close()

  ## timeout after a while..
  def sighandler(signo, stack):
    print "Timed out.."
    # print z3expr(constr, True).sexpr()
    p.terminate()

  signal.signal(signal.SIGALRM, sighandler)
  signal.alarm(z3_timeout)

  try:
    res = parent_conn.recv()
  except EOFError:
    res = (z3.unknown, None)
  finally:
    signal.alarm(0)

  p.join()
  return res

## Symbolic type replacements

def concolic_bool(sym, v):
  ## Python claims that 'bool' is not an acceptable base type,
  ## so it seems difficult to subclass bool.  Luckily, bool has
  ## only two possible values, so whenever we get a concolic
  ## bool, add its value to the constraint.
  add_constr(sym_eq(sym, ast(v)))
  return v

class concolic_int(int):
  def __new__(cls, sym, v):
    self = super(concolic_int, cls).__new__(cls, v)
    self.__v = v
    self.__sym = sym
    return self

  def __eq__(self, o):
    if not isinstance(o, int):
      return False

    if isinstance(o, concolic_int):
      res = (self.__v == o.__v)
    else:
      res = (self.__v == o)

    return concolic_bool(sym_eq(ast(self), ast(o)), res)

  def __ne__(self, o):
    return not self.__eq__(o)

  # def __cmp__(self, o):
  #   res = long(self.__v).__cmp__(long(o))
  #   if concolic_bool(sym_lt(ast(self), ast(o)), res < 0):
  #     return -1
  #   if concolic_bool(sym_gt(ast(self), ast(o)), res > 0):
  #     return 1
  #   return 0

  def __lt__(self, o):
    res = long(self.__v).__cmp__(long(o))
    sym = sym_lt(ast(self), ast(o))
    if res < 0:
      add_constr(sym_eq(sym, ast(True)))
      return True

    add_constr(sym_eq(sym, ast(False)))
    return False

  def __gt__(self, o):
    res = long(self.__v).__cmp__(long(o))
    sym = sym_gt(ast(self), ast(o))
    if res > 0:
      add_constr(sym_eq(sym, ast(True)))
      return True

    add_constr(sym_eq(sym, ast(False)))
    return False

  def __cmp__(self, o):
    res = long(self.__v).__cmp__(long(o))
    if res < 0:
      sym = sym_lt(ast(self), ast(o))
      add_constr(sym_eq(sym, ast(True)))
      return -1
    if res > 0:
      sym = sym_gt(ast(self), ast(o))
      add_constr(sym_eq(sym, ast(True)))
      return 1

    return 0

  def __add__(self, o):
    if isinstance(o, concolic_int):
      res = self.__v + o.__v
    else:
      res = self.__v + o
    return concolic_int(sym_plus(ast(self), ast(o)), res)

  def __radd__(self, o):
    res = o + self.__v
    return concolic_int(sym_plus(ast(o), ast(self)), res)

  def __sub__(self, o):
    res = self.__v - o
    return concolic_int(sym_minus(ast(self), ast(o)), res)

  def __mul__(self, o):
    res = self.__v * o
    return concolic_int(sym_mul(ast(self), ast(o)), res)

  def __div__(self, o):
    res = self.__v / o
    return concolic_int(sym_div(ast(self), ast(o)), res)

  def _sym_ast(self):
    return self.__sym

class concolic_str(str):
  def __new__(cls, sym, v):
    assert type(v) == str or type(v) == unicode
    self = super(concolic_str, cls).__new__(cls, v)
    self.__v = v
    self.__sym = sym
    return self

  def __eq__(self, o):
    if not isinstance(o, str) and not isinstance(o, unicode):
      return False

    if isinstance(o, concolic_str):
      res = (self.__v == o.__v)
    else:
      res = (self.__v == o)

    return concolic_bool(sym_eq(ast(self), ast(o)), res)

  def __ne__(self, o):
    return not self.__eq__(o)

  def __add__(self, o):
    if isinstance(o, concolic_str):
      res = self.__v + o.__v
    else:
      res = self.__v + o
    return concolic_str(sym_concat(ast(self), ast(o)), res)

  def __radd__(self, o):
    res = o + self.__v
    return concolic_str(sym_concat(ast(o), ast(self)), res)

  ## Exercise 4: your code here.
  def __len__(self):
    res = self.__v.__len__()
    return concolic_int(sym_length(ast(self)), res)

  def __contains__(self, o):
    res = self.__v.__contains__(o)
    return concolic_bool(sym_contains(ast(self), ast(o)), res)

  def startswith(self, o):
    res = self.__v.startswith(o)
    return concolic_bool(sym_startswith(ast(self), ast(o)), res)

  def endswith(self, o):
    res = self.__v.endswith(o)
    return concolic_bool(sym_endswith(ast(self), ast(o)), res)

  def __getitem__(self, i):
    res = self.__v[i]
    return concolic_str(sym_substring(ast(self), ast(i), ast(1)), res)

  def __getslice__(self, i, j):
    if j == 9223372036854775807 or j == 2147483647:
      ## Python passes in INT_MAX when there's no upper bound.
      ## Unfortunately, this differs depending on whether you're
      ## running in a 32-bit or a 64-bit system.
      j = self.__len__()
    res = self.__v[i:j]
    return concolic_str(sym_substring(ast(self), ast(i), ast(j-i)), res)

  def find(self, ch):
    res = self.__v.find(ch)
    return concolic_int(sym_indexof(ast(self), ast(ch)), res)

  def decode(self, encoding = sys.getdefaultencoding(), errors = 'strict'):
    ## XXX hack: we restrict z3str to just 7-bit ASCII (see call to
    ## setAlphabet7bit) and then pretend that str and unicode objects
    ## are the same.
    return self

  def encode(self, encoding = sys.getdefaultencoding(), errors = 'strict'):
    ## XXX same hack as for decode().
    return self

  def __unicode__(self):
    ## XXX same hack as for decode().
    return self

  def lstrip(self, chars = ' \t\n\r'):
    for ch in chars:
      if self.startswith(chars):
        return self[1:].lstrip(chars)
    return self

  def rsplit(self, sep = None, maxsplit = -1):
    if maxsplit != 1 or type(sep) != str:
      return self.__v.rsplit(sep, maxsplit)

    name = 'rsplit_%s_%s' % (self.__sym, sep)
    l = mk_str(name + '_l')
    r = mk_str(name + '_r')
    if l + sep + r != self:
      require(sep not in self)
      return self

    require(sep not in l)
    require(sep not in r)
    return (l, r)

  def upper(self):
    ## XXX an incorrect overloading that gets us past werkzeug's use
    ## of .upper() on the HTTP method name..
    return self

  def _sym_ast(self):
    return self.__sym

## Override some builtins..

old_len = __builtin__.len
def xlen(o):
  if isinstance(o, concolic_str):
    return o.__len__()
  return old_len(o)
__builtin__.len = xlen

## Track inputs that should be tried later

from itertools import *
class Permutator(object):
  def __init__(self, domain, dim = 1):
    self.domain = domain
    self.dim = dim
    self.permutator = product(domain, repeat = dim)

  def get(self):
    if (len(self.domain) > 0 and self.dim > 0):
      return self.permutator
    else:
      self.domain = [{'dummy':0}]
      self.repeat = 1
      self.permutator = product(self.domain, repeat = self.repeat)
      return self.permutator

class InputQueue(object):
  def __init__(self):
    ## "inputs" is a priority queue storing inputs we should try.
    ## The inputs are stored as a dictionary, from symbolic variable
    ## name to the value we should try.  If a value is not present,
    ## mk_int() and mk_str() below will pick a default value.  Each
    ## input also has a priority (lower is "more important"), which
    ## is useful when there's too many inputs to process.
    self.inputs = Queue.PriorityQueue()
    self.inputs.put((0, {}))

    ## "branchcount" is a map from call site (filename and line number)
    ## to the number of branches we have already explored at that site.
    ## This is used to choose priorities for inputs.
    self.branchcount = collections.defaultdict(int)

  def empty(self):
    return self.inputs.empty()

  def get(self):
    (prio, values) = self.inputs.get()
    return values

  def add(self, new_values, caller):
    prio = self.branchcount[caller]
    self.branchcount[caller] += 1
    self.inputs.put((prio, new_values))

## Actual concolic execution API

concrete_values = {}

def mk_int(id):
  global procs_map
  pidx = procs_map[threading.current_thread().ident]
  
  global concrete_values
  if pidx not in concrete_values:
    concrete_values[pidx] = {}

  if id not in concrete_values[pidx]:
    concrete_values[pidx][id] = 0

  return concolic_int(sym_int(id), concrete_values[pidx][id])

# mk_str_lock = threading.Lock()
#   mk_str_lock.acquire()
#   mk_str_lock.release()
def mk_str(id):
  global procs_map
  pidx = procs_map[threading.current_thread().ident]

  global concrete_values
  if pidx not in concrete_values:
    concrete_values[pidx] = {}

  if id not in concrete_values[pidx]:
    concrete_values[pidx][id] = ''

  res = concolic_str(sym_str(id), concrete_values[pidx][id])

  return res

def make_next_constr_expr(constr_list):
  clen = len(constr_list)
  constr_expr = ast(True)
  for i in range(0, clen-1):
    constr_expr = sym_and(constr_list[i], constr_expr)

  constr_expr = sym_and(sym_eq(constr_list[clen-1].a, ast(not constr_list[clen-1].b.b)), constr_expr)
  return constr_expr

from multiprocessing import *

def do_nothing():
  return

def filter_nothing(inputs):
  return list(inputs)

def concolic_test(testfunc, initfunc = do_nothing, verifyfunc = do_nothing,
                  filterfunc = filter_nothing, maxproc = 2, verbose = 0):
  ## "checked" is the set of constraints we already sent to Z3 for
  ## checking.  use this to eliminate duplicate paths.
  checked = set()

  ## "permutation" is the set of inputs that we have explored
  old_permutation = []
  permutation = []

  global procs_map
  global concrete_values
  global cur_path_constr

  ## for numproc = 1, we simply do concolic test and gather inputs
  inputs = [{'dummy':0}]
  inputs_gather = []
  while len(inputs) > 0:
    global concrete_values
    concrete_values[0] = inputs[0]
    inputs = inputs[1:len(inputs)]

    cur_path_constr[0] = []

    if verbose > 0:
      print 'Trying concrete values:', concrete_values[0]

    ## Initialization
    initfunc()

    ## process vector
    procs = {}
    procs_map = {}
    procs[0] = threading.Thread(target=testfunc)

    try:
      procs[0].start()
      procs_map[procs[0].ident] = 0
    except RequireMismatch:
      pass

    ## Let's join threads
    procs[0].join()

    ## Verification
    verifyfunc()

    clen = len(cur_path_constr[0])
    for i in range(clen, 0, -1):
      constr_expr = make_next_constr_expr(cur_path_constr[0][0:i])
      if constr_expr in checked:
        continue

      checked.add(constr_expr)

      (ok, model) = fork_and_check(constr_expr)
      if ok == z3.sat:
        inputs.append(model)
        if model not in inputs_gather:
          inputs_gather.append(model)
        break

  ## filter
  inputs_gather = filterfunc(inputs_gather)

  ## now for numproc >= 2
  for numproc in range(maxproc):
    numproc = numproc + 1

    if numproc == 1:
      continue

    ## list of inputs we should try to explore.
    inputs = Permutator(inputs_gather, numproc)

    for input in inputs.get():
      if verbose > 0:
        print 'Trying concrete values:', input

      pidx = 0
      for per_input in input:
        concrete_values[pidx] = per_input
        cur_path_constr[pidx] = []
        pidx = pidx + 1

      ## Initialization
      initfunc()

      ## process vector
      procs = {}
      procs_map = {}
      for i in range(pidx):
        procs[i] = threading.Thread(target=testfunc)

      try:
        for i in range(pidx):
          procs[i].start()
          procs_map[procs[i].ident] = i
      except RequireMismatch:
        pass
      except:
        print "I was car..."

      ## Let's join threads
      for i in range(pidx):
        procs[i].join()

      ## Verification
      verifyfunc()

      ## Now try to increase permutation pool
      for i in range(pidx):
        clen = len(cur_path_constr[i])

        for ci in range(clen, 0, -1):
          constr_expr = make_next_constr_expr(cur_path_constr[i][0:ci])
          if constr_expr in checked:
            continue

          checked.add(constr_expr)

          (ok, model) = fork_and_check(constr_expr)
          if ok == z3.sat:
            if model not in permutation:
              permutation.append(model)
            break
