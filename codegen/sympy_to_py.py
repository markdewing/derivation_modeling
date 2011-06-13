
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

    # break expression into the sum (and children) and everything else (above the sum)
    (sum, other) = extract_sum(e)
    ep = expr_to_py(extra_args=extra_args, index_trans=index_trans)(other)

    init = py_assign_stmt(py_var('total'),py_num(0),py_assign_stmt.PY_ASSIGN_EQUAL)
    sum = sum_to_py(sum, extra_args=extra_args, index_trans=index_trans)
    fd = py_function_def(func_name,py_arg_list(*func_args))
    for d in definitions:
        define = py_assign_stmt(py_var(str(d.lhs)), expr_to_py()(d.rhs), py_assign_stmt.PY_ASSIGN_EQUAL)
        fd.add_statement(define)
    fd.add_statement(init,sum)
    if other:
        final = py_assign_stmt(py_var('final'),ep,py_assign_stmt.PY_ASSIGN_EQUAL)
    fd.add_statement(final)
    fd.add_statement(py_return_stmt(py_var('final')))

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

        if m(Symbol):
            return py_var(str(e))

        if m(Integer):
            return py_num(e.p)

        if m(Real):
            return py_num(e.num,promote_to_fp=True)

        # alternate syntax for the pattern match?
        # m(Rational, m.numerator(v.e1), m.denominator(v.e2))
        # m(Rational, v.e1 / v.e2)
        if m(Rational):
            (n,d) = e.as_numer_denom()
            return py_expr(py_expr.PY_OP_DIVIDE, py_num(n), py_num(d, True))

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


