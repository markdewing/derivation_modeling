
from sympy  import *
from sympy.printing.mathml import MathMLPrinter
from sympy.utilities.mathml import c2p
from xml.dom import minidom, Node

class xml_doc(object):
    def __init__(self):
        self.doc = minidom.Document()
        self.create_base_xhtml()
        self.create_base_math()

    def create_base_xhtml(self):
        doc_type = minidom.DocumentType("html")
        doc_type.publicId = "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN"
        doc_type.systemId = "http://www.w3.org/TR/MathML2/dtd/xhtml-math11-f.dtd"
        self.doc.appendChild(doc_type)

    def create_base_math(self):
        html_node = self.create_child_element(self.doc,"html")
        html_node.attributes['xmlns'] = "http://www.w3.org/1999/xhtml"
        html_node.attributes['xmlns:math'] = "http://www.w3.org/1998/Math/MathML"
        self.head_node = self.create_child_element(html_node,"head")
        self.body_node = self.create_child_element(html_node,"body")

    def add_css(self,css):
        self.css = self.create_child_text_element(self.head_node,"style",css)
        self.css.setAttribute("type","text/css")
        

    def create_math_node(self, node):
        math_node = self.create_child_element(node,"math")
        a_str = "http://www.w3.org/1998/Math/MathML"
        math_node.attributes['xmlns'] = a_str
        return math_node

    def add_math_node(self, parent, child_to_add):
        mnode = self.create_math_node(parent)
        mnode.appendChild(child_to_add)

    def add_math(self, parent, expr):
        ml = printing.mathml(expr)
        pm = c2p(ml)
        tree = minidom.parseString(pm)
        self.add_math_node(parent, tree.firstChild)

    def create_child_element(self, parent, name):
        new_node = self.doc.createElement(name)
        parent.appendChild(new_node)
        return new_node

    def create_text_element(self, name, text):
        new_node = self.doc.createElement(name)
        new_text = self.doc.createTextNode(text)
        new_node.appendChild(new_text)
        return new_node

    def create_child_text_element(self, parent, name, text):
        new_node = self.create_text_element(name, text)
        parent.appendChild(new_node)
        return new_node

    def create_link_node(self, parent, link, text):
        new_node = self.doc.createElement('a')
        new_node.attributes['href'] = link
        new_text = self.doc.createTextNode(text)
        new_node.appendChild(new_text)
        parent.appendChild(new_node)
        return new_node


    def toprettyxml(self):
        return self.doc.toprettyxml()

    def toxml(self):
        return self.doc.toxml()


