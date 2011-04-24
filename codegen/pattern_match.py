
from sympy import * 

class AutoVarInstance(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

class AutoVar(object):
    '''Access any member variable to return an AutoVarInstance object that can be used
       to bind it to a value later'''
    def __init__(self):
        self.vars = []
    def __getattr__(self,name):
        self.vars.append(name)
        return AutoVarInstance(self,name)


class Match(object):
    def __init__(self, expr, indent=0):
        self.expr = expr
        self.indent = indent
    def type(self, value):
        '''Match on the type of the expression type'''
        return isinstance(type(self.expr),value)
    def __call__(self, *args):
        '''Match on first arg as an expression type, next args bind to expression args'''
        match = True
        if len(args) > 0:
            match = isinstance(self.expr,args[0])
        if match == False:
            return False
        if len(args) == 1:
            return match

        expr_args = self.expr.args
        if len(args) == 3 and len(self.expr.args) > 2:
            expr_args = self.expr.as_two_terms()
        vars_to_bind = []
        for a,e in zip(args[1:], expr_args):
            if isinstance(a,tuple):
                m = Match(e,self.indent+1)
                match &=  m(*a)
            elif isinstance(a, AutoVarInstance):
                vars_to_bind.append( (a, a.name, e) )
            else:
                match &= a == e
            if not match:
                break
        if match:
            for a,name,e in vars_to_bind:
                a.parent.__dict__[name] = e

        return match
            


if __name__ == '__main__':
    pass
 
    



