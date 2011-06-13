

# Tree representation of C/C++ (including preprocessor)
#  Intended for code generation


import functools

c_indent_spaces = 4

def get_indent(**kw):
    indent = kw.get('indent', 0)
    out = ' '*indent
    return out

class c_base(object):
    def __init__(self):
        self._args = []
        self._parent = None

    def to_string(self, **kw):
        return ''

    def __str__(self):
        return self.to_string()

    def contains(self, test_val):
        if test_val(self):
            return True
        for a in self._args:
            if a and a.contains(test_val):
                return True
        return False


def is_add(e):
    if isinstance(e,c_expr):
        if e.op == c_expr.C_OP_PLUS:
            return True
        if e.op == c_expr.C_OP_MINUS and e._args[1] != None:
            return True
    return False

#class c_type(c_base):
#    def __init__(self, type, is_pointer=False, is_reference=False):
#        self.type = type
#        self.is_pointer = is_pointer
#        self.is_reference = is_reference
#    def to_string(self):
#        if self.is_pointer:
#            return self.type + "*"
#        if self.is_reference:
#            return self.type + "&"
#        return self.type

class c_type(object):
    _typelist = {}
    def __new__(cls, type, *args):
        if type in c_type._typelist:
            return c_type._typelist[type]
        obj = object.__new__(cls)
        obj.type = type
        c_type._typelist[type] = obj
        return obj
    def to_string(self, **kw):
        return str(self.type)

    def __str__(self):
        return self.to_string()

    def __call__(self, name=''):
        return c_var(name, self)

c_void = c_type('void')
c_int = c_type('int')
c_double = c_type('double')

class c_function_type(c_base):
    def __init__(self, func_type, *args):
        c_base.__init__(self)
        self.type = func_type
        if args:
            self._args = args

    def to_string(self, **kw):
        out = str(self.type) + ' %(name)s('
        out += ','.join([str(s) for s in self._args])
        out += ')'
        return out

class c_typedef(c_base):
    def __init__(self, name, type):
        c_base.__init__(self)
        self.name = name
        self._args.append(type)

    def to_string(self, **kw):
        type = self._args[0]
        out = 'typedef '
        if isinstance(type, c_func_type):
            out += self._args[0].to_string(name=self.name,**kw)
        else:
            out += self._args[0].to_string(**kw) + ' ' + str(self.name)
        out += ';\n'
        return out

class c_var(c_base):
    def __init__(self, name, type=None):
        c_base.__init__(self)
        self.name = name
        self.type = type
    def to_string(self, **kw):
        if self.type:
            if 'no_type' in kw:
                return self.name.to_string(**kw)
            elif len(str(self.name)) == 0:
                return self.type.to_string(**kw)
            else:
                return self.type.to_string(**kw) + " " + str(self.name)
        else:
            return str(self.name)

class c_num(c_base):
    def __init__(self, val):
        c_base.__init__(self)
        self.val = val
    def to_string(self, **kw):
        return str(self.val)

#class c_typed_var(c_base):
#    def __init__(self, type, name):
#        c_base.__init__(self)
#        if isinstance(name, str):
#            self.var = c_var(name)
#        else:
#            self.var = name
#        self.type = type
#    def to_string(self):
#        return self.type.to_string() + " " + self.var.to_string()


