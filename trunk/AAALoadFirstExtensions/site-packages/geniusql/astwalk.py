"""AST visitors, including rewriters and deparsers.

This work, including the source code, documentation
and related data, is placed into the public domain.

The orginal author is Robert Brewer.

THIS SOFTWARE IS PROVIDED AS-IS, WITHOUT WARRANTY
OF ANY KIND, NOT EVEN THE IMPLIED WARRANTY OF
MERCHANTABILITY. THE AUTHOR OF THIS SOFTWARE
ASSUMES _NO_ RESPONSIBILITY FOR ANY CONSEQUENCE
RESULTING FROM THE USE, MODIFICATION, OR
REDISTRIBUTION OF THIS SOFTWARE.
"""

from compiler import ast
from opcode import cmp_op
import operator
import types
from geniusql import codewalk


ast_to_op = {ast.Power: operator.pow,
             ast.Mul: operator.mul,
             ast.Div: operator.div,
             ast.FloorDiv: operator.floordiv,
             ast.Mod: operator.mod,
             ast.Add: operator.add,
             ast.Sub: operator.sub,
             ast.Subscript: operator.getitem,
             ast.LeftShift: operator.lshift,
             ast.RightShift: operator.rshift,
             ast.Bitand: operator.and_,
             ast.Bitor: operator.or_,
             ast.Bitxor: operator.xor,
             ast.And: operator.and_,
             ast.Or: operator.or_,
             }

binary_to_ast = {'BINARY_POWER': ast.Power,
                 'BINARY_MULTIPLY': ast.Mul,
                 'BINARY_DIVIDE': ast.Div,
                 'BINARY_FLOOR_DIVIDE': ast.FloorDiv,
                 'BINARY_TRUE_DIVIDE': ast.Div,
                 'BINARY_MODULO': ast.Mod,
                 'BINARY_ADD': ast.Add,
                 'BINARY_SUBTRACT': ast.Sub,
                 'BINARY_LSHIFT': ast.LeftShift,
                 'BINARY_RSHIFT': ast.RightShift,
                 }

bit_to_ast = {'BINARY_AND': ast.Bitand,
              'BINARY_OR': ast.Bitor,
              'BINARY_XOR': ast.Bitxor,
              }

repr_to_op = {'**': operator.pow,
              '*': operator.mul,
              '/': operator.div,
              '//': operator.floordiv,
              '%': operator.mod,
              '+': operator.add,
              '-': operator.sub,
              '<<': operator.lshift,
              '>>': operator.rshift,
              '&': operator.and_,
              '|': operator.or_,
              '^': operator.xor,
              }



class AST(object):
    
    args = None
    kwargs = None
    star_args = None
    dstar_args = None
    _root = None
    
    def __init__(self, root=None, args=None, kwargs=None,
                 star_args=None, dstar_args=None):
        self.root = root
        self.args = args or []
        self.kwargs = kwargs or []
        self.star_args = star_args
        self.dstar_args = dstar_args
    
    def _get_root(self):
        return self._root
    def _set_root(self, root):
        self._root = root
    root = property(_get_root, _set_root, "The root node of the AST")
    
    def __repr__(self):
        return ("AST(%r, args=%r, kwargs=%r, star_args=%r, dstar_args=%r)" %
                (self.root, self.args, self.kwargs,
                 self.star_args, self.dstar_args))


