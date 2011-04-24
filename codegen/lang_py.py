#!/usr/bin/python


# Tree representation of Python, designed for output and code generation

# how much should each level be indented
py_indent_spaces = 4 

py_indent_level = 0

def change_indent_level(change):
  global py_indent_level
  py_indent_level += change

def indent_string():
  global py_indent_level
  nspaces = py_indent_spaces * py_indent_level
  return ' '*nspaces

# for debugging

def print_subtree(p,indent=0):
  if p == None or isinstance(p,str):
    return
  for s in p.args:
    #print ' '*indent,[s],s
    print ' '*indent,type(s)
    print ' '*indent,[s]
    #print ' '*indent,s.__class__
    print_subtree(s,indent+1)

def print_tree(p):
  #print [p],p
  #print p,type(p)
  print type(p)
  print_subtree(p)


# utility functions

def create_parent_links(p,parent=None):
  if p and not isinstance(p,str):
    p.parent = parent
    if p.args:
      for s in p.args:     
        create_parent_links(s,p)

def find_nodes(nodeType,p,recursive=False):
  nodes = []
  if not p or isinstance(p,str):
    return nodes
  for s in p.args:
    if isinstance(s,nodeType):
      nodes.append(s)
    if recursive:
      nodes.extend(find_nodes(nodeType,s,recursive))
  return nodes

def find_template_nodes(node,parent=None):
  node_dict = {}
  if isinstance(node,py_class) and isinstance(node.name,py_template):
    node_dict[node.name.name] = (node.name,node)
  elif isinstance(node,py_template):
    node_dict[node.name] = (node,parent)
  for s in node.args:
    d = find_template_nodes(s,node)
    node_dict.update(d)
  return node_dict

def replace_node(root,node,new_node,recursive=False):
  if root == None:
    return
  for i,arg in enumerate(root.args):
    if arg == node:
      root.args[i] = new_node
      return
    elif recursive:
      replace_node(arg,node,new_node,recursive)

def replace_template_node(node,template_name,new_val):
  if node == None:
    return False
  if isinstance(node,py_class) and isinstance(node.name,py_template):
    node.name = new_val
    return True
  if isinstance(node,py_function_def) and  isinstance(node.name,py_template):
    node.name = new_val
    return True
  for i,arg in enumerate(node.args):
    if isinstance(arg,py_template) and arg.name == template_name:
      node.args[i] = new_val
      return True
    if isinstance(arg,py_expr_stmt) and arg.args[0].name == template_name:
      node.args[i] = new_val
      return True
    else:
      ret = replace_template_node(arg,template_name,new_val)
      if ret:
        return True
  

def delete_node(node,p):
  for i in range(len(p.args)):
    if node == p.args[i]:
      del p.args[i]
      #break
  


def comma_list_str(args):
  arglen = len(args)
  out = ''
  for (i,arg) in enumerate(args):
    out += arg
    if i < arglen-1:
      out += ","
  return out

def comma_list(args):
  arglen = len(args)
  out = ''
  for (i,arg) in enumerate(args):
    out += arg.to_string()
    if i < arglen-1:
      out += ","
  return out
    

class py_base(object):
  def __init__(self):
    self.args = []
    self.parent = None
  def to_string(self,need_paren=False):
    return ''
  def contains(self,test_val):
    if test_val(self):
      return True
    for a in self.args:
      if a and a.contains(test_val):
        return True
    return False
  def __str__(self):
    return self.to_string()


class py_var(py_base):
  def __init__(self,name):
    py_base.__init__(self)
    self.name = name
  def to_string(self,need_paren=0):
    return self.name
  def __str__(self):
    return self.name

class py_num(py_base):
  def __init__(self,value,promote_to_fp=False):
    py_base.__init__(self)
    self.promote_to_fp = promote_to_fp
    if isinstance(value,str):
      self.value = value 
    else:
      self.value = str(value)
  def to_string(self,need_paren=False):
    if self.promote_to_fp:
      return str(float(self.value))
    return self.value
  def __str__(self):
    return self.value

class py_string(py_base):
  PY_STRING_SHORT = 0
  PY_STRING_LONG = 1
  def __init__(self,value,type=PY_STRING_SHORT):
    py_base.__init__(self)
    self.value = value
    self.type = type
  def to_string(self,need_paren=False):
    delim = '"'
    if self.type == self.PY_STRING_LONG:
      delim = '"""'
    out = delim + self.value + delim
    return out
  

def is_add(py):
  if isinstance(py,py_expr):
    if py.op == py_expr.PY_OP_PLUS:
      return True
    if py.op == py_expr.PY_OP_MINUS and py.args[1] != None:
      return True
  return False

def is_expr(py):
  return isinstance(py,py_expr)

