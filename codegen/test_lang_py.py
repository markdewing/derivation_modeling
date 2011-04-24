#!/usr/bin/python

from lang_py import *
import unittest

class TestVar(unittest.TestCase):
  def test_one(self):
    val = py_var('a')
    self.assertEqual(val.to_string(),'a')

class TestNum(unittest.TestCase):
  def test_one(self):
    val = py_num('1')
    self.assertEqual(val.to_string(),'1')
  def test_two(self):
    val = py_num(2)
    self.assertEqual(val.to_string(),'2')

class TestExpr(unittest.TestCase): 
  def test_one(self):
    val = py_expr(py_expr.PY_OP_PLUS,py_var('a'),py_var('b'))
    self.assertEqual(val.to_string(),'a + b')
  def test_two(self):
    val = py_expr(py_expr.PY_OP_TIMES,py_var('a'),py_var('b'))
    self.assertEqual(val.to_string(),'a * b')
  def test_minus(self):
    minus = py_expr(py_expr.PY_OP_MINUS,py_var('a'))
    self.assertEqual(minus.to_string(),'-a')
  def test_parens(self):
    val = py_expr(py_expr.PY_OP_PLUS,py_var('a'),py_var('b'))
    self.assertEqual(val.to_string(True),'(a + b)')
  def test_exp(self):
    val = py_expr(py_expr.PY_OP_POW,py_var('a'),py_var('b'))
    self.assertEqual(val.to_string(),'a**b')
  def test_exp_parens(self):
    subval = py_expr(py_expr.PY_OP_TIMES,py_var('a'),py_var('b'))
    val = py_expr(py_expr.PY_OP_POW,subval,py_var('i'))
    self.assertEqual(val.to_string(),'(a * b)**i')
  def test_fp_divide(self):
    val = py_expr(py_expr.PY_OP_DIVIDE,py_num('1'),py_num('2'))
    self.assertEqual(val.to_string(),'1 / 2')
  def test_equal(self):
    val = py_expr(py_expr.PY_OP_EQUAL,py_num('1'),py_num('2'))
    self.assertEqual(val.to_string(),'1 == 2')
  def test_not_equal(self):
    val = py_expr(py_expr.PY_OP_NOT_EQUAL,py_num('1'),py_num('2'))
    self.assertEqual(val.to_string(),'1 != 2')
  def test_greater_than(self):
    val = py_expr(py_expr.PY_OP_GT,py_num('1'),py_num('2'))
    self.assertEqual(val.to_string(),'1 > 2')
  def test_greater_or_equal(self):
    val = py_expr(py_expr.PY_OP_GE,py_num('1'),py_num('2'))
    self.assertEqual(val.to_string(),'1 >= 2')
  def test_less_than(self):
    val = py_expr(py_expr.PY_OP_LT,py_num('1'),py_num('2'))
    self.assertEqual(val.to_string(),'1 < 2')
  def test_less_or_equal(self):
    val = py_expr(py_expr.PY_OP_LE,py_num('1'),py_num('2'))
    self.assertEqual(val.to_string(),'1 <= 2')
     

class TestFunctionCall(unittest.TestCase): 
  def test_one(self):
    val = py_function_call('func',py_var('a'),py_var('b'))
    self.assertEqual(val.to_string(),'func(a,b)')
  def test_two(self):
    expr = py_expr(py_expr.PY_OP_PLUS,py_var('a'),py_var('b'))
    val = py_function_call('func',expr,py_var('b'))
    self.assertEqual(val.to_string(),'func(a + b,b)')
  def test_none(self):
    val = py_function_call('func')
    self.assertEqual(val.to_string(),'func()')

class TestArgList(unittest.TestCase): 
  def test_one(self):
    val = py_arg_list(py_var('a'),py_var('b'))
    self.assertEqual(val.to_string(),'a,b')
  def test_one(self):
    val = py_arg_list(py_default_arg(py_var('a'),py_var('b')),py_var('c'))
    self.assertEqual(val.to_string(),'a=b,c')

class TestFunctionDef(unittest.TestCase): 
  def test_one(self):
    arglist = py_arg_list(py_var('a'),py_var('b'))
    val = py_function_def('func',arglist)
    self.assertEqual(val.to_string(),'def func(a,b):\n')
  def test_minimal(self):
    val = py_function_def('func')
    ret = py_return_stmt(py_var('1'))
    val.add_statement(ret)
    self.assertEqual(val.to_string(),'def func():\n  return 1\n')

class TestAssignment(unittest.TestCase): 
  def test_one(self):
    stmt = py_assign_stmt(py_var('a'),py_var('b'))
    self.assertEqual(stmt.to_string(),'a = b')
  def test_incr(self):
    stmt = py_assign_stmt(py_var('a'),py_var('b'),py_assign_stmt.PY_ASSIGN_PLUS)
    self.assertEqual(stmt.to_string().strip(),'a += b')
  def test_one(self):
    val = py_expr(py_expr.PY_OP_PLUS,py_var('c'),py_var('d'))
    stmt = py_assign_stmt(py_var('a'),val)
    self.assertEqual(stmt.to_string().strip(),'a = c + d')

