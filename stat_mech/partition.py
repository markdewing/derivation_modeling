

# this should form one page - listing some definitions and setting out the basic form for the
# parition function

from sympy import Symbol, Integral, exp
from sympy.prototype.derivation import derivation, definition, replace_definition

Z = Symbol('Z')
T = Symbol('T')
k = Symbol('k')
V = Symbol('V')
R = Symbol('R')
Beta = Symbol('beta')


partition_function = derivation(Z,Integral(exp(-V/(k*T)),R))
partition_function.set_name('partition')
partition_function.set_title('Partition Function')

beta_def = definition(Beta,1/(k*T),T)

partition_function.add_step( replace_definition(beta_def), 'Insert definition of beta')

