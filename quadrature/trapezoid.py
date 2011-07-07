
# represent the trapezoidal rule for integration

from sympy import Symbol, Sum, Function, Eq
from sympy.tensor import Indexed, Idx, IndexedBase
from sympy.utilities.iterables import preorder_traversal
from sympy.prototype.derivation import derivation,identity
from sum_util import peel_n

i = Symbol('i',integer=True)
n = Symbol('n',integer=True)

I = Symbol('I')
f = Function('f')
h = Symbol('h')
x = IndexedBase('x')

a = Symbol('a')
b = Symbol('b')


definition_of_h = Eq(h,(b-a)/n)

trap = derivation(I,Sum(h/2*(f(x[i])+f(x[i+1])),(i,1,n)))
trap.set_name('trapezoidal_int')
trap.set_title('Trapezoidal Rule for Integration')

def split_sum(s):
    v = s.function.expand()
    sums = []
    for t in v.iter_basic_args():
        new_s = Sum(t,s.limits)
        sums.append(new_s)
    return sums[0] + sums[1]

def rewrite(s,rules):
    ''' rewrite an expression.  The rules argument is a list of 2-tuples.
        In each tuple, the first item is a type and the second is a function to apply'''
    if s.is_Atom: 
        return s 
    terms = []
    for t in s.args:
        m = None
        for r in rules:
            if isinstance(t,r[0]):
                m = r
                break
        if m:
            terms.append(r[1](t))
        else:
            terms.append(t)
    return s.func(*terms)

def get_index(term):
    for p in preorder_traversal(term):
        if type(p) == Indexed:
            return p.indices[0]
    return None

def adjust_index(s,adjust):
    new_limits = (s.limits[0][0], s.limits[0][1]+adjust, s.limits[0][2]+adjust)
    new_func = s.function.subs(s.limits[0][0], s.limits[0][0]+adjust)
    return Sum(new_func, new_limits)

def adjust_limit(s):
    v = s.function
    #adjust = get_index(v).args[0].extract_additively('i')
    adjust = get_index(v).extract_additively(i)
    new_s = adjust_index(s,-adjust)
    return new_s

def adjust_limits(s):
    # need to loop over Sums 
    new_s = rewrite(s,[(Sum,adjust_limit)])
    return new_s

class peel_sum_terms(object):
    def __init__(self,min,max):
        self.min = min
        self.max = max
    def __call__(self,s):
        lmin = s.limits[0][1]
        if self.min-lmin > 0:
            (xtra,ns) = peel_n(s, self.min-lmin)
        else:
            xtra = 0
            ns = s

        lmax = s.limits[0][2]
        if lmax-self.max > 0:
            (xtra2,ns2) = peel_n(ns, lmax-self.max, do_lower=False)
        else:
            xtra2 = 0
            ns2 = ns

        new_s = ns2 + xtra + xtra2
        return new_s

        
def peel_terms(s):
    lim_min = None
    lim_max = None
    for p in preorder_traversal(s):
        if isinstance(p,Sum):
            lmin = p.limits[0][1]
            lmax = p.limits[0][2]
            if lim_min:
                lim_min = max(lmin,lim_min)
            else:
                lim_min = lmin
            if lim_max:
                lim_max = min(lmax,lim_max)
            else:
                lim_max = lmax
         
    p = peel_sum_terms(lim_min, lim_max)     
    new_s = rewrite(s,[(Sum,p)])
    return new_s
    

trap.add_step(identity(split_sum),'Split sum')
trap.add_step(identity(adjust_limits),'Adjust limits')
trap.add_step(identity(peel_terms),'Peel terms')

#trap.to_xhtml()
trap.to_mathjax()

if __name__ == '__main__':
    trap.do_print()

