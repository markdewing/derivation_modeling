
from sympy import *
from sympy.prototype.codegen.lang_c import *
from sympy.prototype.codegen.sympy_to_c import *
from sympy.prototype.codegen.transforms import extract_integrals

# convert an integral

def convert_one_integral(e, func_trans=[], unique_id=''):
    class_list = [] 
    var_list = [d[0] for d in e.limits]
    print 'var_list = ',var_list

    # generate the innermost routine, the one that actually evaluates the function 
    v = var_list[-1]
    args = []
    for a in var_list:
        if a.is_Integer:
            args.append(c_int(str(a)))
        elif str(a) == 'f':
            args.append(c_var(str(a),c_type(kw['func_type_name'])))
        else:
            args.append(c_double(str(a))) 

    func_type = c_func_type(c_double(unique_id + 'f_'+str(v)),*args)
    fb = c_block()
    func = c_function_def(func_type, fb)

    body = c_return(expr_to_c(func_trans=func_trans)(e.function))
    fb.add_statement(body)
    class_list.append(func)

    # generate increasingly outer functions
    n = c_var('n')

    #elist = [(idx,v) for idx,v in enumerate(var_list[:-1])]
    elist = [(idx,v) for idx,v in enumerate(var_list)]
    elist.reverse()
    for idx,v in elist[1:]:
    #for idx,v in elist:
        inp_args = []
        for a in var_list[:idx+1]:
            if a.is_Integer:
                inp_args.append(c_int(str(a)))
            elif str(a) == 'f':
                inp_args.append(c_var(str(a),c_type(kw['func_type_name'])))
            else:
                inp_args.append(c_double(str(a))) 

        f_type = c_func_type(c_double(unique_id+ 'f_'+str(v)),*inp_args)
        fb = c_block()
        f = c_function_def(f_type, fb)
        a = str(e.limits[idx-1][1])
        b = str(e.limits[idx-1][2])
        #a = str(e.limits[idx+1][1])
        #b = str(e.limits[idx+1][2])
        other_args = [c_var(arg) for arg in var_list[:idx+1]]
        #trap_call = c_function_call('trap'+str(idx+1),c_var(a), c_var(b), c_var(unique_id + 'f_'+str(var_list[idx+1])),n,*other_args)

        func_to_call_name = unique_id + 'f_' + str(var_list[idx+1])
        print 'will call',idx,func_to_call_name
        #trap_call = c_function_call('trap'+str(idx+1),c_var(a), c_var(b), c_var(unique_id + 'f_'+str(var_list[idx-1])),n,*other_args)
        trap_call = c_function_call('trap'+str(idx+1),c_var(a), c_var(b), c_var(func_to_call_name),n,*other_args)
        fb.add_statement(c_assign(c_double('v'),trap_call))
        fb.add_statement(c_return(c_var('v')))
        class_list.append(f)


    a = str(e.limits[0][1])
    b = str(e.limits[0][2])
    #call = py_function_call('trap0',py_arg_list(py_var(a), py_var(b), py_var('f_'+var_list[0]),n))
    call = c_function_call('trap0',c_var(a), c_var(b), c_var(unique_id + 'f_'+str(var_list[0])),n)
    #v = c_double('v')
    #int_val = c_assign(v,call)
    class_list.append(call)
    #print_val = c_print_stmt(v)
    return class_list

def convert_integral(e, transforms=[]):

    trap_inc = pp_include_local('ctrap_gen.h')

    class_list = [trap_inc, pp_include('math.h'), pp_include('stdio.h')]
    define_n = c_assign(c_int('n'),c_num(10))
    class_list.append(define_n)

    ft = {}
    for sym,decl in transforms:
        f = decl.final().rhs
        name = decl.output_name
        print 'generating ',name
        func =  convert_simple_func(f,func_name=name)
        class_list.append(func)
        ft[str(sym)] = name

    main_type = c_func_type(c_int('main'))
    main_b = c_block()
    main = c_function_def(main_type,main_b)

    n = c_var('n')

    ints,e2 = extract_integrals()(e)

    for name, int_expr in ints:
        var = c_double(name) 
        clist = convert_one_integral(int_expr,func_trans=ft, unique_id=name)
        print 'clist',clist
        #class_list.append(clist[0])
        class_list.extend(clist[:-1])
        #print 'clist',clist[0],clist[1]
        main_b.add_statement(c_assign(var, clist[-1]))

    v = c_double('v')
    int_val = c_assign(v,expr_to_c()(e2))


    # generate the innermost routine, the one that actually evaluates the function 