class py_expr(py_base): 
  PY_OP_PLUS = 1
  PY_OP_MINUS = 2
  PY_OP_TIMES = 3
  PY_OP_DIVIDE = 4
  PY_OP_POW = 5
  PY_OP_EQUAL = 6
  PY_OP_NOT_EQUAL = 7
  PY_OP_GT = 8
  PY_OP_GE = 9
  PY_OP_LT = 10
  PY_OP_LE = 11
  PY_OP_XOR = 12
  PY_OP_AND = 13
  PY_OP_OR = 14
  def __init__(self,op,arg1=None,arg2=None):
    py_base.__init__(self) 
    self.op = op
    self.args.append(arg1)
    self.args.append(arg2)
  def to_string(self,need_paren=False):
    out = ""
  def __init__(self,op,arg1=None,arg2=None):
    py_base.__init__(self) 
    self.op = op
    self.args.append(arg1)
    self.args.append(arg2)
  def to_string(self,need_paren=False):
    out = ""
    arg1_str = "<no arg1>"
    might_need_paren = False
    if (self.op == py_expr.PY_OP_TIMES or
        self.op == py_expr.PY_OP_DIVIDE):
      if self.args[0] and self.args[0].contains(is_add):
        might_need_paren = True
      if self.args[1] and self.args[1].contains(is_add):
        might_need_paren = True

    if (self.op == py_expr.PY_OP_POW or
       self.op == py_expr.PY_OP_DIVIDE):
      if self.args[0].contains(is_expr):
        might_need_paren = True
      if self.args[1].contains(is_expr):
        might_need_paren = True

    if self.args[0]:
      arg1_str = self.args[0].to_string(might_need_paren)
    arg2_str = ""
    if self.args[1]: 
      if isinstance(self.args[1],py_num):
        arg2_str = self.args[1].to_string(might_need_paren)
      else:
        arg2_str = self.args[1].to_string(might_need_paren)

    if need_paren:
      out += '('
    if self.op == py_expr.PY_OP_PLUS:
      out += arg1_str + ' + ' + arg2_str
    elif self.op == py_expr.PY_OP_MINUS:
      if self.args[1] == None:
        out += '-' + arg1_str
      else:
        out += arg1_str + ' - ' + arg2_str
    elif self.op == py_expr.PY_OP_TIMES:
      out += arg1_str + ' * ' + arg2_str
    elif self.op == py_expr.PY_OP_DIVIDE:
      out += arg1_str + ' / ' + arg2_str
    elif self.op == py_expr.PY_OP_POW:
      out += arg1_str + '**' + arg2_str
    elif self.op == py_expr.PY_OP_EQUAL:
      out += arg1_str + ' == ' + arg2_str
    elif self.op == py_expr.PY_OP_NOT_EQUAL:
      out += arg1_str + ' != ' + arg2_str
    elif self.op == py_expr.PY_OP_GT:
      out += arg1_str + ' > ' + arg2_str
    elif self.op == py_expr.PY_OP_GE:
      out += arg1_str + ' >= ' + arg2_str
    elif self.op == py_expr.PY_OP_LT:
      out += arg1_str + ' < ' + arg2_str
    elif self.op == py_expr.PY_OP_LE:
      out += arg1_str + ' <= ' + arg2_str
    elif self.op == py_expr.PY_OP_XOR:
      out += arg1_str + ' ^ ' + arg2_str
    elif self.op == py_expr.PY_OP_AND:
      out += arg1_str + ' & ' + arg2_str
    elif self.op == py_expr.PY_OP_OR:
      out += arg1_str + ' | ' + arg2_str

    if need_paren:
      out += ')'

    return out 

class py_expr_stmt(py_base): 
  def __init__(self,arg):
    py_base.__init__(self) 
    self.args.append(arg)
  def to_string(self,need_paren=False):
    out = indent_string() + self.args[0].to_string() + '\n'
    return out

class py_array(py_base): 
  def __init__(self,*args):
    py_base.__init__(self)
    self.args.extend(args)
  def add_value(self,*value):
    self.args.extend(value)
  def to_string(self,need_paren=False):
    out = "["
    arglen = len(self.args)
    for (i,arg) in enumerate(self.args):
      out += arg.to_string()
      if i < arglen-1:
        out += ","
    out += "]"
    return out

class py_tuple(py_base): 
  def __init__(self,*args):
    py_base.__init__(self)
    self.args.extend(args)
  def add_value(self,*value):
    self.args.extend(value)
  def to_string(self,need_paren=False):
    out = "("
    arglen = len(self.args)
    for (i,arg) in enumerate(self.args):
      out += arg.to_string()
      if i < arglen-1:
        out += ","
    out += ")"
    return out

