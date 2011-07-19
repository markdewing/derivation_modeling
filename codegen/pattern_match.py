
class AutoVarInstance(object):
    """Placeholder for binding an AutoVar member."""
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def bind_value(self, name, e):
        self.parent.bind_value(name, e)


class AutoVar(object):
    """
    Tracks member variables for later binding and use.

    Access any member variable and it will return an AutoVarInstance object
    that can bind it to a value later.
    """

    def __getattr__(self,name):
        return AutoVarInstance(self,name)

    def bind_value(self, name, e):
        self.__dict__[name] = e


class Match(object):
    """
    Match patterns in an expression tree.
    """

    def __init__(self, expr):
        self.expr = expr

    def type(self, value):
        """Match on the type of the expression type.
           Used for matching all functions."""
        return isinstance(type(self.expr),value)

    def exact(self, value):
        """Match exact values, for singletons."""
        return value == self.expr

    def __call__(self, *args):
        """Match on first argument as an expression type.
           Next arguments bind to expression arguments."""
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
                m = Match(e)
                match &= m(*a)
            elif isinstance(a, AutoVarInstance):
                vars_to_bind.append( (a, a.name, e) )
            else:
                match &= a == e
            if not match:
                break
        if match:
            for a,name,e in vars_to_bind:
                a.bind_value(name,e)

        return match

