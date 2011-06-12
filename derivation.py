
from sympy import Eq, Function, Symbol, diff, sympify, print_gtk, solve, Integral, simplify, printing
from xml_util import xml_doc
import codecs
import sys

class approx_lhs(object):
    ''' Replace the left hand side with a new value (approximation)'''
    def __init__(self,  new_value):
        self.new_value = new_value

    def __call__(self, eqn):
        eqn = Eq(self.new_value,eqn.args[1])
        return eqn 

class add_term(object):
    '''Add a term an equation'''
    def __init__(self,  term):
        self.term = term

    def __call__(self, eqn):
        eqn = Eq(eqn.args[0] + self.term, eqn.args[1] + self.term)
        return eqn

class mul_factor(object):
    '''Multiply equation by a factor'''
    def __init__(self,  factor):
        self.factor = factor

    def __call__(self, eqn):
        eqn = Eq(eqn.args[0] * self.factor, eqn.args[1] * self.factor)
        return eqn

class identity(object):
    '''Perform operation that leaves rhs modified, but unchanged'''
    def __init__(self, transform):
        self.transform = transform

    def __call__(self, eqn):
        eqn = Eq(eqn.args[0],self.transform(eqn.args[1]))
        return eqn

class doit(object):
    '''Evaluate unevaluated terms on the rhs'''

    def __call__(self, eqn):
        eqn = Eq(eqn.args[0],eqn.args[1].doit())
        return eqn
    


class replace(object):
    '''Replace values'''
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def __call__(self, eqn):
        eqn = eqn.subs(self.v1, self.v2)
        return eqn

class replace_definition(object):
    '''Replace quantity with its definition'''
    def __init__(self, definition):
        self.definition = definition

    def __call__(self, eqn):
        eqn = eqn.subs(self.definition.to_replace,self.definition.replace_with()[0])
        return eqn

def replace_integral(expr, replacement):
    if isinstance(expr, Integral):
        return Integral(expr.function, *replacement)
    elif expr.is_Atom:
        return expr
    else:
        new_args = []
        for v in expr.args:
            print type(v)
            new_v = replace_integral(v, replacement)
            new_args.append(new_v)

        return expr.func(*new_args)


class specialize_integral(object):
    '''Replace integration variable with more specialized versions'''
    def __init__(self, symbol, replacement):
        self.symbol = symbol
        self.replacement = replacement

    def __call__(self, eqn):
        eqn = Eq(eqn.lhs, replace_integral(eqn.rhs, self.replacement))
        return eqn

class do_integral(object):
    '''Should really do this symbolically '''
    def __init__(self, value, remaining_variables):
        self.value = value
        self.variables = remaining_variables

    def __call__(self, eqn):
        eqn = Eq(eqn.lhs, self.value * Integral(eqn.rhs.function, *self.variables))
        return eqn

global_derivation_list = []

def compute_children():
    for g in global_derivation_list:
        for g2 in global_derivation_list:
            if g2.parent == g:
                g.children.append(g2)

def all_to_xhtml():
    for g in global_derivation_list:
        print g.name, g.title
        if g.parent:
            print '  parent: ',g.parent.name
        for c in g.children:
            print '  children:  ',c.name, 
        print '' 
        #g.to_xhtml()
        g.to_mathjax()