class LambdaParser(codewalk.Visitor):
    """Produce an AST from a supplied lambda.
    
    reduce: if True (the default), free variables are turned into Consts
        wherever possible.
    
    Example: k = lambda x: x.Date == datetime.date(2004, 1, 1)
             q = LambdaParser(k, reduce=False).ast()
             r = LambdaParser(k, reduce=True).ast()
    
    _____ q _____
    Lambda(['x'], [], 0,
      Compare(Getattr(Name('x'), 'Date'),
              [('==', CallFunc(Getattr(Name('datetime'), 'date'),
                               [Const(2004), Const(1), Const(1)],
                               None, None))
              ]))
    
    _____ r _____
    Lambda(['x'], [], 0,
      Compare(Getattr(Name('x'), 'Date'),
              [('==', Const(datetime.date(2004, 1, 1)))])
          )
    
    reduce also pre-computes binary operations *and all other builtin or
    free functions* where all operands are constants, globals, or freevars.
    For example:
        Mul((3, 4))
        
    is replaced with:
        Const(12)
    
    However, order is important. lambda x: x * 4 * 5 won't see any
    optimization, because the order of eval is (x * 4) * 5. Rewritten
    as lambda x: 4 * 5 * x, the "4 * 5" can be replaced with "20".
    
    irreducible: a list of constants (globals, freevars, or attributes)
        which should not be reduced. For example, datetime.date.today
        would usually be called and the result stored in the AST (since
        it takes no arguments, and therefore has no free variables).
        If you want the today function to be stored directly in the AST
        (so it can be called later), include it in this "irreducible" list.
        This does not control the conversion of globals and free variables
        into constants--that happens regardless. It only controls the
        reduction of complex expressions into simpler ones.
    
    env: a dict of objects which will be used to make Consts out of
        globals and builtins. This is auto-populated with items in
        __builtin__ and any globals which were present at the time
        the function was created, so you usually don't have to add
        anything. However, it can be a handy way for frameworks to
        provide globals without forcing every caller to import them.
    """
    
    def __init__(self, func, env=None, reduce=True, irreducible=None):
        codewalk.Visitor.__init__(self, func)
        
        self.reduce = reduce
        
        if env is None:
            self.env = {}
        else:
            self.env = env.copy()
        import __builtin__
        self.env.update(vars(__builtin__))
        self.env.update(func.func_globals)
        
        self.ast = AST()
        
        fc = func.func_code
        self.ast.args = list(fc.co_varnames)
        if fc.co_flags & codewalk.CO_VARKEYWORDS:
            self.ast.dstar_args = self.ast.args.pop()
        if fc.co_flags & codewalk.CO_VARARGS:
            self.ast.star_args = self.ast.args.pop()
        
        if irreducible is None:
            irreducible = []
        self.irreducible = irreducible
    
    def walk(self):
        """Walk self and set self.ast.root."""
        self.stack = []
        self.targets = {}
        
        codewalk.Visitor.walk(self)
        
        self.ast.root = self.stack[0]
        
        if self.verbose:
            self.debug("stack:", self.stack)
    
    def _may_reduce(self, *terms):
        """Return True if all terms are ast.Const and not marked irreducible."""
        for term in terms:
            if not isinstance(term, ast.Const):
                return False
            if term.value in self.irreducible:
                return False
            if getattr(term.value, "irreducible", False):
                return False
        return True
    
    def visit_instruction(self, op, lo=None, hi=None):
        # Get the instruction pointer for the current instruction.
        ip = self.cursor - 3
        if hi is None:
            ip += 1
            if lo is None:
                ip += 1
        
        # This is where we do folding of logical AND and OR operators.
        # The Python code just writes "a AND b", but the VM (bytecode)
        # acts more like assembly, using conditional JUMP instructions to
        # implement logical operators. The map stored in self.targets is
        # of the form:
        #     {JUMP target: [(self.stack[-1], 'and'), ...]}
        # where "JUMP target" is the instruction number of the bytecode
        # which is the target of the JUMP, and each item in the value list
        # is a tuple of (top of the calling stack, operation).
        # It's a list because a single bytecode may be the target of
        # multiple JUMP instructions.
        # See visit_JUMP_IF_FALSE / TRUE.
        terms = self.targets.get(ip)
        if terms:
            clause = self.stack[-1]
            while terms:
                term, oper = terms.pop()
                if self.reduce and self._may_reduce(term, clause):
                    op = ast_to_op[oper]
                    clause = ast.Const(op(term.value, clause.value))
                else:
                    clause = oper((term, clause))
            self.stack[-1] = clause
            if self.verbose:
                self.debug("clause:", clause, "\n")
            
            if op == 1:
                # Py2.4: The current instruction is POP_TOP, which means
                # the previous is probably JUMP_*. If so, we don't want to
                # pop the value we just placed on the stack and lose it.
                # We need to replace the entry that the JUMP_* made in
                # self.targets with our new TOS.
                target = self.targets[self.last_target_ip]
                target[-1] = ((clause, target[-1][1]))
                if self.verbose:
                    self.debug("newtarget:", self.last_target_ip, target)
    
    def visit_BUILD_LIST(self, lo, hi):
        numterms = lo + (hi << 8)
        if numterms:
            self.stack[-numterms:] = [ast.List(self.stack[-numterms:])]
    
    def visit_BUILD_MAP(self, lo, hi):
        # Add an empty Dict and add to its .items in STORE_SUBSCR
        self.stack.append(ast.Dict([]))
    
    def visit_BUILD_TUPLE(self, lo, hi):
        numterms = lo + (hi << 8)
        if numterms:
            self.stack[-numterms:] = [ast.Tuple(self.stack[-numterms:])]
    
    def visit_CALL_FUNCTION(self, lo, hi):
        kwargs = []
        for i in xrange(hi):
            val = self.stack.pop()
            key = self.stack.pop()
            kwargs.append(ast.Keyword(key, val))
        
        if lo:
            args = self.stack[-lo:]
            self.stack[-lo:] = []
        else:
            args = []
        
        func = self.stack[-1]
        
        if self.reduce and self._may_reduce(func):
            if func.value is getattr and not isinstance(args[0], ast.Const):
                self.stack[-1] = ast.Getattr(args[0], args[1].value)
                return
            else:
                # If all args/kwargs are also Const,
                # reduce to a single Const.
                argvals = [a.value for a in args if self._may_reduce(a)]
                if len(argvals) == len(args):
                    kwargvals = dict([(k.name, k.expr.value) for k, v in kwargs
                                      if self._may_reduce(k.expr)])
                    if len(kwargvals) == len(kwargs):
                        retval = func.value(*tuple(argvals), **kwargvals)
                        self.stack[-1] = ast.Const(retval)
                        return
        
        if kwargs:
            args += kwargs
        self.stack[-1] = ast.CallFunc(func, args)
    
    def visit_COMPARE_OP(self, lo, hi):
        term1, term2 = self.stack[-2:]
        op = cmp_op[lo + (hi << 8)]
        if self.reduce and self._may_reduce(term1, term2):
            oper = codewalk.comparisons[op]
            self.stack[-2:] = [ast.Const(oper(term1.value, term2.value))]
        else:
            self.stack[-2:] = [ast.Compare(term1, [(op, term2)])]
        if self.verbose:
            self.debug(op)
    
    def visit_DUP_TOP(self):
        self.stack.append(self.stack[-1])
    
    def visit_JUMP_IF_FALSE(self, lo, hi):
        # Note that self.cursor has already advanced to the next instruction.
        target = self.cursor + (lo + (hi << 8))
        bucket = self.targets.setdefault(target, [])
        bucket.append((self.stack[-1], ast.And))
        if self.verbose:
            self.debug("target:", target, bucket)
        # Store target ip for the special code in visit_instruction
        self.last_target_ip = target
    
    def visit_JUMP_IF_TRUE(self, lo, hi):
        # Note that self.cursor has already advanced to the next instruction.
        target = self.cursor + (lo + (hi << 8))
        bucket = self.targets.setdefault(target, [])
        bucket.append((self.stack[-1], ast.Or))
        if self.verbose:
            self.debug("target:", target, bucket)
        # Store target ip for the special code in visit_instruction
        self.last_target_ip = target
    
    def visit_LOAD_ATTR(self, lo, hi):
        term = self.co_names[lo + (hi << 8)]
        obj = self.stack[-1]
        if self.reduce and self._may_reduce(obj):
            self.stack[-1] = ast.Const(getattr(obj.value, term))
        else:
            self.stack[-1] = ast.Getattr(obj, term)
        if self.verbose:
            self.debug(term)
    
    def visit_LOAD_CONST(self, lo, hi):
        val = self.co_consts[lo + (hi << 8)]
        self.stack.append(ast.Const(val))
        if self.verbose:
            self.debug(val)
    
    def visit_LOAD_DEREF(self, lo, hi):
        if self.reduce and hasattr(self, '_func'):
            value = self._func.func_closure[lo + (hi << 8)]
            self.stack.append(ast.Const(codewalk.deref_cell(value)))
            return
        
        name = self.co_freevars[lo + (hi << 8)]
        self.stack.append(ast.Name(name))
    
    def visit_LOAD_FAST(self, lo, hi):
        term = self.co_varnames[lo + (hi << 8)]
        self.stack.append(ast.Name(term))
        if self.verbose:
            self.debug(term)
    
    def visit_LOAD_GLOBAL(self, lo, hi):
        name = self.co_names[lo + (hi << 8)]
        if self.reduce:
            if name not in self.env:
                raise KeyError("'%s' is not present in supplied globals." % name)
            self.stack.append(ast.Const(self.env[name]))
            return
        
        self.stack.append(ast.Name(name))
    
    def visit_POP_TOP(self):
        self.stack.pop()
    
    def visit_ROT_TWO(self):
        k, v = self.stack[-2:]
        self.stack[-2:] = [v, k]
    
    def visit_ROT_THREE(self):
        x, k, v = self.stack[-3:]
        self.stack[-3:] = [v, x, k]
    
    def visit_SLICE_PLUS_0(self):
        obj = self.stack[-1]
        if self.reduce and self._may_reduce(obj):
            self.stack[-1] = ast.Const(obj.value[:])
        else:
            self.stack[-1] = ast.Slice(obj, 'OP_APPLY', None, None)
    
    def visit_SLICE_PLUS_1(self):
        obj, arg = self.stack[-2:]
        if self.reduce and self._may_reduce(obj, arg):
            self.stack[-2:] = [ast.Const(obj.value[arg.value:])]
        else:
            self.stack[-2:] = [ast.Slice(obj, 'OP_APPLY', arg, None)]
    
    def visit_SLICE_PLUS_2(self):
        obj, arg = self.stack[-2:]
        if self.reduce and self._may_reduce(obj, arg):
            self.stack[-2:] = [ast.Const(obj.value[:arg.value])]
        else:
            self.stack[-2:] = [ast.Slice(obj, 'OP_APPLY', None, arg)]
    
    def visit_SLICE_PLUS_3(self):
        obj, arg1, arg2 = self.stack[-3:]
        if self.reduce and self._may_reduce(obj, arg1, arg2):
            self.stack[-3:] = [ast.Const(obj.value[arg1.value:arg2.value])]
        else:
            self.stack[-3:] = [ast.Slice(obj, 'OP_APPLY', arg1, arg2)]
    
    def visit_STORE_SUBSCR(self):
        # 'x' should be an ast.Dict
        v, x, k = self.stack[-3:]
        self.stack[-3:] = []
        x.items.append((k, v))
    
    def visit_UNARY_INVERT(self):
        term = self.stack[-1]
        if self.reduce and self._may_reduce(term):
            self.stack[-1] = ast.Const(~term.value)
        else:
            self.stack[-1] = ast.Invert(term)
    
    def visit_UNARY_NEGATIVE(self):
        term = self.stack[-1]
        if self.reduce and self._may_reduce(term):
            self.stack[-1] = ast.Const(-term.value)
        else:
            self.stack[-1] = ast.UnarySub(term)
    
    def visit_UNARY_NOT(self):
        term = self.stack[-1]
        if self.reduce and self._may_reduce(term):
            self.stack[-1] = ast.Const(not term.value)
        else:
            self.stack[-1] = ast.Not(term)
    
    def visit_UNARY_POSITIVE(self):
        term = self.stack[-1]
        if self.reduce and self._may_reduce(term):
            self.stack[-1] = ast.Const(+term.value)
        else:
            self.stack[-1] = ast.UnaryAdd(term)
    
    def visit_BINARY_SUBSCR(self):
        op1, op2 = self.stack[-2:]
        if self.reduce and self._may_reduce(op1, op2):
            self.stack[-2:] = [ast.Const(op1.value[op2.value])]
        else:
            self.stack[-2:] = [ast.Subscript(op1, 'OP_APPLY', [op2])]
    
    def binary_op(self, op):
        op1, op2 = self.stack[-2:]
        if self.reduce and self._may_reduce(op1, op2):
            self.stack[-2:] = [ast.Const(ast_to_op[op](op1.value, op2.value))]
        else:
            # Binary ops like ast.Add take a single tuple as a first arg
            self.stack[-2:] = [op((op1, op2))]
    
    def bit_op(self, op):
        op1, op2 = self.stack[-2:]
        if self.reduce and self._may_reduce(op1, op2):
            self.stack[-2:] = [ast.Const(ast_to_op[op](op1.value, op2.value))]
        else:
            self.stack[-2:] = [op(op1, op2)]