class c_expr(c_base):
    C_OP_PLUS = '+'
    C_OP_MINUS = '-'
    C_OP_TIMES = '*'
    C_OP_DIVIDE = '/'
    C_OP_LT = '<'
    C_OP_PREINCR  = '++'

    def __init__(self, op=C_OP_PLUS, arg1=None, arg2=None):
        c_base.__init__(self)
        self._op = op
        self._args.append(arg1)
        if arg2:
            self._args.append(arg2)

    def bind(self):
        return functools.partial(c_expr,self._op)

    @property
    def op(self):
        return self._op

    def to_string(self, **kw):
        out = ''

        child_need_paren = False
        if (self.op == c_expr.C_OP_TIMES or
            self.op == c_expr.C_OP_DIVIDE):
            if self._args[0] and self._args[0].contains(is_add):
                child_need_paren = True
            if self._args[1] and self._args[1].contains(is_add):
                child_need_paren = True

        arg1_str = '<no arg1>'
        if len(self._args) > 0:
            arg1_str = self._args[0].to_string(need_paren=child_need_paren)

        arg2_str = ''
        if len(self._args) > 1:
            arg2_str = self._args[1].to_string(need_paren=child_need_paren)

        need_paren = kw.get('need_paren',False)

        if need_paren:
            out += '('

        if len(self._args) > 1:
            out += arg1_str + ' ' + self._op + ' ' + arg2_str
        elif len(self._args) == 1:
            out += self._op + arg1_str

        if need_paren:
            out += ')'

        return out

def bind(obj, *arg, **kw):
    return functools.partial(obj, *arg, **kw)


#c_add = c_expr(op=c_expr.C_OP_PLUS).bind()
c_add = bind(c_expr, c_expr.C_OP_PLUS)
c_sub = bind(c_expr, c_expr.C_OP_MINUS)
c_div = c_expr(op=c_expr.C_OP_DIVIDE).bind()
c_less_than = c_expr(op=c_expr.C_OP_LT).bind()
c_pre_incr = c_expr(op=c_expr.C_OP_PREINCR).bind()


class c_assign(c_base):
    C_ASSIGN_EQUAL = '='
    C_ASSIGN_PLUS = '+='
    C_ASSIGN_MINUS = '-='

    def __init__(self, lhs=None, rhs=None, op=C_ASSIGN_EQUAL):
        c_base.__init__(self)
        self._args.append(lhs)
        self._args.append(rhs)
        self._op = op

    def bind(self):
        return functools.partial(c_assign,op=self._op)

    def to_string(self, **kw):
        lhs = self._args[0]
        rhs = self._args[1]
        out = get_indent(**kw)
        if lhs:
            out += lhs.to_string(**kw)
            out += ' ' + self._op + ' '
        if rhs:
            out += rhs.to_string(**kw)
        if 'no_end_line' not in kw:
            out += ";\n"
        return out

#c_assign_plus = c_assign(op=c_assign.C_ASSIGN_PLUS).bind()
c_assign_plus = bind(c_assign,op=c_assign.C_ASSIGN_PLUS)
c_assign_minus = c_assign(op=c_assign.C_ASSIGN_MINUS).bind()

class c_for(c_base):
    def __init__(self, init=None, test=None, incr=None, body=None):
        c_base.__init__(self)
        self._args.append(init)
        self._args.append(test)
        self._args.append(incr)
        if body:
            self._args.append(body)

    def to_string(self, **kw):
        indent = get_indent(**kw)
        out = indent
        kw2 = kw.copy()
        if 'indent' in kw2:
            del kw2['indent']
        out = indent + 'for('
        if self._args[0]:
            out += self._args[0].to_string(no_end_line=True, **kw2)
        out += ";"
        if self._args[1]:
            out += self._args[1].to_string(**kw2)
        out += ";"
        if self._args[2]:
            out += self._args[2].to_string(**kw2)
        out += ') {\n'
        if 'indent' in kw:
            kw['indent'] += c_indent_spaces
        for a in self._args[3:]:
            out += a.to_string(**kw)
        out += indent + '}\n'
        return out


class c_block(c_base):
    def __init__(self, *args):
        c_base.__init__(self)
        self.add_statement(*args)

    def add_statement(self, *stmts):
        self._args.extend(stmts)

    def to_string(self, **kw):
        out = ''
        for a in self._args:
            out += a.to_string(indent=c_indent_spaces, **kw)
        return out

class c_stmt(c_base):
    def __init__(self, *args):
        c_base.__init__(self)
        self._args.extend(args)

    def to_string(self, **kw):
        out = get_indent(**kw)
        for a in self._args:
            out += str(a) + ';'
        out += '\n'
        return out

