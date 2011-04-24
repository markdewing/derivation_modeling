
from sympy import Symbol, Function
from sympy.prototype.derivation import derivation

r = Symbol('r')
V = Symbol('V')

# set epsilon and sigma to 1 for now

lj_expr = 4*(1/r**12 - 1/r**6)

lj_pot = derivation(V(r),lj_expr)
lj_pot.set_name('lennard-jones')
lj_pot.set_title('Lennard-Jones Potential')


if __name__ == '__main__':
    lj_pot.to_xhtml()


