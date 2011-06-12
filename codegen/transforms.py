
from sympy import * 
from pattern_match import AutoVar,AutoVarInstance,Match

# Common tree matching and transform functions


def find_func(func, e):
    m = Match(e)
    if m(func):
        return [e]
    
    fs = []
    for n in e.args:
        fs.extend(find_func(func, n))
    return fs

# returns tuple of (sum term, other terms)
def extract_sum(e):
    m = Match(e)

    if m(Sum):
        return (e, Symbol('total'))
        #return (e, None)

    # not sure how to express this any better?
    if (len(e.args)) == 0:
        return (None,e)

    # default 
    arg = e.args
    sum = None
    new_args = []
    for a in arg:
        (sums, other) = extract_sum(a)
        if sums:
            sum = sums
        #if other:
        new_args.append(other) 
        #if not other:
        #    other = Symbol('total') 


    return (sum, e.new(*new_args))

# returns a list of expressions
class extract_integrals:
    def __init__(self):
        self.idx = 0
        
    def __call__(self, e):
        m = Match(e)
    
        if m(Integral):
            name = 'val' + str(self.idx)
            ret = ([(name,e)], Symbol(name))
            self.idx += 1
            return ret

        # not sure how to express this any better?

        if (len(e.args)) == 0:
            return ([],e)

        # default 
        arg = e.args
        ints = []
        new_args = []
        for a in arg:
            (new_ints, other) = self(a)
            ints.extend(new_ints)
            new_args.append(other) 
            #if not other:
            #    other = Symbol('total') 

        return (ints, e.new(*new_args))

    


# returns set of free variables (and functions)
def extract_free_variables(e):
    m = Match(e)

    if m(Sum):
        limit_var = e.limits[0][0] 
        vars = extract_free_variables(e.function)
        lower = extract_free_variables(e.limits[0][1])
        upper = extract_free_variables(e.limits[0][2])
        vars.update(lower)
        vars.update(upper)
        if limit_var in vars:
            vars.remove(limit_var)
        return vars

    if m(Symbol):
        return set([e])

    if m.type(FunctionClass): 
        return set([type(e)])

    # not sure how to express this any better?
    if (len(e.args)) == 0:
        return set([])

    # default 
    arg = e.args
    free_vars = set()
    for a in arg:
        other = extract_free_variables(a)
        free_vars.update(other) 

    return free_vars
    

if __name__ == '__main__':
    x = Symbol('x')
    num = Integral(x*x,x)
    denom = Integral(x+1,x)
    e = num/denom
    val = extract_integrals()(e)
    print val