class py_array_ref(py_base): 
  def __init__(self,name,*index):
    py_base.__init__(self)
    self.args.append(name)
    self.args.extend(index)
  def to_string(self,need_paren=False):
    out = self.args[0].to_string() 
    for arg in self.args[1:]:
      out += "[" + arg.to_string() + "]"
    return out

class py_slice(py_base):
  def __init__(self,lower=None,upper=None):
    py_base.__init__(self)
    self.args.append(lower)
    self.args.append(upper)
  def to_string(self,need_paren=False):
    out = ''
    if self.args[0]:
      out += self.args[0].to_string()
    out += ':'
    if self.args[1]:
      out += self.args[1].to_string()
    return out
   


class py_function_call(py_base):
  def __init__(self,name,*args):
    py_base.__init__(self)
    self.name = name
    self.args.extend(args)
  def to_string(self,need_paren=False):
    out = self.name + '('
    arglen = len(self.args)
    for (i,arg) in enumerate(self.args):
      try:
        out += arg.to_string()
      except:
        if arg:
            out += arg
      if i <  arglen-1:
        out += ","
    out += ')'
    return out

class py_arg_list(py_base):
  def __init__(self,*args):
    py_base.__init__(self)
    self.args.extend(args)
  def to_string(self,need_paren=False):
    arglen = len(self.args) 
    out = ""
    for (i,arg) in enumerate(self.args):
      out += arg.to_string()
      if i < arglen-1:
        out += ','
    return out

class py_default_arg(py_base):
  def __init__(self,arg,default_value):
    py_base.__init__(self)
    self.args.append(arg)
    self.args.append(default_value)
  def to_string(self,need_paren=False):
    out = self.args[0].to_string() + '=' + self.args[1].to_string()
    return out

class py_stmt_block(py_base):
  def __init__(self,*args):
    py_base.__init__(self)
    self.args.extend(args)
  def add_statements(self,*args):
    self.args.extend(args)
  def to_string(self,need_paren=False):
    out = ""
    for arg in self.args:
      out += arg.to_string()
      #out += "\n"
    return out
    

class py_function_def(py_base):
  def __init__(self,name,*args):
    py_base.__init__(self)
    self.name = name
    if len(args) == 0:
      self.args = [None]
    self.args.extend(args)
  def add_statement(self,*stmt):
    self.args.extend(stmt)
  def to_string(self,need_paren=False):
    if isinstance(self.name,str):
      out = indent_string() + 'def ' + self.name + '('
    else:
      out = indent_string() + 'def ' + self.name.to_string() + '('
    if self.args[0]:
      out += self.args[0].to_string()
    out += '):\n'
    change_indent_level(1)
    for arg in self.args[1:]:
      out += arg.to_string()
    change_indent_level(-1)
    return out

class py_class(py_base): 
  def __init__(self,name,*args):
    py_base.__init__(self)
    self.name = name
    self.args.extend(args)
  def add_method(self,*method):
    self.args.extend(method)
  def to_string(self,need_paren=False):
    if isinstance(self.name,str):
      out = "class " + self.name + ":\n"
    else:
      out = "class " + self.name.to_string() + ":\n"
    change_indent_level(1)
    for arg in self.args:
      out += arg.to_string()
    change_indent_level(-1)
    out += "\n"
    return out

class py_attr_ref(py_base): 
  def __init__(self,name,attr=None):
    py_base.__init__(self)
    self.args.append(name)
    if attr:
      self.args.append(attr)
  def to_string(self,need_paren=False):
    out = self.args[0].to_string()
    if len(self.args) > 1 and self.args[1]:
      out += "." + self.args[1].to_string()
    return out

class py_return_stmt(py_base):
  def __init__(self,*args):
    py_base.__init__(self)
    self.args.extend(args)
  def to_string(self,need_paren=False):
    out = indent_string()
    out += "return"
    if len(self.args) and self.args[0]:
      out += ' ' + self.args[0].to_string()
    out += "\n"
    return out

class py_print_stmt(py_base):
  def __init__(self,*args):
    py_base.__init__(self)
    self.redirect=False
    self.args.extend(args)
  def set_redirect(self,redirect):
    self.redirect = redirect
  def to_string(self,need_paren=False):
    out = indent_string()
    out += "print "
    if self.redirect:
      out += ">>"
    out += comma_list(self.args)
    #arglen = len(self.args)
    #for (i,arg) in enumerate(self.args):
    #  out += arg.to_string()
    #  if i < arglen-1:
    #    out += ','
    out += "\n"
    return out

class py_pass_stmt(py_base):
  def __init__(self,*args):
    py_base.__init__(self)
    self.args.extend(args)
  def to_string(self,need_paren=False):
    out = indent_string()
    out += "pass\n"
    return out

