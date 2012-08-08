
from sympy import Symbol, Basic, Tuple


class Vector(Symbol):
    def __init__(self, label, dim=None, **kw_args):
        Symbol.__init__(label, **kw_args)
        self.dim = dim

    def __abs__(self):
        return VectorMagnitude(self)

    def components(self):
        sym = str(self)
        components = [Symbol(sym+'_x'), Symbol(sym+'_y'), Symbol(sym+'_z')]
        return  components[:self.dim]


class VectorMagnitude(Basic):
    def __init__(self, arg): 
        self._args = Tuple(arg)

    def decompose(self):
        comps = self.args[0].components()
        return sqrt(sum([x*x for x in comps]))

 


if __name__ == '__main__':
    from sympy import Function, exp
    from sympy.functions import Abs
    from sympy.integrals import Integral
    v1 = Vector('v1',dim=2)
    v2 = Vector('v2',dim=2)
    i = Symbol('i',integer=True)
    a = Symbol('a')
    print v1,type(v1)
    #e = 2*Integral(Abs(v1-v2),(v1,0.2))
    V = Function('V')
    #V2 = V(i)
    e = Integral(exp(-a*V(v1)),v1)
    
    print e,e.subs(V(v1),V(Abs(v1)))

