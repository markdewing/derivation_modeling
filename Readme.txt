
Running the examples
--------------------

To get html output, run
  quadrature/trapezoid.py - produces trapezoidal_int.html
  stat_mech/int_lj_n2d2.py - produces partition.html, specialize_n2d2.html, lj_n2.html, and lennard-jones.html
 If you open partition.html, the next two pages (specialize_n2d2.html and lj_n2.html) are linked from it.

To get python code, run
  quadrature/convert_trap.py - produces ptrap_gen.py
  stat_mech/final.py - produces do_int.py (which imports ptrap_gen.py)

To get C code, run
  quadrature/c_convert_trap.py - produces ctrap_gen.h and ctrap_gen.cpp
  stat_mech/c_final.py - produces main_int.cpp
    Compile main_int.cpp and ctrap_gen.cpp to get an executable


Contents
--------

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
  

example_codegen.py - The classical 'Hello World' program in the C and python trees.  Run it to generated hello_py.py and hello_c.c.

codegen/
  lang_py.py - Python language model
  pattern_match.py - experiment in pattern-matching syntax for converting sympy trees to other forms
  sympy_to_py.py - convert sympy expressions to Python
  sympy_to_c.py - convert sympy expressions to C
  transforms.py - some common tree transformtions - mostly extracting information, like sums or free variables
  
