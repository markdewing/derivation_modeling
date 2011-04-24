
from int_gen import convert_integral
from int_lj_n2d2 import lj_n2
#from int_lj_n2d3 import lj_n2
#from int_lj_n3d2 import lj_n2


val = lj_n2.final()
print val
print 'rhs',val.rhs
print 'lhs',val.lhs
t = convert_integral(val.rhs)

f = open('do_int.py','w')
f.write(t.to_string())
f.close()