class c_string(c_base):
    def __init__(self, val):
        c_base.__init__(self)
        self._val = val

    def to_string(self, **kw):
        return '"' + self._val + '"'


class c_function_def(c_base):
    def __init__(self, func_type, block=None):
        c_base.__init__(self)
        self.type = func_type
        if block:
            self._args.append(block)

    def to_string(self, **kw):
        out = str(self.type)
        if len(self._args) > 0:
            out += "{\n"
            out += str(self._args[0])
            out += "}\n"
        else:
            out += " {}\n"
        #out = str(self.type)%{'name':str(self.name)} + '('  ','.join(self._args) + ')'
        return out


class c_declaration(c_base):
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def to_string(self, **kw):
        out = str(self.type)%{'name':str(self.name)}
        return out

class c_func_type(c_base):
    def __init__(self, ret_type, *args):
        c_base.__init__(self)
        self._args.append(ret_type)
        self._args.extend(args)

    def to_string(self, **kw):
        ret_type = self._args[0]
        name = ret_type.name
        if 'name' in kw:
            name = kw['name']
        out = str(ret_type.type) + ' ' + str(name) + '('
        out += ','.join([str(a) for a in self._args[1:]])
        out += ')'
        return out

class c_func_decl(c_base):
    def __init__(self, func_type):
        c_base.__init__(self)
        self._args.append(func_type)

    def to_string(self, **kw):
        out = self._args[0].to_string()
        out += ";\n"
        return out

class c_return(c_base):
    def __init__(self, arg=None):
        c_base.__init__(self)
        if arg:
            self._args.append(arg)

    def to_string(self, **kw):
        out = get_indent(**kw) + "return"
        if len(self._args) > 0:
            out += " " + str(self._args[0])
        out += ";\n"
        return out

class c_function_call(c_base):
    def __init__(self, name, *args):
        c_base.__init__(self)
        self.name = name
        self._args.extend(args)

    def to_string(self, **kw):
        out = self.name + '('
        out += ','.join([str(a) for a in self._args])
        out += ')'
        return out


class pp_include(c_base):
    INCLUDE_TYPE_SYSTEM = 1
    INCLUDE_TYPE_LOCAL = 2

    def __init__(self, include_file, include_type = INCLUDE_TYPE_SYSTEM):
        c_base.__init__(self)
        self.include_file = include_file
        self.include_type = include_type

    def _quote_delim(self):
        if self.include_type == self.INCLUDE_TYPE_SYSTEM:
            return '<>'
        return '""'

    def to_string(self, **kw):
        s = '#include '
        s += self._quote_delim()[0]
        s += self.include_file
        s += self._quote_delim()[1]
        s += '\n'

        return s

pp_include_local = bind(pp_include, include_type=pp_include.INCLUDE_TYPE_LOCAL)

class pp_define(c_base):
    def __init__(self, name, value=None):
        c_base.__init__(self)
        self._args.append(name)
        if value:
            self._args.append(value)

    def to_string(self, **kw):
        s = '#define '
        s += self._args[0]
        if len(self._args) > 1:
            s += ' ' + self._args[1]
        return s

class pp_ifdef(c_base):
    def __init__(self, expr):
        c_base.__init__(self)
        self._args.append(expr)


    def to_string(self, **kw):
        s = '#ifdef '
        s += str(self._args[0])
        s += '#endif'

def test_include():
    tree = pp_include('stdio.h')
    print tree.to_string()

def test_void_func():
    #void_func = c_function_def('func',c_double_type)
    func_type = c_function_type(c_double, c_var('i',c_int), c_double('sum'))
    void_func_decl = c_declaration('func', func_type)
    #void_func_decl = func_type('func')
    #inti = c_int_type('i')
    print void_func_decl.to_string()


if __name__ == '__main__':
    #test_include()
    test_void_func()
