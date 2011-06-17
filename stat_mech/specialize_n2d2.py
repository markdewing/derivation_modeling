

# this should form another page listing - specializing to N = 2 in 2 dimensions

from sympy import Symbol, Integral, exp, Function, Abs, Eq
from sympy.prototype.vector import Vector, VectorMagnitude
from sympy.prototype.vector_utils import decompose, add_limits, replace_func
from sympy.prototype.derivation import derivation, definition, replace_definition, specialize_integral, replace, do_integral, identity
from partition import partition_function, beta_def, R, V

r1 = Vector('r1',dim=2)
r2 = Vector('r2',dim=2)

V2 = Function('V')
n2 = partition_function.new_derivation()
n2.set_name('specialize_n2d2')
n2.set_title('Specialized to N=2, D=2')
#n2.do_print()
n2.add_step(specialize_integral(R,(r1,r2)),'specialize to N=2')
n2.add_step(replace(V,V2(r1,r2)),'replace potential with N=2')
#n2.do_print()

r_cm = Vector('r_cm',dim=2)
r_12 = Vector('r_12',dim=2)

r_12_def = definition(r_12, r2-r1)
r_cm_def = definition(r_cm, (r1+r2)/2)

V12 = Function('V')

# replace r1,r2 with r_12 and r_cm
#   tranformation of limit region is hard, but the square box should be equivalent in periodic
#   boundary conditions
#  Jacobian is 1

n2.add_step(specialize_integral(r1,(r_12,r_cm)),'Switch variables')
n2.add_step(replace(V2(r1,r2),V12(r_12)),'Specialize to a potential that depends only on interparticle distance')
n2.add_step(replace(V12(r_12),V12(Abs(r_12))),'Depend only on the magnitude of the distance')
#n2.add_step(replace_func(V12(r_12),Eq(V12,V12(Abs(r_12)))),'Depend only on the magnitude of the distance')
n2.do_print()

Vol = Symbol('Omega')
n2.add_step(do_integral(Vol, [r_12]),'Integrate out r_cm (this step is still a hack)')

L = Symbol('L')
n2.add_step(identity(decompose),'Decompose into vector components')
# Lower limit is small, rather than 0 to avoid a division by zero error at the origin.
n2.add_step(identity(add_limits(-L/2,L/2)),'Add integration limits')

