
from lj import lj_pot
from specialize_n2d2 import n2,V12,r_12
from sympy.prototype.derivation import replace, compute_children, all_to_xhtml
from sympy.prototype.vector_utils import replace_func

from sympy import Symbol, sqrt, Integral

lj_n2 = n2.new_derivation()
lj_n2.set_name('lj_n2')
lj_n2.set_title('Using LJ potential with N=2')
lj_eqn = lj_pot.final()
lj_n2.add_step(replace_func(V12,lj_eqn),'Specialize to the LJ potential')


lj_n2.add_step(replace('L',1.0),'Insert value for box size')
lj_n2.add_step(replace('Omega',1.0),'Insert value for box volume')
lj_n2.add_step(replace('beta',1.0),'Insert value for temperature')



# Could evaluate now in sympy
#i1 = lj_n2.final().rhs
#print 'Z = ',i1.evalf()

# Could replace the last three steps with the following code
# to evaluate parameter scan in sympy

#for i in range(10):
#    for j in range(10):
#        box_len = 0.6 + j*.02
#        beta = 0.5 + i*.1
#        i1 = lj_n2.final().rhs
#        i1 = i1.subs('L',box_len)
#        i1 = i1.subs('Omega',box_len*box_len)
#        i1 = i1.subs('beta',beta)
#        val = i1.evalf()
#        print box_len,beta,val

if __name__ == '__main__':
    compute_children()
    all_to_xhtml()

