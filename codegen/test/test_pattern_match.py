
from sympy.prototype.codegen.pattern_match import Match, AutoVar
from sympy import Symbol, Add, Mul, S, FunctionClass, Function, numbers, \
    Integer, Float


def test_empty():
    m = Match(None)
    assert m(Add) == False

def test_Add():
    x = Symbol('x')
    y = Symbol('y')
    m = Match(x+y)
    assert m(Add) == True
    v = AutoVar()
    assert m(Add, v.e1, v.e2) == True
    assert v.e1 == x or  v.e1 == y
    assert v.e2 == x or  v.e2 == y


def test_nested():
    x = Symbol('x')
    y = Symbol('y')
    m = Match(x-y)
    v = AutoVar()
    assert m(Add, (Mul, S.NegativeOne, v.e1), v.e2) == True
    assert v.e1 == y
    assert v.e2 == x


def test_function():
    f = Function('f')
    x = Symbol('x')
    e = f(x)
    m = Match(e)
    assert m(f) == True
    assert m.type(FunctionClass) == True

def test_numbers():
    e = numbers.pi
    m = Match(e)
    assert m(numbers.Pi) == True

def test_singleton():
    e = Integer(1)/2
    m = Match(e)
    assert m.exact(S.Half) == True

def test_values():
    m = Match(Integer(1))
    assert m(Integer) == True
    m2 = Match(Float(2.1))
    assert m2(Float) == True



