#!/usr/bin/python


from sympy import sympify
from sympy_to_py import expr_to_py
from lang_py import *
from print_tree import print_tree
import unittest

class TestVar(unittest.TestCase):
  def test_one(self):
    val = sympify('a+b')
    py = expr_to_py(val)
    self.assertEqual(py.to_string(),'b + a')

class TestNum(unittest.TestCase):
  def test_one(self):
    val = sympify('1')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_num))
    self.assertEqual(py.to_string(),'1')
  def test_pi(self):
    val = sympify('pi')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_var))
    self.assertEqual(py.to_string(),'math.pi')
  def test_rational(self):
    val = sympify('3/4')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_expr))
    self.assertEqual(py.to_string(),'3 / 4.0')

class TestPow(unittest.TestCase):
  def test_one(self):
    val = sympify('a**2')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_expr))
    self.assertEqual(py.to_string(),'a**2')
  def test_inv(self):
    val = sympify('(a/b)**i')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_expr))
    self.assertEqual(py.to_string(),'(a / b)**i')

class TestAdd(unittest.TestCase):
  def test_plus(self):
    val = sympify('x+y')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_expr))
    self.assertEqual(py.to_string(),'y + x')
  def test_minus(self):
    val = sympify('x-y')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_expr))
    self.assertEqual(py.to_string(),'x - y')
  def test_minus2(self):
    val = sympify('x-2*y')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_expr))
    self.assertEqual(py.to_string(),'-2 * y + x')
  def test_minus3(self):
    val = sympify('z-2*y*z')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_expr))
    self.assertEqual(py.to_string(),'z + -2 * y * z')
  def test_minus4(self):
    val = sympify('2*exp(-r)-3*x*exp(-r)')
    py = expr_to_py(val)
    self.assert_(isinstance(py,py_expr))
    self.assertEqual(py.to_string(),'-3 * x * math.exp(-r) + 2 * math.exp(-r)')




if __name__ == '__main__':
  unittest.main()
