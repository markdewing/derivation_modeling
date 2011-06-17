
# Represent a simple 'Hello, World' program using the python and C trees

from sympy.prototype.codegen.lang_py import *
from sympy.prototype.codegen.lang_c import *

def example_python():
    body = py_stmt_block()

    hello_func = py_function_def('hello')
    hello_func.add_statement(py_print_stmt(py_string("Hello, World")))
    body.add_statements(hello_func)
    main = py_if(py_expr(py_expr.PY_OP_EQUAL, py_var('__name__'),py_string('__main__')))
    main.add_true_statement(py_expr_stmt(py_function_call('hello')))
    body.add_statements(main)

    f = open('hello_py.py','w')
    f.write(body.to_string())
    f.close()

def example_c():
    body = c_block()
    body.add_statement(pp_include('stdio.h'))
    main_body = c_block()
    main = c_function_def(c_func_type(c_int('main')), main_body)
    main_body.add_statement(c_stmt(c_function_call("printf",c_string("Hello, World\\n"))))
    main_body.add_statement(c_return(c_num(0)))
    body.add_statement(main)
    f = open('hello_c.c','w')
    f.write(body.to_string())
    f.close()

if __name__ == '__main__':
    example_python()
    example_c()
