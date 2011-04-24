
from sympy import * 
from lang_py import *
#from print_tree import *
from pattern_match import AutoVar,AutoVarInstance,Match

index_trans = {}
extra_args = []

# returns tuple of (sum term, other terms)
def extract_sum(e):
    m = Match(e)

    if m(Sum):
        return (e, Symbol('total'))
        #return (e, None)

    # not sure how to express this any better?
    if (len(e.args)) == 0:
        return (None,e)

    # default 
    arg = e.args
    sum = None
    new_args = []
    for a in arg:
        (sums, other) = extract_sum(a)
        if sums:
            sum = sums
        #if other:
        new_args.append(other) 
        #if not other:
        #    other = Symbol('total') 


    return (sum, e.new(*new_args))


# returns set of free variables (and functions)
def extract_free_variables(e):
    m = Match(e)

    if m(Sum):
        limit_var = e.limits[0][0] 
        vars = extract_free_variables(e.function)
        lower = extract_free_variables(e.limits[0][1])
        upper = extract_free_variables(e.limits[0][2])
        vars.update(lower)
        vars.update(upper)
        if limit_var in vars:
            vars.remove(limit_var)
        return vars

    if m(Symbol):
        return set([e])

    if m.type(FunctionClass): 
        return set([type(e)])

    # not sure how to express this any better?
    if (len(e.args)) == 0:
        return set([])

    # default 
    arg = e.args
    free_vars = set()
    for a in arg:
        other = extract_free_variables(a)
        free_vars.update(other) 

    return free_vars
    

def convert(e,definitions=[],func_name='func'):
    global extra_args 
    free_vars = extract_free_variables(e) 
    for d in definitions:
        def_free_vars = extract_free_variables(d.rhs)
        free_vars.update(def_free_vars)
        free_vars.remove(d.lhs)
    func_args = [py_var(str(a)) for a in sorted(free_vars,key=lambda x:str(x))]
    func_args.extend([py_var(a) for a in extra_args])
    (sum, other) = extract_sum(e)
    ep = expr_to_py(other)
    init = py_assign_stmt(py_var('total'),py_num(0),py_assign_stmt.PY_ASSIGN_EQUAL)
    sum = sum_to_py(sum)
    fd = py_function_def(func_name,py_arg_list(*func_args))
    for d in definitions:
        define = py_assign_stmt(py_var(str(d.lhs)), expr_to_py(d.rhs), py_assign_stmt.PY_ASSIGN_EQUAL)
        fd.add_statement(define)
    fd.add_statement(init,sum)
    if other:
        final = py_assign_stmt(py_var('final'),ep,py_assign_stmt.PY_ASSIGN_EQUAL)
    fd.add_statement(final)
    fd.add_statement(py_return_stmt(py_var('final')))
    
    return fd
    
def sum_to_py(e):
    v = AutoVar()
    m = Match(e)

    if m(Sum, v.e1, v.e2):
        lower_limit = expr_to_py(v.e2[1])
        upper_limit = expr_to_py((v.e2[2]+1))
        body = py_assign_stmt(py_var('total'),expr_to_py(v.e1),py_assign_stmt.PY_ASSIGN_PLUS)
        loop =  py_for(expr_to_py(v.e2[0]),py_function_call('range',lower_limit,upper_limit),body)
        return loop

def expr_to_py(e):
    '''Convert sympy expression to python syntax tree'''
    v = AutoVar()
    m = Match(e)

    # subtraction
    if m(Add, (Mul, S.NegativeOne, v.e1), v.e2):
        return py_expr(py_expr.PY_OP_MINUS, expr_to_py(v.e2), expr_to_py(v.e1))


    if m(Add, v.e1, v.e2):
        return py_expr(py_expr.PY_OP_PLUS, expr_to_py(v.e1), expr_to_py(v.e2))

    # reciprocal
    if m(Pow, v.e2, S.NegativeOne):
        return py_expr(py_expr.PY_OP_DIVIDE, py_num(1.0), expr_to_py(v.e2))

    # division
    if m(Mul, v.e1, (Pow, v.e2, S.NegativeOne)):
        return py_expr(py_expr.PY_OP_DIVIDE, expr_to_py(v.e1), expr_to_py(v.e2))

    if m(Mul, S.NegativeOne, v.e1):
        return py_expr(py_expr.PY_OP_MINUS, expr_to_py(v.e1))

    if m(Mul, v.e1, v.e2):
        return py_expr(py_expr.PY_OP_TIMES, expr_to_py(v.e1), expr_to_py(v.e2))

    if m(exp, v.e1):
        return py_function_call('math.exp', expr_to_py(v.e1))

    if m(numbers.Pi):
        return py_var("math.pi")

    if m(Indexed, (IndexedBase, v.e1), (Idx, v.e2)):
        global index_trans
        if str(v.e1) in index_trans:
            idx_var,idx_expr = index_trans[str(v.e1)]
            ex = expr_to_py(idx_expr.subs(idx_var,v.e2))
            return ex
        return None
        

    # alternate syntax for the pattern match?
    #if m(Pow, v.e1 ** v.e2):
    if m(Pow, v.e1, v.e2):
        return py_expr(py_expr.PY_OP_POW, expr_to_py(v.e1), expr_to_py(v.e2))

    # function call
    if m.type(FunctionClass):
        global extra_args
        args = [expr_to_py(a) for a in e.args]
        args.extend([py_var(a) for a in extra_args])
        return py_function_call(str(type(e)), *args)

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

if __name__ == '__main__':
    a = Symbol('a')
    b = Symbol('b')
    r = Symbol('r')
    f = Function('f')
    i = Symbol('i',integer=True)
    x = IndexedBase('x')
    index_trans['x'] = py_expr(py_expr.PY_OP_PLUS,py_var('a'),py_expr(py_expr.PY_OP_TIMES,py_var('i'),py_var('h')))
    #e = x[i]
    #e = 1/b
    #e = a-5*b
    #e = 1+a+b
    e = exp(-4.0/a**3)
    #e = -3*exp(-a)
    #e = 1 + f(b) + Sum(f(a),(a,1,10))
    #print 'args',len(e.args),[type(a) for a in e.args]
    print_tree(e)
    r = expr_to_py(e)

    #r = convert(e)
    print 'r = ', type(r),str(r)
    #print_tree(r)
    



