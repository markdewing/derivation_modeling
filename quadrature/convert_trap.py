
from trapezoid import trap,definition_of_h
from sympy.prototype.codegen import sympy_to_py
from sympy.prototype.codegen import lang_py
from sympy.prototype.codegen.lang_py import py_expr,py_var
import sympy


e = trap.final()

idx = sympy.Symbol('a') + sympy.Symbol('i')*sympy.Symbol('h')
index_trans = {}
index_trans['x'] = (sympy.Symbol('i'), idx)

t = lang_py.py_file()
f = open('ptrap_gen.py','w')
for narg in range(4):
    #sympy_to_py.extra_args = ['e'+str(i) for i in range(narg)]
    extra_args = ['e'+str(i) for i in range(narg)]
    ep = sympy_to_py.convert(e.rhs,definitions=[definition_of_h],func_name='trap'+str(narg),
            index_trans=index_trans, extra_args=extra_args)
    f.write(ep.to_string())
    f.write('\n')
f.close()


