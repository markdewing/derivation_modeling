
from int_gen import convert_integral, convert_main
from sympy.prototype.codegen.sympy_to_py import expr_to_py
from int_lj_n2d2 import lj_n2
#from int_lj_n2d3 import lj_n2
#from int_lj_n3d2 import lj_n2


val = lj_n2.final()
print val
print 'rhs',val.rhs
print 'lhs',val.lhs
#t = convert_integral(val.rhs)
t = convert_main(val.rhs)
#t = expr_to_py()(val.rhs)

f = open('do_int.py','w')
f.write(t.to_string())
f.close()