class TestPrint(unittest.TestCase): 
  def test_zero_arg(self):
    stmt = py_print_stmt()
    self.assertEqual(stmt.to_string().strip(),'print')
  def test_one_arg(self):
    stmt = py_print_stmt(py_var('a'))
    self.assertEqual(stmt.to_string().strip(),'print a')
  def test_redirect(self):
    stmt = py_print_stmt(py_var('a'))
    stmt.set_redirect(True)
    self.assertEqual(stmt.to_string().strip(),'print >>a')

class TestClass(unittest.TestCase): 
  def test_one(self):
    val = py_class('test_class')
    self.assertEqual(val.to_string(),'class test_class:\n\n')
  def test_with_def(self):
    fdef = py_function_def('func',py_arg_list(),py_pass_stmt())
    val = py_class('test_class',fdef)
    self.assertEqual(val.to_string(),'class test_class:\n  def func():\n    pass\n\n')

class TestAttrRef(unittest.TestCase): 
  def test_one(self):
    val = py_attr_ref(py_var('test'))
    self.assertEqual(val.to_string(),'test')
  def test_two(self):
    val = py_attr_ref(py_var('test'),py_var('two'))
    self.assertEqual(val.to_string(),'test.two')

class TestArray(unittest.TestCase): 
  def test_zero(self):
    val = py_array()
    self.assertEqual(val.to_string(),'[]')
  def test_one(self):
    val = py_array(py_var('a'))
    self.assertEqual(val.to_string(),'[a]')
  def test_two(self):
    val = py_array(py_var('a'),py_var('b'))
    self.assertEqual(val.to_string(),'[a,b]')

class TestTuple(unittest.TestCase): 
  def test_zero(self):
    val = py_tuple()
    self.assertEqual(val.to_string(),'()')
  def test_one(self):
    val = py_tuple(py_var('a'))
    self.assertEqual(val.to_string(),'(a)')
  def test_two(self):
    val = py_tuple(py_var('a'),py_var('b'))
    self.assertEqual(val.to_string(),'(a,b)')

class TestArrayRef(unittest.TestCase): 
  def test_zero(self):
    val = py_array_ref(py_var('a'),py_num('0'))
    self.assertEqual(val.to_string(),'a[0]')
  def test_slice(self):
    val = py_array_ref(py_var('a'),py_slice(py_num('0'),py_num('1')))
    self.assertEqual(val.to_string(),'a[0:1]')
  def test_slice_upper(self):
    val = py_array_ref(py_var('a'),py_slice(None,py_num('1')))
    self.assertEqual(val.to_string(),'a[:1]')
  def test_slice_lower(self):
    val = py_array_ref(py_var('a'),py_slice(py_num('1'),None))
    self.assertEqual(val.to_string(),'a[1:]')
  def test_slice_empty(self):
    val = py_array_ref(py_var('a'),py_slice(None,None))
    self.assertEqual(val.to_string(),'a[:]')
  def test_multi(self):
    val = py_array_ref(py_var('a'),py_num('0'),py_var('i'))
    self.assertEqual(val.to_string(),'a[0][i]')

class TestComment(unittest.TestCase): 
  def test_zero(self):
    comment = py_comment()
    self.assertEqual(comment.to_string(),'#\n')
  def test_one(self):
    comment = py_comment("autogenerated code")
    self.assertEqual(comment.to_string(),'#autogenerated code\n')

class TestImport(unittest.TestCase): 
  def test_zero(self):
    imp = py_import()
    self.assertEqual(imp.to_string(),'import \n')
  def test_one(self):
    imp = py_import('math')
    self.assertEqual(imp.to_string(),'import math\n')
  def test_from(self):
    imp = py_import('math',False,'sqrt')
    self.assertEqual(imp.to_string().strip(),'from math import sqrt')
  def test_from2(self):
    imp = py_import('math',False,'sqrt','cos')
    self.assertEqual(imp.to_string().strip(),'from math import sqrt,cos')

class TestString(unittest.TestCase): 
  def test_short(self):
    val = py_string("string value")
    self.assertEqual(val.to_string(),'"string value"')
  def test_long(self):
    val = py_string("string value",py_string.PY_STRING_LONG)
    self.assertEqual(val.to_string(),'"""string value"""')

class TestFor(unittest.TestCase): 
  def test_simple(self):
    val = py_for(py_var('a'),py_var('b'))
    val.add_statement(py_pass_stmt())
    self.assertEqual(val.to_string(),'for a in b:\n  pass\n')

class TestTry(unittest.TestCase): 
  def test_simple(self):
    val = py_try([py_expr_stmt(py_var('a'))],py_except('Stuff',py_pass_stmt()))
    self.assertEqual(val.to_string(),'try:\n  a\nexcept Stuff:\n  pass\n')

class TestTemplate(unittest.TestCase): 
  def test_simple(self):
    val = py_template('one')
    self.assertEqual(val.to_string(),'%one%')
  def test_find(self):
    val = py_template('one')
    d = find_template_nodes(val,None)
    self.assertEqual(d,{'one':(val,None)})
  def test_find_class(self):
    val1 = py_class(py_template('one'),py_pass_stmt())
    val = py_file('blank.py',val1)
    d = find_template_nodes(val,None)
    self.assertEqual(d,{'one':(val1.name,val1)})

if __name__ == '__main__':
  unittest.main()