# Add visit_BINARY methods to LambdaParser.
for k, v in binary_to_ast.iteritems():
    setattr(LambdaParser, "visit_" + k,
            lambda self, op=v: self.binary_op(op))
for k, v in bit_to_ast.iteritems():
    setattr(LambdaParser, "visit_" + k,
            lambda self, op=v: self.bit_op(op))


class ASTDeparser(object):
    """Produce code (as a string) from a supplied AST."""
    
    def __init__(self, ast):
        self.verbose = False
        self.ast = ast
    
    def debug(self, *messages):
        for term in messages:
            print term,
        print
    
    def walk(self, node):
        """Walk the AST and return a string of code."""
        nodetype = node.__class__.__name__
        method = getattr(self, "visit_" + nodetype)
        args = node.getChildren()
        if self.verbose:
            self.debug(nodetype, args)
        return method(*args)
    
    def visit_And(self, *terms):
        return " and ".join(["(%s)" % self.walk(term) for term in terms])
    
    def visit_Or(self, *terms):
        return " or ".join(["(%s)" % self.walk(term) for term in terms])
    
    def visit_List(self, *terms):
        return "[%s]" % ", ".join([self.walk(term) for term in terms])
    
    def visit_Dict(self, *terms):
        return "{%s}" % ", ".join(["%s: %s" % (self.walk(terms[i]),
                                               self.walk(terms[i + 1]))
                                   for i in xrange(0, len(terms), 2)])
    
    def visit_Tuple(self, *terms):
        terms = [self.walk(term) for term in terms]
        if len(terms) == 1:
            terms.append('')
        return "(%s)" % ", ".join(terms)
    
    def visit_CallFunc(self, func, *args):
        star_args = args[-1]
        dstar_args= args[-2]
        
        posargs = []
        kwargs = {}
        for arg in args[:-2]:
            if isinstance(arg, ast.Keyword):
                key, val = arg.name, self.walk(arg.value)
                kwargs[key] = val
            else:
                posargs.append(self.walk(arg))
        kwargs = ", ".join(["%s=%s" % (str(k), v) for k, v in kwargs.iteritems()])
        posargs = ", ".join([str(x) for x in posargs])
        
        if kwargs:
            kwargs = ", " + kwargs
        if star_args:
            star_args = ", " + star_args.name
        else:
            star_args = ""
        if dstar_args:
            dstar_args = ", " + dstar_args.name
        else:
            dstar_args = ""
        
        func = self.walk(func)
        
        return ("%s(%s%s%s%s)" %
                (func, posargs, kwargs, star_args, dstar_args))
    
    def visit_Compare(self, expr, *ops):
        expr = [self.walk(expr)]
        i = 0
        ops_len = len(ops)
        while i < ops_len:
            expr.append(ops[i])
            expr.append(self.walk(ops[i + 1]))
            i += 2
        return " ".join(expr)
    
    def visit_Getattr(self, expr, attrname):
        return "%s.%s" % (self.walk(expr), attrname)
    
    def visit_Const(self, value):
        mod = getattr(value, "__module__", None)
        if isinstance(value, (types.FunctionType, type)):
            # The const in question is a factory function, like int or date.
            name = value.__name__
            term = mod + "." + name
        else:
            term = repr(value)
            if mod and not mod.startswith("__"):
                if not term.startswith(mod + "."):
                    term = mod + "." + term
        return term
    
    def visit_Name(self, name):
        return name
    
    def visit_Slice(self, expr, flags, lower, upper):
        expr = self.walk(expr)
        if lower is None:
            lower = ""
        else:
            lower= self.walk(lower)
        if upper is None:
            upper = ""
        else:
            upper= self.walk(upper)
        return "%s[%s:%s]" % (expr, lower, upper)
    
    def visit_Subscript(self, expr, flags, subs):
        return "%s[%s]" % (self.walk(expr), self.walk(subs))
    
    def visit_Invert(self, expr):
        return "~(" + self.walk(expr) + ")"
    
    def visit_UnarySub(self, expr):
        return "-(" + self.walk(expr) + ")"
    
    def visit_Not(self, expr):
        return "not (" + self.walk(expr) + ")"
    
    def visit_UnaryAdd(self, expr):
        return "+(" + self.walk(expr) + ")"
    
    # ------------------------ Binary Operations ------------------------ #
    
    def binary_op(self, left, op, right):
        return "%s %s %s" % (self.walk(left), op, self.walk(right))
    
    def visit_Power(self, left, right):
        return self.binary_op(left, '**', right)
    
    def visit_Mul(self, left, right):
        return self.binary_op(left, '*', right)
    
    def visit_Div(self, left, right):
        return self.binary_op(left, '/', right)
    
    def visit_FloorDiv(self, left, right):
        return self.binary_op(left, '//', right)
    
    def visit_Mod(self, left, right):
        return self.binary_op(left, '%', right)
    
    def visit_Add(self, left, right):
        return self.binary_op(left, '+', right)
    
    def visit_Sub(self, left, right):
        return self.binary_op(left, '-', right)
    
    def visit_LeftShift(self, left, right):
        return self.binary_op(left, '<<', right)
    
    def visit_RightShift(self, left, right):
        return self.binary_op(left, '>>', right)
    
    def bit_op(self, op, nodes):
        return (" %s " % op).join(map(self.walk, nodes))
    
    def visit_Bitand(self, nodes):
        return self.bit_op("&", nodes)
    
    def visit_Bitor(self, nodes):
        return self.bit_op("|", nodes)
    
    def visit_Bitxor(self, nodes):
        return self.bit_op("^", nodes)