#    v = var_list[-1]
#    args = []
#    for a in var_list:
#        if a.is_Integer:
#            args.append(c_int(str(a)))
#        elif str(a) == 'f':
#            args.append(c_var(str(a),c_type(kw['func_type_name'])))
#        else:
#            args.append(c_double(str(a))) 
#
#    func_type = c_func_type(c_double('f_'+str(v)),*args)
#    fb = c_block()
#    func = c_function_def(func_type, fb)
#
#    body = c_return(expr_to_c(func_trans=ft)(e.function))
#    fb.add_statement(body)
#    class_list.append(func)
#
#    # generate increasingly outer functions
#
#    elist = [(idx,v) for idx,v in enumerate(var_list[:-1])]
#    elist.reverse()
#    for idx,v in elist:
#        inp_args = []
#        for a in var_list[:idx+1]:
#            if a.is_Integer:
#                inp_args.append(c_int(str(a)))
#            elif str(a) == 'f':
#                inp_args.append(c_var(str(a),c_type(kw['func_type_name'])))
#            else:
#                inp_args.append(c_double(str(a))) 
#
#        f_type = c_func_type(c_double('f_'+str(v)),*inp_args)
#        fb = c_block()
#        f = c_function_def(f_type, fb)
#        a = str(e.limits[idx+1][1])
#        b = str(e.limits[idx+1][2])
#        other_args = [c_var(arg) for arg in var_list[:idx+1]]
#        trap_call = c_function_call('trap'+str(idx+1),c_var(a), c_var(b), c_var('f_'+str(var_list[idx+1])),n,*other_args)
#        fb.add_statement(c_assign(c_double('v'),trap_call))
#        fb.add_statement(c_return(c_var('v')))
#        class_list.append(f)
#
#
#    a = str(e.limits[0][1])
#    b = str(e.limits[0][2])
#    #call = py_function_call('trap0',py_arg_list(py_var(a), py_var(b), py_var('f_'+var_list[0]),n))
#    call = c_function_call('trap0',c_var(a), c_var(b), c_var('f_'+str(var_list[0])),n)
#    v = c_double('v')
#    int_val = c_assign(v,call)
    #print_val = c_print_stmt(v)


    main_b.add_statement(int_val)
    print_val = c_stmt(c_function_call('printf',c_string("val = %g\\n"), c_var('v')))
    main_b.add_statement(print_val)
    main_b.add_statement(c_return(c_num(0)))
    class_list.append(main)
    

    return c_block(*class_list)


#def convert_one_integral(e):
#    # create function
#    int_var = e.limits[0][0]
#    func = py_function_def(py_var('f'),py_arg_list(py_var(str(int_var))))
#    body = py_return_stmt(expr_to_py(e.function))
#    func.add_statement(body)
#
#
#    trap_import = py_import('ptrap_gen',False,'trap')
#
#    #call trap(a,b,f,n)
#    a = str(e.limits[0][1])
#    b = str(e.limits[0][2])
#
#    
#    n = py_var('n')
#    define_n = py_assign_stmt(n,py_num(10))
#    call = py_function_call('trap',py_arg_list(py_var(a), py_var(b), py_var('f'),n))
#    v = py_var('v')
#    int_val = py_assign_stmt(v,call)
#    print_val = py_print_stmt(v)
#
#    block = py_stmt_block(trap_import,func,define_n,int_val,print_val)
#
#    return block


if __name__ == '__main__':
    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    #e = Integral(x*y,(x,0,1),(y,2,3))  
    e = Integral(x*y*z,(x,0,1),(y,2,3),(z,4,5))  
    #e = Integral(x,(x,0,1))  
    b = convert_integral(e)
    print b
