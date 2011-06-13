
from sympy.prototype.codegen.lang_c import *
from sympy.prototype.codegen.sympy_to_c import expr_to_c
from sympy import Symbol, sympify

def test_var():
    a = Symbol('a')
    e = expr_to_c()(a)
    assert str(e) == 'a'

def test_add_sym():
    e1 = expr_to_c()(sympify('a+b'))
    # comparing to a string is brittle - can we do better?
    # normalize the string - removing spaces might help?
    assert str(e1) == 'b + a'
    e2 = expr_to_c()(sympify('a+b+c'))
    print str(e2)
    assert str(e2) == 'b + a + c'

def test_add_sym_to_num():
    e = expr_to_c()(sympify('a+1'))
    assert str(e) == '1 + a'

def test_mul():
    e1 = expr_to_c()(sympify('a*b'))
    print 'e1 = ',str(e1)
    assert str(e1) == 'a * b'
    e2 = expr_to_c()(sympify('2*b'))
    assert str(e2) == '2 * b'

def test_add_and_mul():
    e1 = expr_to_c()(sympify('a+2*b'))
    assert str(e1) == '2 * b + a'


def test_div():
    e1 = expr_to_c()(sympify('a/b'))
    assert str(e1) == 'a / b'
    e2 = expr_to_c()(sympify('1.0/b'))
    assert str(e2) == '1.0 / b'