class LambdaDeparser(ASTDeparser):
    """Produce code (as a string) for a Python lambda from a supplied AST."""
    
    def __init__(self, ast, env=None):
        ASTDeparser.__init__(self, ast)
        if env is None:
            self.env = {}
        else:
            self.env = env.copy()
        import __builtin__
        self.env.update(vars(__builtin__))
    
    def code(self, include_func_header=True):
        product = self.walk(self.ast.root)
        if include_func_header:
            args = (self.ast.args or [])[:]
            if self.ast.kwargs:
                args.append(self.ast.kwargs)
            if self.ast.star_args:
                args.append("*%s" % self.ast.star_args)
            if self.ast.dstar_args:
                args.append("**%s" % self.ast.dstar_args)
            args = ", ".join(args)
            if args:
                args = " " + args
            
            product = "lambda%s: %s" % (args, product)
        return product
    
    def visit_Const(self, value):
        mod = getattr(value, "__module__", None)
        if isinstance(value, (types.FunctionType, type)):
            # The const in question is a factory function, like int or date.
            name = value.__name__
            # Here's where we differ from the superclass: pull names from
            # an environment to reduce
            if name in self.env:
                term = name
            else:
                term = mod + "." + name
        else:
            term = repr(value)
            if mod and not mod.startswith("__"):
                if not term.startswith(mod + "."):
                    term = mod + "." + term
        return term


del k, v
