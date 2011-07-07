
from sympy import *
from lang_c import *
from pattern_match import AutoVar,AutoVarInstance,Match
from transforms import extract_free_variables, extract_sum

def sum_to_c(e, **kw):
    v = AutoVar()
    m = Match(e)

    ec = expr_to_c(**kw)
    if m(Sum, v.e1, v.e2):
        lower_limit = ec(v.e2[1])
        upper_limit = ec((v.e2[2]+1))
        body = c_assign_plus(c_var('total'), ec(v.e1))
        #loop =  c_for(ec(v.e2[0]),function_call('range',lower_limit,upper_limit),body)
        loop_idx = c_var(str(v.e2[0]))
        typed_loop_idx = c_int(str(v.e2[0]))
        loop_init = c_assign(typed_loop_idx, lower_limit)
        loop_test = c_less_than(loop_idx, upper_limit)
        loop_inc = c_pre_incr(loop_idx)
        loop =  c_for(loop_init, loop_test, loop_inc, body)
        return loop


class expr_to_c(object):
    def __init__(self, scope={}, index_trans={}, extra_args=[], func_trans={}):
        self._scope = scope
        self._index_trans = index_trans
        self._extra_args = extra_args
        self._func_trans = func_trans

    def __call__(self, e):
        v = AutoVar()
        m = Match(e)

        # subtraction
        if m(Add, v.e1, (Mul, S.NegativeOne, v.e2)):
            return c_sub(self(v.e1), self(v.e2))

        if m(Add, v.e1, v.e2):
            #return c_expr(c_expr.C_OP_PLUS, self(v.e1), self(v.e2))
            return c_add(self(v.e1), self(v.e2))

        # reciprocal
        if m(Pow, v.e2, S.NegativeOne):
            return c_expr(c_expr.C_OP_DIVIDE, c_num(1.0), self(v.e2))

        # division
        if m(Mul, v.e1, (Pow, v.e2, S.NegativeOne)):
            #return c_expr(c_expr.C_OP_DIVIDE, self(v.e1), self(v.e2))
            return c_div(self(v.e1), self(v.e2))

        if m(Mul, v.e1, v.e2):
            return c_expr(c_expr.C_OP_TIMES, self(v.e1), self(v.e2))

        if m(exp, v.e1):
            return c_function_call('exp', self(v.e1))

        if m(Pow, v.e1, v.e2):
            return c_function_call('pow', self(v.e1), self(v.e2))

        #if m(Indexed, (IndexedBase, v.e1), (Idx, v.e2)):
        if m(Indexed, (IndexedBase, v.e1), v.e2):
            if str(v.e1) in self._index_trans:
                idx_var, idx_expr = self._index_trans[str(v.e1)]
                ex = self(idx_expr.subs(idx_var, v.e2))
                return ex
            return None

        if m.type(FunctionClass):
            args = [self(a) for a in e.args]
            args.extend([c_var(a) for a in self._extra_args])
            name = str(type(e))
            if name in self._func_trans:
                name = self._func_trans[name]
            return c_function_call(name, *args)

        if m(Symbol):
            #if str(e) in self._scope:
            #    return self._scope[str(e)]
            ## automatically create the variable if it does not exist in the symbol table
            ## could also issue a warning or an error here
            var = c_var(str(e))
            #self._scope[str(e)] = var
            return var

        if m.exact(S.Half):
            return c_div(c_num(1.0), c_num(2.0))

        if m(Integer):
            return c_num(e.p)

        if m(Float):
            return c_num(e.num)

        print 'no match',type(e)
        return None

def convert(e, definitions=[], func_name='func', extra_args=[], index_trans={}, **kw):
    free_vars = extract_free_variables(e)
    for d in definitions:
        def_free_vars = extract_free_variables(d.rhs)
        free_vars.update(def_free_vars)
        free_vars.remove(d.lhs)
    #func_args = [c_var(str(a)) for a in sorted(free_vars,key=lambda x:str(x))]
    func_args = []
    for a in sorted(free_vars,key=lambda x:str(x)):
        if a.is_Integer:
            func_args.append(c_int(str(a)))
        elif str(a) == 'f':
            func_args.append(c_var(str(a),c_type(kw['func_type_name'])))
        else:
            func_args.append(c_double(str(a)))

    func_args.extend([c_double(a) for a in extra_args])

    func_type = c_func_type(c_double(func_name), *func_args)
    func_decl = c_func_decl(func_type)

    e_args = [c_double() for a in extra_args]
    inner_func_type = c_func_type(c_double(), c_double(), *e_args)
    func_typedef = c_typedef(kw['func_type_name'], inner_func_type)

    ft = kw.get('func_trans',{})

    # break expression into the sum (and children) and everything else (above the sum)
    (sum, other) = extract_sum(e)
    ep = expr_to_c(index_trans=index_trans, extra_args=extra_args, func_trans=ft)(other)

    init = c_assign(c_double('total'), c_num(0))
    sum = sum_to_c(sum, extra_args=extra_args, index_trans=index_trans)
    body = c_block()
    fd = c_function_def(func_type, body)
    for d in definitions:
        define = c_assign(c_double(str(d.lhs)), expr_to_c()(d.rhs))
        body.add_statement(define)

    body.add_statement(init, sum)
    if other:
        final = c_assign(c_double('final'), ep)
    body.add_statement(final)
    body.add_statement(c_return(c_var('final')))

    return fd, c_block(func_typedef, func_decl)

def convert_simple_func(e, func_name='func', extra_args=[]):
    free_vars = extract_free_variables(e)
    func_args = []
    for a in sorted(free_vars,key=lambda x:str(x)):
        if a.is_Integer:
            func_args.append(c_int(str(a)))
        else:
            func_args.append(c_double(str(a)))

    func_args.extend([c_double(a) for a in extra_args])

    func_type = c_func_type(c_double(func_name), *func_args)
    func_decl = c_func_decl(func_type)

    e_args = [c_double() for a in extra_args]

    ep = expr_to_c(extra_args=extra_args)(e)

    body = c_block()
    fd = c_function_def(func_type, body)

    body.add_statement(c_return(ep))

    return fd


if __name__ == '__main__':
    a = Symbol('a')
    b = Symbol('b')
    c = a+b

    print expr_to_c()(c)
