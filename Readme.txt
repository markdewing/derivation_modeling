


derivation.py - model a derivation and all various operational steps

vector.py - just enough to model a vector
vector_utils.py -  utilities to decompose an expression involving vectors in vector components, and some
         others that have nothing to do with vectors.

xml_util.py - utilities for building an MathML document

quadrature/
  sum_util.py - utilities for manipulating sums
  trapezoid.py - start from the linear approximation for a single interval and
     extend the result to a series of intervals.
   convert_trap.py - convert the expression in trapezoid.py to Python code (creates ptrap_gen.py)
   c_convert_trap.py -  as above, but convert to C code (creates ctrap_gen.h, ctrap_gen.cpp)

stat_mech/
  final.py - create the top level Python code to call the integration routines (creates do_int.py)
  c_final.py - create the top level C code to call the integration routines (creates main_int.cpp)
  int_gen.py - convert a multidimensional symbol integral to Python code to iteratively call an integration routine
  c_int_gen.py - convert a multidimensional symbol integral to C code to iteratively call an integration routine

  These four are the the model derivation.
    partition.py - define the partition function
    specialize_n2d2.py - specialize the partition function to the case of 2 particles in 2 spatial dimensions
    lj.py - define the Lennard-Jones potential
    int_lj_n2d2.py - specialize the partition function to the Lennard-Jones potential.
       Also specify the temperature and box size to make the integral completely numerical.
  

codegen/
  lang_py.py - Python language model
  pattern_match.py - experiment in pattern-matching syntax for converting sympy trees to other forms
  sympy_to_py.py - convert sympy expressions to Python
  sympy_to_c.py - convert sympy expressions to C
  transforms.py - some common tree transformtions - mostly extracting information, like sums or free variables
  