class py_assign_stmt(py_base):
  PY_ASSIGN_EQUAL = 1
  PY_ASSIGN_PLUS = 2
  PY_ASSIGN_MINUS = 2
  def __init__(self,lhs=None,rhs=None,op=PY_ASSIGN_EQUAL):
    py_base.__init__(self)
    self.args.append(lhs)
    self.args.append(rhs)
    self.op = op
  def to_string(self,need_paren=False):
    out = indent_string()
    lhs = self.args[0]
    rhs = self.args[1]
    if lhs:
      out += lhs.to_string()
      if self.op == py_assign_stmt.PY_ASSIGN_EQUAL: 
        out += " = "
      elif self.op == py_assign_stmt.PY_ASSIGN_PLUS: 
        out += " += "
      elif self.op == py_assign_stmt.PY_ASSIGN_MINUS: 
        out += " -= "
    if rhs:
       out += rhs.to_string()
    out += '\n'
    return out


class py_import(py_base):
  def __init__(self,name='',whole_module=True,*args):
    py_base.__init__(self)
    self.name = name
    self.whole_module = whole_module
    self.args.extend(args)
  def to_string(self):
    if self.whole_module:
      out = "import " + self.name
    else:
      out =  "from " + self.name + " import "
      out += comma_list_str(self.args)
    out += '\n'
    return out


class py_comment(py_base):
  def __init__(self,text='',*args):
    py_base.__init__(self)
    self.text = text
    self.args.extend(args)
  def to_string(self):
    out = '#' + self.text + '\n'
    return out

class py_blank_line(py_base):
  def __init__(self,nblank=1,*args):
    py_base.__init__(self)
    self.nblank = nblank
    self.args.extend(args)
    
  def to_string(self):
    out = '\n'*self.nblank
    return out

class py_file(py_base):
  def __init__(self,name='',*args):
    py_base.__init__(self)
    self.name = name
    self.args.extend(args)
  def add_element(self,*element):
    self.args.extend(element)
  def to_string(self):
    out = ''
    for a in self.args:
      out += a.to_string()
    return out
  
class py_for(py_base):
  def __init__(self,target,expr_list,*args):
    py_base.__init__(self)
    self.args.append(target)
    self.args.append(expr_list)
    self.args.extend(args)
  def add_statement(self,*element):
    self.args.extend(element)
  def to_string(self):
    out = indent_string() + 'for ' + self.args[0].to_string() 
    out += ' in ' + self.args[1].to_string() + ':\n'
    change_indent_level(1)
    for arg in self.args[2:]:
      out += arg.to_string()
    change_indent_level(-1)
    return out

class py_if(py_base):
  def __init__(self,test,true_stmts=None,false_stmts=None):
    py_base.__init__(self)
    self.args.append(test)
    if true_stmts == None:
      self.args.append(py_stmt_block())
    else:
      self.args.append(py_stmt_block(true_stmts))
    if false_stmts == None:
      self.args.append(py_stmt_block())
    else:
      self.args.append(py_stmt_block(false_stmts))
      
  def add_true_statement(self,*element):
    self.args[1].add_statements(*element)
  def add_false_statement(self,*element):
    self.args[2].add_statements(*element)
  def to_string(self):
    out = indent_string() + 'if ' + self.args[0].to_string()  + ':\n'
    change_indent_level(1)
    out += self.args[1].to_string()
    change_indent_level(-1)
    if len(self.args[2].args) > 0:
      out += indent_string() + 'else:\n'
      change_indent_level(1)
      out += self.args[2].to_string()
      change_indent_level(-1)
    return out

class py_except(py_base):
  def __init__(self,except_name,except_stmts=None):
    py_base.__init__(self)
    self.except_name = except_name
    if except_stmts:
      self.args.append(except_stmts)
  def add_statements(*stmts):
    self.args.extend(stmts)
  def to_string(self):
    out = indent_string() + 'except ' + self.except_name + ':\n'
    change_indent_level(1)
    for arg in self.args:
      out += arg.to_string()
    change_indent_level(-1)
    return out
    
class py_try(py_base):
  def __init__(self,body_stmts=None,except_stmts=None):
    py_base.__init__(self)
    if body_stmts == None:
      self.args.append(py_stmt_block())
    else:
      self.args.append(py_stmt_block(*body_stmts))
    if except_stmts:
      self.args.append(except_stmts)
  def to_string(self):
    out = indent_string() + 'try:\n'
    change_indent_level(1)
    out += self.args[0].to_string()
    change_indent_level(-1)
    if len(self.args) > 0:
      out += self.args[1].to_string()
    return out

class py_template(py_base):
  def __init__(self,name):
    py_base.__init__(self)
    self.name = name
  def to_string(self,need_paren=False):
    out = '%' + self.name + '%'
    return out
    
     