class derivation(object):
    def __init__(self, initial_lhs, initial_rhs):
        self.steps = [(None,'')]
        self.eqn = Eq(initial_lhs, initial_rhs)
        self.eqns = [self.eqn]
        self.name = 'tmp'
        self.parent = None
        self.title = None
        self.children = []
        self.definitions = []
        self.output_name = ""
        self.attach_aux = []  # auxiliary equations or functions
        global_derivation_list.append(self)

    def add_step(self, operation, description=''):
        ''' Add a derivation step.  The 'operation' can be a single item, or a list
            of items applied in one step.
        '''
        self.steps.append((operation, description))
        try:
            new_eqn = self.eqns[-1]
            for op in operation:
                new_eqn = op(new_eqn)
            self.eqns.append(new_eqn)
        except TypeError: 
            self.eqns.append(operation(self.eqns[-1]))

    def set_name(self, name):
        self.name = name

    def set_title(self, title):
        self.title = title

    def set_output_name(self, output_name):
        self.output_name = output_name

    def final(self):
        return self.eqns[-1]

    def new_derivation(self):
        d = derivation(self.final().lhs, self.final().rhs)
        d.parent = self
        return d

    def add_definition(self, definition, description=''):
        '''Add a definition, either used in the derivation, or to be replaced later'''
        self.definitions.append((definition, description))

    def add_aux(self, symbol, declaration):
        '''Add equations that are not replaced (function calls)'''
        self.attach_aux.append( (symbol, declaration) )

    def do_print(self):
        for (s,e) in zip(self.steps,self.eqns):
            print e,s[1]
            #print_gtk(e)

    def to_xhtml(self):
        xd = xml_doc()
        xd.add_css(".math {position:relative; left: 40px;}")
        xd.add_css(".definition {position:relative; left: 40px;}")
        if self.title:
            xd.create_child_text_element(xd.body_node,'h1',self.title)
        if len(self.definitions) > 0:
            defi = xd.create_child_element(xd.body_node,'p')
            xd.create_child_text_element(defi,'h2','Definitions')
            for (idx,d) in enumerate(self.definitions):
                c = xd.create_child_element(defi,'p')
                #div = xd.create_child_element(c,'div')
                xd.add_math(c,d[0])
                span = xd.create_child_text_element(c,'span',d[1])
                span.setAttribute('class','definition')
        deriv = xd.create_child_element(xd.body_node,'p')
        xd.create_child_text_element(deriv,'h2','Derivation')
        for (idx,(s,e)) in enumerate(zip(self.steps,self.eqns)):
            c = xd.create_child_element(deriv,'p')
            xd.create_child_text_element(c,'p',s[1])
            d = xd.create_child_element(c,'div')
            if idx > 0:
                d.setAttribute('class','math')
            xd.add_math(d,e)
        if self.parent:
            parent_file = self.parent.name  + '.xhtml'
            #xd.create_child_text_element(xd.body_node,'p','Parent: ' + self.parent.name)
            ln = xd.create_child_text_element(xd.body_node,'p','Parent: ')
            xd.create_link_node(ln,self.parent.name+'.xhtml',self.parent.name)
        for c in self.children:
            ln = xd.create_child_text_element(xd.body_node,'p','Children: ')
            xd.create_link_node(ln,c.name+'.xhtml',c.name)
        #f = open("tmp.xhtml",'w')
        #s = convert_symbols(xd.toprettyxml(),do_html=True)
        s = xd.toprettyxml()
        #f = codecs.open('tmp.xhtml','w','UTF-8',errors='backslashreplace')
        f = codecs.open(self.name+'.xhtml','w','UTF-8',errors='backslashreplace')
        f.write(s)
        f.close()

    def to_mathjax(self):
        xd = xml_doc(add_mathml=False)
        xd.add_css(".math {position:relative; left: 40px;}")
        xd.add_css(".definition {position:relative; left: 40px;}")
        xd.add_script()
        if self.title:
            xd.create_child_text_element(xd.body_node,'h1',self.title)
        if len(self.definitions) > 0:
            defi = xd.create_child_element(xd.body_node,'p')
            xd.create_child_text_element(defi,'h2','Definitions')
            for (idx,d) in enumerate(self.definitions):
                c = xd.create_child_element(defi,'p')
                #div = xd.create_child_element(c,'div')
                xd.add_math(c,d[0])
                span = xd.create_child_text_element(c,'span',d[1])
                span.setAttribute('class','definition')
        deriv = xd.create_child_element(xd.body_node,'p')
        xd.create_child_text_element(deriv,'h2','Derivation')
        for (idx,(s,e)) in enumerate(zip(self.steps,self.eqns)):
            c = xd.create_child_element(deriv,'p')
            xd.create_child_text_element(c,'p',s[1])
            d = xd.create_child_element(c,'div')
            if idx > 0:
                d.setAttribute('class','math')
            xd.add_math(d,e)
        if self.parent:
            parent_file = self.parent.name  + '.html'
            #xd.create_child_text_element(xd.body_node,'p','Parent: ' + self.parent.name)
            ln = xd.create_child_text_element(xd.body_node,'p','Parent: ')
            xd.create_link_node(ln,self.parent.name+'.html',self.parent.name)
        for c in self.children:
            ln = xd.create_child_text_element(xd.body_node,'p','Children: ')
            xd.create_link_node(ln,c.name+'.html',c.name)
        for (sym,decl) in self.attach_aux:
            ln = xd.create_child_text_element(xd.body_node,'p','Aux: ')
            xd.create_link_node(ln,decl.name+'.html',str(sym) + " = " + decl.name)
            
        #f = open("tmp.xhtml",'w')
        #s = convert_symbols(xd.toprettyxml(),do_html=True)
        s = xd.toprettyxml()
        #s = xd.toxml()
        #f = codecs.open('tmp.xhtml','w','UTF-8',errors='backslashreplace')
        f = codecs.open(self.name+'.html','w','UTF-8',errors='backslashreplace')
        f.write(s)
        f.close()
        

class definition(object):
    def __init__(self, symbol, value, to_replace=None):
        self.eqn = Eq(symbol, value)
        self.description = ''
        self.to_replace = to_replace  # ugly - need to be able to replace an expression directly

    def lhs(self):
        return self.eqn.lhs

    def rhs(self):
        return self.eqn.rhs

    def replace_with(self):
        return solve(self.eqn, self.to_replace)
    
       

def derive_euler():
    f = Function('f')
    x = Symbol('x')
    df = diff(f(x),x)
    fd = sympify('(f_1 - f_0)/h')
    g = Symbol('2*x')
    h = Symbol('h')
    f0 = Symbol('f_0')

    d = derivation(df,g)

    d.add_step(approx_lhs(fd),'Approximate derivative with finite difference')
    d.add_step(mul_factor(h))
    d.add_step(add_term(f0))

    d.do_print()


if __name__ == '__main__':
    derive_euler()
