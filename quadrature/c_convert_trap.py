
from sympy.prototype.quadrature.trapezoid import trap,definition_of_h
from sympy.prototype.codegen import sympy_to_c
from sympy.prototype.codegen import lang_c
import sympy


e = trap.final()

idx = sympy.Symbol('a') + sympy.Symbol('i')*sympy.Symbol('h')
index_trans = {"x":(sympy.Symbol('i'),idx)}


print e.rhs
f_h = open('ctrap_gen.h','w')
f_cpp = open('ctrap_gen.cpp','w')

inc_f = lang_c.pp_include('ctrap_gen.h',lang_c.pp_include.INCLUDE_TYPE_LOCAL)
f_cpp.write(inc_f.to_string())

for narg in range(6):
    extra_args = ['e'+str(i) for i in range(narg)]
    (ep,inc) = sympy_to_c.convert(e.rhs, definitions=[definition_of_h], func_name='trap'+str(narg),
                    extra_args=extra_args, index_trans=index_trans, func_type_name='FUNC'+str(narg))
    f_cpp.write(ep.to_string())
    f_cpp.write('\n')
    f_h.write(inc.to_string())
    f_h.write('\n')
f_cpp.close()
f_h.close()


