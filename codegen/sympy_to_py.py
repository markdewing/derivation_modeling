
from sympy import *
from lang_py import *
from pattern_match import AutoVar,AutoVarInstance,Match
from transforms import extract_free_variables, extract_sum




def convert(e,definitions=[], func_name='func', extra_args=[], index_trans={}):

    # function arguments = free variables + extra args

    free_vars = extract_free_variables(e)
    for d in definitions:
        def_free_vars = extract_free_variables(d.rhs)
        free_vars.update(def_free_vars)
        free_vars.remove(d.lhs)
    func_args = [py_var(str(a)) for a in sorted(free_vars,key=lambda x:str(x))]
    func_args.extend([py_var(a) for a in extra_args])

    epy = expr_to_py(extra_args=extra_args, index_trans=index_trans)
    ep = epy(e)

    fd = py_function_def(func_name,py_arg_list(*func_args))
    for d in definitions:
        define = py_assign_stmt(py_var(str(d.lhs)), expr_to_py()(d.rhs), py_assign_stmt.PY_ASSIGN_EQUAL)
        fd.add_statement(define)
    fd.add_statement(*epy._pre_statements)
    fd.add_statement(py_return_stmt(ep))

    return fd




def sum_to_py(e, **kw):
    v = AutoVar()
    m = Match(e)

    ep = expr_to_py(**kw)
    if m(Sum, v.e1, v.e2):
        lower_limit = ep(v.e2[1])
        upper_limit = ep((v.e2[2]+1))
        body = py_assign_stmt(py_var('total'),ep(v.e1),py_assign_stmt.PY_ASSIGN_PLUS)
        loop =  py_for(ep(v.e2[0]),py_function_call('range',lower_limit,upper_limit),body)
        return loop 

class expr_to_py(object):
    '''Convert sympy expression to python syntax tree'''
    def __init__(self, index_trans={}, extra_args=[], func_trans={}):
        # functions that describes how to translate indexed values
        self._index_trans = index_trans

        # list of extra arguments to pass through a function call
        self._extra_args = extra_args

        # Function's name that should be used in the generated code
        self._func_trans = func_trans


        # Items that should go before the current statement
        self._pre_functions = []
        self._pre_statements = []
        self._imports = []

    def __call__(self, e):
        v = AutoVar()
        m = Match(e)

        # subtraction
        if m(Add, (Mul, S.NegativeOne, v.e1), v.e2):
            return py_expr(py_expr.PY_OP_MINUS, self(v.e2), self(v.e1))


        if m(Add, v.e1, v.e2):
            return py_expr(py_expr.PY_OP_PLUS, self(v.e1), self(v.e2))

        # reciprocal
        if m(Pow, v.e2, S.NegativeOne):
            return py_expr(py_expr.PY_OP_DIVIDE, py_num(1.0), self(v.e2))

        # division
        if m(Mul, v.e1, (Pow, v.e2, S.NegativeOne)):
            return py_expr(py_expr.PY_OP_DIVIDE, self(v.e1), self(v.e2))

        if m(Mul, S.NegativeOne, v.e1):
            return py_expr(py_expr.PY_OP_MINUS, self(v.e1))

        if m(Mul, v.e1, v.e2):
            return py_expr(py_expr.PY_OP_TIMES, self(v.e1), self(v.e2))

        if m(exp, v.e1):
            return py_function_call('math.exp', self(v.e1))

        if m(numbers.Pi):
            return py_var("math.pi")

        if m(Indexed, (IndexedBase, v.e1), v.e2):
            if str(v.e1) in self._index_trans:
                idx_var,idx_expr = self._index_trans[str(v.e1)]
                ex = self(idx_expr.subs(idx_var,v.e2))
                return ex
            return None


        # alternate syntax for the pattern match?
        #if m(Pow, v.e1 ** v.e2):
        if m(Pow, v.e1, v.e2):
            return py_expr(py_expr.PY_OP_POW, self(v.e1), self(v.e2))

        # function call
        if m.type(FunctionClass):
            args = [self(a) for a in e.args]
            args.extend([py_var(a) for a in self._extra_args])
            name = str(type(e))
            if name in self._func_trans:
                name = self._func_trans[name]
            return py_function_call(name, *args)


        if m(Integral):
            return self.convert_integral(e)

        if m(Sum, v.e1, v.e2):
            init = py_assign_stmt(py_var('total'),py_num(0),py_assign_stmt.PY_ASSIGN_EQUAL)

            lower_limit = self(v.e2[1])
            upper_limit = self((v.e2[2]+1))
            body = py_assign_stmt(py_var('total'),self(v.e1),py_assign_stmt.PY_ASSIGN_PLUS)
            loop =  py_for(self(v.e2[0]),py_function_call('range',lower_limit,upper_limit),body)
            self._pre_statements.append(init)
            self._pre_statements.append(loop)
            return py_var('total')

        if m(Symbol):
            return py_var(str(e))

        if m(Integer):
            return py_num(e.p)

        if m(Float):
            return py_num(e.num,promote_to_fp=True)

        # alternate syntax for the pattern match?
        # m(Rational, m.numerator(v.e1), m.denominator(v.e2))
        # m(Rational, v.e1 / v.e2)
        if m(Rational):
            (n,d) = e.as_numer_denom()
            return py_expr(py_expr.PY_OP_DIVIDE, py_num(n), py_num(d, True))

