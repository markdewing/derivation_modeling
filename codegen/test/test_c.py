
from sympy.prototype.codegen.lang_c import *

def test_var():
    a = c_var('a')
    assert str(a) == 'a'
    b = c_int('b')
    assert str(b) == 'int b'


def test_type():
    i1 = c_type('int')
    assert i1 == c_int
    i2 = c_type('int2')
    assert i1 != i2

def test_assign():
    a1 = c_assign(c_var('a'), c_num(0))
    print str(a1)
    assert str(a1) == 'a = 0;\n'
    a1 = c_assign_plus(c_var('a'), c_num(1))
    assert str(a1) == 'a += 1;\n'

def test_expr():
    a1 = c_add(c_num(1),c_var('b'))
    assert str(a1) == '1 + b'

    p1 = c_pre_incr(c_var('a'))
    assert str(p1) == '++a'

def test_for():
    f1 = c_for()
    assert str(f1) == 'for(;;) {\n}\n'

    f2 = c_for(c_assign(c_var('a'),c_num(1)))
    print f2
    assert str(f2) == 'for(a = 1;;) {\n}\n'

def test_return():
    r1 = c_return()
    assert str(r1) == 'return;\n'

    r2 = c_return(c_var('a'))
    assert str(r2) == 'return a;\n'

def test_typedef():
    t1 = c_typedef('length',c_int())
    print t1
    assert str(t1) == 'typedef int length;\n'

    t2 = c_typedef('FUNC', c_func_type(c_double(), c_double()))
    print t2
    assert str(t2) == 'typedef double FUNC(double);\n'

