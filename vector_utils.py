
from sympy.prototype.vector import Vector, VectorMagnitude
from sympy import Symbol, Expr, Basic, Tuple, Add, Mul, S, Function, Abs, FunctionClass
from sympy.tensor import Indexed, IndexedBase, Idx
from sympy.integrals import Integral
from sympy.functions import sqrt
from codegen.pattern_match import AutoVar,AutoVarInstance,Match


def is_vector(e):
    m = Match(e)
    v = AutoVar()
    if m(Add,v.e1,v.e2):
        return is_vector(v.e1) and is_vector(v.e2)

    if m(Mul,v.e1,v.e2):
        return is_vector(v.e1) or is_vector(v.e2)

    if m(Vector):
        return True

    return False

# This doesn't belong in here
class replace_func(object):
    def __init__(self, old, new):
        self.old = old
        self.new = new
    def __call__(self,e):
        v = AutoVar()
        m = Match(e)

        #if m(self.old):
        if m.type(FunctionClass):
            if type(e) == self.old:
                arg = self.new.lhs.args[0] 
                return self.new.rhs.subs(arg, e.args[0])

        if (len(e.args)) == 0:
            return e

        arg = e.args
        new_args = []
        for a in arg:
            other = self(a)
            new_args.append(other)
        r = e.new(*new_args)
        return r

# This doesn't belong in here
class add_limits(object):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
    def __call__(self,e):
        v = AutoVar()
        m = Match(e)

        if m(Integral):
            newlim = []
            for lim in e.limits:
                newlim.append((lim[0],self.lower,self.upper))
            new_e = Integral(e.function, *newlim)
            return new_e

        if (len(e.args)) == 0:
            return e

        arg = e.args
        new_args = []
        for a in arg:
            other = self(a)
            new_args.append(other)


        r = e.new(*new_args)
        return r

    
        
def decompose(e):
    '''Decompose an expression involving vectors into an expression of the vector components'''
    v = AutoVar()
    m = Match(e)

    if m(Add, (Mul, S.NegativeOne, v.e1), v.e2):
        if is_vector(v.e2) and is_vector(v.e2):
            return [v1 - v2 for v1,v2 in zip(decompose(v.e1),decompose(v.e2))]

    if m(Add, v.e1, v.e2):
        if is_vector(v.e2) and is_vector(v.e2):
            return [v1 + v2 for v1,v2 in zip(decompose(v.e1),decompose(v.e2))]

    if m(Mul, v.e1, v.e2):
        if is_vector(v.e2):
            return [v.e1*x for x in decompose(v.e2)]

    if m(Abs, v.e1):
        return sqrt(sum([x*x for x in decompose(v.e1)])) 

    if m(Vector):
        return e.components()

    if m(Integral):
        newlim = []
        for lim in e.limits:
            newlim.extend(decompose(lim[0]))
        return Integral(decompose(e.function), *newlim)

    if (len(e.args)) == 0:
        return e

    arg = e.args
    new_args = []
    for a in arg:
        other = decompose(a)
        new_args.append(other)


    r = e.new(*new_args)
    return r
        

 


if __name__ == '__main__':
    v1 = Vector('v1',dim=2)
    v2 = Vector('v2',dim=2)
    i = Symbol('i',integer=True)
    print v1,type(v1)
    e = 2*Integral(Abs(v1),(v1,0.2))
    V = Function('V')
    V2 = V(v1)
    x = Symbol('x')
    V_def = x*x
    #e = v1-v2
    #print e,type(e),type(type(e))
    print replace_func(V(v1),V(Abs(v1)))(V2)
    #print decompose(e)
    #print Abs(v1-v2).decompose()
    #print replace_func(V2,V_def)