# convert multidimensional integral as iterated integral
    def convert_integral(self, e):
        var_list = [str(d[0]) for d in e.limits]
    
        import_list = ['trap'+str(i) for i in range(len(var_list))]
        trap_import = py_import('ptrap_gen',False, *import_list)
        self._imports.append(trap_import)
    
    
        n = py_var('n')
        for idx,v in enumerate(var_list[:-1]):
            inp_args = [py_var(arg) for arg in var_list[:idx+1]]
            f = py_function_def('f_'+v,py_arg_list(*inp_args))
            a = str(e.limits[idx+1][1])
            b = str(e.limits[idx+1][2])
            other_args = [py_var(arg) for arg in var_list[:idx+1]]
            trap_call = py_function_call('trap'+str(idx+1),py_arg_list(py_var(a), py_var(b), py_var('f_'+var_list[idx+1]),n,*other_args))
            f.add_statement(py_assign_stmt(py_var('v'),trap_call))
            f.add_statement(py_return_stmt(py_var('v')))
            self._pre_functions.append(f)
    
        # generate the innermost routine, the one that actually evaluates the function 
        v = var_list[-1]
        args = [py_var(a) for a in var_list]
        func = py_function_def('f_'+v,py_arg_list(*args))
        body = py_return_stmt(self(e.function))
        func.add_statement(body)
        self._pre_functions.append(func)
    
    
        a = str(e.limits[0][1])
        b = str(e.limits[0][2])
        #define_n = py_assign_stmt(n,py_num(10))
        call = py_function_call('trap0',py_arg_list(py_var(a), py_var(b), py_var('f_'+var_list[0]),n))
        
        return call
        #return {'core':call, 'pre':class_list}

def convert_simple_func(e, func_name='func', extra_args=[]):
    free_vars = extract_free_variables(e)
    func_args = []
    for a in sorted(free_vars, key=lambda x:str(x)):
        func_args.append(py_var(str(a)))

    func_args.extend([py_var(a) for a in extra_args])

    ep = expr_to_py(extra_args=extra_args)(e)

    fd = py_function_def(func_name, py_arg_list(*func_args))
    fd.add_statement(py_return_stmt(ep))

    return fd

if __name__ == '__main__':
    a = Symbol('a')
    b = Symbol('b')
    r = Symbol('r')
    f = Function('f')
    i = Symbol('i',integer=True)
    x = IndexedBase('x')
    index_trans = {}
    index_trans['x'] = py_expr(py_expr.PY_OP_PLUS,py_var('a'),py_expr(py_expr.PY_OP_TIMES,py_var('i'),py_var('h')))
    #e = x[i]
    #e = 1/b
    #e = a-5*b
    #e = 1+a+b
    e = exp(-4.0/a**3)
    #e = -3*exp(-a)
    #e = 1 + f(b) + Sum(f(a),(a,1,10))
    #print 'args',len(e.args),[type(a) for a in e.args]
    r = expr_to_py(index_trans=index_trans)(e)

    #r = convert(e)
    print 'r = ', type(r),str(r)


