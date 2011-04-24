
# peel some iterations off a sum

from sympy import *
from sympy.tensor import Indexed, Idx, IndexedBase



def peel_one(s):
    v,lower,upper = s.limits[0]
    f = s.function
    t1 = f.subs(v,lower)
    r = Sum(f,(v,lower+1,upper))
    return t1 + r

def peel_n(s, n=1, do_lower=True ):
    v,lower,upper = s.limits[0]
    f = s.function
    t = 0
    for i in range(n):
        if do_lower:
            t1 = f.subs(v,lower+i)
        else:
            t1 = f.subs(v,upper-i)
        t += t1
    if do_lower:
        r = Sum(f,(v,lower+n,upper))
    else:
        r = Sum(f,(v,lower,upper-n))
    return [t,r]

if __name__ == '__main__':
    i,n = symbols('i n', integer=True)

    h = symbols('h')

    x = IndexedBase('x')
    f = Function('f')
    print 'f = ',f

    s = Sum(h/2*f(x[i]),(i,1,n))
    print 's = ',s
    print 's limits = ',s.limits
    r1 = peel_one(s)
    print 'r1 = ',r1

    r2 = peel_n(s,2,do_lower=False)
    print 'r2 = ',r2

    v = s.subs(n,2)
    print 'v = ',v.doit()
