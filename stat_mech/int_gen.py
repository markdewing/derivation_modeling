
from sympy import *
from sympy.prototype.codegen.lang_py import *
from sympy.prototype.codegen.sympy_to_py import *

# convert an integral


def convert_integral(e):
    var_list = [str(d[0]) for d in e.limits]

    import_list = ['trap'+str(i) for i in range(len(var_list))]
    trap_import = py_import('ptrap_gen',False, *import_list)

    math_import = py_import('math')
    class_list = [trap_import,math_import]
    #for v in var_list[0:-1]:
    #    f = py_class('f_'+v)
    #    init = py_function_def('__init__',py_arg_list(py_var('self'),py_var(var_list[1])))
    #    init.add_statement(py_assign_stmt(py_var('self.'+var_list[1]),py_var(var_list[1])))
    #    call = py_function_def('__call__',py_arg_list(py_var('self'),py_var(v)))
    #    
    #    call.add_statement( py_assign_stmt( py_var(var_list[1]), py_var('self.' + var_list[1])))
    #    call.add_statement( py_assign_stmt( py_var('v'), expr_to_py(e.function)))

    #    call.add_statement( py_return_stmt( py_var('v')))
    #    #call.add_statement( py_return_stmt( py_expr(py_expr.PY_OP_TIMES,py_var('self.'+var_list[1]),py_var(v))))
    #    f.add_method(init)
    #    f.add_method(call)
    #    class_list.append(f)

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
        class_list.append(f)

    # generate the innermost routine, the one that actually evaluates the function 
    v = var_list[-1]
    args = [py_var(a) for a in var_list]
    func = py_function_def('f_'+v,py_arg_list(*args))
    body = py_return_stmt(expr_to_py(e.function))
    func.add_statement(body)
    class_list.append(func)


    #v = var_list[0]
    #f = py_function_def('f_'+v,py_var(v))
    #a = str(e.limits[0][1])
    #b = str(e.limits[0][2])
    #trap_call = py_function_call('trap1',py_arg_list(py_var(a), py_var(b), py_function_call('f_'+var_list[1],py_arg_list(py_var(v))),n))
    #f.add_statement(py_assign_stmt(py_var('v'),trap_call))
    #f.add_statement(py_return_stmt(py_var('v')))

    a = str(e.limits[0][1])
    b = str(e.limits[0][2])
    define_n = py_assign_stmt(n,py_num(10))
    call = py_function_call('trap0',py_arg_list(py_var(a), py_var(b), py_var('f_'+var_list[0]),n))
    v = py_var('v')
    int_val = py_assign_stmt(v,call)
    print_val = py_print_stmt(v)

    define_n = py_assign_stmt(n,py_num(10))
    #class_list.append(f)
    class_list.append(define_n)
    class_list.append(int_val)
    class_list.append(print_val)
    

    return py_stmt_block(*class_list)


def convert_one_integral(e):
    # create function
    int_var = e.limits[0][0]
    func = py_function_def(py_var('f'),py_arg_list(py_var(str(int_var))))
    body = py_return_stmt(expr_to_py(e.function))
    func.add_statement(body)


    trap_import = py_import('ptrap_gen',False,'trap')

    #call trap(a,b,f,n)
    a = str(e.limits[0][1])
    b = str(e.limits[0][2])

    
    n = py_var('n')
    define_n = py_assign_stmt(n,py_num(10))
    call = py_function_call('trap',py_arg_list(py_var(a), py_var(b), py_var('f'),n))
    v = py_var('v')
    int_val = py_assign_stmt(v,call)
    print_val = py_print_stmt(v)

    block = py_stmt_block(trap_import,func,define_n,int_val,print_val)

    return block


if __name__ == '__main__':
    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    #e = Integral(x*y,(x,0,1),(y,2,3))  
    e = Integral(x*y*z,(x,0,1),(y,2,3),(z,4,5))  
    #e = Integral(x,(x,0,1))  
    b = convert_integral(e)
    print b
