
from sympy.prototype.stat_mech.c_int_gen import convert_integral
from sympy.prototype.codegen.lang_c import *
from sympy.prototype.stat_mech.int_lj_n2d2 import lj_n2
#from gen_int_lj_n2d2 import lj_n2

#from en_lj_n2d2 import en_lj_n2
#from en_lj_n3d2 import en_lj_n3

#from int_lj_n2d3 import lj_n2
#from int_lj_n3d2 import lj_n2


val = lj_n2.final()
#val = en_lj_n2.final()
#val = en_lj_n3.final()
print val
print 'rhs',val.rhs
print 'lhs',val.lhs

t = convert_integral(val.rhs, transforms=lj_n2.attach_aux)
#t = convert_integral(val.rhs, transforms=en_lj_n2.attach_aux)
#t = convert_integral(val.rhs, transforms=en_lj_n3.attach_aux)
f = open('main_int.cpp','w')
f.write(t.to_string())
f.close()





