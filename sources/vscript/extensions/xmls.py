

import xml.dom.minidom
from .. import errors
from ..subtypes import boolean, integer, generic, string, true, false, \
	v_empty, v_mismatch, v_nothing
from ..variables import variant


default_indent="\t"
default_newline="\n"


def wrap(node):
	if node is None:
		return v_nothing
	elif node.nodeType==node.ELEMENT_NODE:
		return v_xmlelement(node)
	elif node.nodeType==node.ATTRIBUTE_NODE:
		return v_xmlattribute(node)
	elif node.nodeType==node.DOCUMENT_NODE:
		return v_xmldocument(node)
	else:
		return v_xmlnode(node)


v_xmlerror=xml.dom.DOMException
v_xmldomstirngsizeerror=xml.dom.DomstringSizeErr
v_xmlhierarchyrequesterror=xml.dom.HierarchyRequestErr
v_xmlindexsizeerror=xml.dom.IndexSizeErr
v_xmlinuseattributeerror=xml.dom.InuseAttributeErr
v_xmlinvalidaccesserror=xml.dom.InvalidAccessErr
v_xmlinvalidcharactererror=xml.dom.InvalidCharacterErr
v_xmlinvalidmodificationerror=xml.dom.InvalidModificationErr
v_xmlinvalidstateerror=xml.dom.InvalidStateErr
v_xmlnamespaceerror=xml.dom.NamespaceErr
v_xmlnotfounderror=xml.dom.NotFoundErr
v_xmlnotsupportederror=xml.dom.NotSupportedErr
v_xmlnodataallowederror=xml.dom.NoDataAllowedErr
v_xmlnodataallowederror=xml.dom.NoModificationAllowedErr
v_xmlsyntaxerror=xml.dom.SyntaxErr
v_xmlwrongdocumenterror=xml.dom.WrongDocumentErr


class v_xmlnodelist(generic):

	def __init__(self, nodes):
		self._nodes=nodes


	def __call__(self, *arguments, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property
		else:
			if len(arguments)!=1: raise errors.wrong_number_of_arguments
			return wrap(self._nodes.item(arguments[0].as_integer))


	def v_length(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("length")
		else:
			return integer(self._nodes.length)

	def v_item(self, index):
		return wrap(self._nodes.item(index.as_integer))


	def __iter__(self):
		for node in self._nodes: yield variant(wrap(node))

	def __len__(self):
		return self._nodes.length


class v_xmlnode(generic):

	def __init__(self, node):
		self._node=node


	def v_parent(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("parent")
		else:
			return wrap(self._node.parentNode)

	def v_prev(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("prev")
		else:
			return wrap(self._node.previousSibling)

	def v_next(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("next")
		else:
			return wrap(self._node.nextSibling)

	def v_attributes(self, index=None, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("attributes")
		else:
			attributes=self._node.attributes
			collection=v_nothing if attributes is None else v_xmlattributemap(attributes)
			return collection if index is None else collection(index)

	def v_nodes(self, index=None, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("nodes")
		else:
			nodes=self._node.childNodes
			collection=v_nothing if nodes is None else v_xmlnodelist(nodes)
			return collection if index is None else collection(index)

	def v_first(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("first")
		else:
			return wrap(self._node.firstChild)

	def v_last(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("last")
		else:
			return wrap(self._node.lastChild)

	def v_name(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("name")
		else:
			name=self._node.nodeName
			return string(name) if isinstance(name, bytes) else v_empty

	def v_localname(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("localname")
		else:
			name=self._node.localName
			return string(name) if isinstance(name, bytes) else v_empty

	def v_prefix(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("prefix")
		else:
			name=self._node.prefix
			return string(name) if isinstance(name, bytes) else v_empty

	def v_namespaceuri(self, **keywords):
		raise errors.not_implemented
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("namespaceuri")
		else:
			uri=self._node.namespaceURI
			return string(uri) if isinstance(uri, bytes) else v_empty

	def v_value(self, **keywords):
		if "let" in keywords:
			self._node.nodeValue=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("value")
		else:
			value=self._node.nodeValue
			return string(value) if isinstance(value, bytes) else v_empty


	def v_unlink(self):
		self._node.unlink()
		return v_mismatch

	def v_type(self):
		raise errors.not_implemented

	def v_hasattributes(self):
		return boolean(self._node.hasAttributes())

	def v_hasnodes(self):
		return boolean(self._node.hasChildNodes())

	def v_iselement(self):
		return boolean(self._node.nodeType==self._node.ELEMENT_NODE)

	def v_isattribute(self):
		return boolean(self._node.nodeType==self._node.ATTRIBUTE_NODE)

	def v_istext(self):
		return boolean(self._node.nodeType==self._node.TEXT_NODE)

	def v_iscdata(self):
		return boolean(self._node.nodeType==self._node.CDATA_SECTION_NODE)

	def v_isentity(self):
		# return boolean(self._node.nodeType==self._node.ENTITY_NODE)
		raise errors.not_implemented

	def v_isprocessinginstruction(self):
		# return boolean(self._node.nodeType==self._node.PROCESSING_INSTRUCTION_NODE)
		raise errors.not_implemented

	def v_iscomment(self):
		return boolean(self._node.nodeType==self._node.COMMENT_NODE)

	def v_isdocument(self):
		return boolean(self._node.nodeType==self._node.DOCUMENT_NODE)

	def v_isdocumenttype(self):
		# return boolean(self._node.nodeType==self._node.DOCUMENT_TYPE_NODE)
		raise errors.not_implemented

	def v_isnotation(self):
		# return boolean(self._node.nodeType==self._node.NOTATION_NODE)
		raise errors.not_implemented

	def v_issamenode(self, node):
		node=node.as_is
		if isinstance(v_xmlnode, node):
			return boolean(self._node.isSameNode(node.node))
		else:
			return boolean(false)

	def v_append(self, node):
		node=node.as_is
		if isinstance(node, v_xmlnode):
			self._node.appendChild(node._node)
			return v_mismatch
		else:
			raise errors.invalid_procedure_call(name="append")

	def v_insert(self, node, reference):
		node, reference=node.as_is, reference.as_is
		if isinstance(node, v_xmlnode) and isinstance(reference, v_xmlnode):
			self._node.insertBefore(node._node, reference._node)
			return v_mismatch
		else:
			raise errors.invalid_procedure_call(name="insert")

	def v_remove(self, node):
		node=node.as_is
		if isinstance(node, v_xmlnode):
			self._node.removeChild(node._node)
			return v_mismatch
		else:
			raise errors.invalid_procedure_call(name="remove")

	def v_replace(self, node, reference):
		node, reference=node.as_is, reference.as_is
		if isinstance(node, v_xmlnode) and isinstance(reference, v_xmlnode):
			self._node.replaceChild(reference, node._node)
			return v_mismatch
		else:
			raise errors.invalid_procedure_call(name="replace")

	def v_normalize(self):
		self._node.normalize()
		return v_mismatch

	def v_clone(self, deep=None):
		if deep is None:
			return wrap(self._node.cloneNode())
		else:
			return wrap(self._node.cloneNode(deep.as_boolean))

	def v_compose(self, indent=None, newline=None):
		if indent is None and newline is None:
			return string(self._node.toxml())
		else:
			return string(self._node.toprettyxml(
				indent=default_indent if indent is None else indent.as_string,
				newline=default_newline if newline is None else newline.as_string))


class v_xmlattributemap(generic):

	def __init__(self, attributes):
		self._attributes=attributes


	def v_length(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("length")
		else:
			return integer(self._attributes.length)


	def v_item(self, index):
		return v_xmlattribute(self._attributes.item(index.as_integer))


	def __iter__(self):
		for attribute in list(self._attributes.values()):
			yield variant(v_xmlattribute(attribute))

	def __len__(self):
		return integer(self._attributes.length)

class v_xmlattribute(v_xmlnode):

	def v_name(self, **keywords):
		if "let" in keywords:
			self._node.name=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("name")
		else:
			return string(self._node.name)


class v_xmlelementlist(v_xmlnodelist):

	def __iter__(self):
		for node in self._nodes:
			if node.nodeType==node.ELEMENT_NODE: yield wrap(node)

class v_xmlelement(v_xmlnode):

	def v_name(self, **keywords):
		if "let" in keywords:
			self._node.tagName=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("name")
		else:
			return string(self._node.tagName)

	def v_elements(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("elements")
		else:
			nodes=self._node.childNodes
			return v_nothing if nodes is None else v_xmlelementlist(nodes)


	def v_search(self, name):
		nodes=self._node.getElementsByTagName(name.as_string)
		return v_nothing if nodes is None else v_xmlelementlist(nodes)

	def v_searchns(self, namespaceuri, name):
		nodes=self._node.getElementsByTagNameNS(namespaceuri.as_string, name.as_string)
		return v_nothing if nodes is None else v_xmlelementlist(nodes)

	def v_hasattribute(self, name):
		return boolean(self._node.hasAttribute(name.as_string))

	def v_hasattributens(self, namespaceuri, name):
		return boolean(self._node.hasAttributeNS(namespaceuri.as_string, name.as_string))

	def v_getattribute(self, name, default=None):
		name=name.as_string
		if default is None:
			return string(self._node.getAttribute(name))
		else:
			if self._node.hasAttribute(name):
				return string(self._node.getAttribute(name))
			else:
				return string(default.as_string)

	def v_getattributens(self, namespaceuri, name, default=None):
		name=name.as_string
		if default is None:
			return string(self._node.getAttributeNS(namespaceuri.as_string, name))
		else:
			if self._node.hasAttribute(name):
				return string(self._node.getAttributeNS(namespaceuri.as_string, name))
			else:
				return string(default.as_string)

	def v_getattributenode(self, name):
		node=self._node.getAttributeNode(name.as_string)
		return v_nothing if node is None else v_xmlattribute(node)

	def v_getattributenodens(self, namespaceuri, name):
		node=self._node.getAttributeNodeNS(namespaceuri.as_string, name.as_string)
		return v_nothing if node is None else v_xmlattribute(node)

	def v_setattribute(self, name, value):
		self._node.setAttribute(name.as_string, value.as_string)
		return v_mismatch

	def v_setattributens(self, namespaceuri, name, value):
		self._node.setAttributeNS(namespaceuri.as_string,
			name.as_string, value.as_string)
		return v_mismatch

	def v_setattributenode(self, node):
		node=node.as_is
		if isinstance(node, v_xmlattribute):
			return wrap(self._node.setAttributeNode(node._node))
		else:
			raise errors.invalid_procedure_call(name="setattributenode")

	def v_setattributenodens(self, namespaceuri, node):
		node=node.as_is
		if isinstance(node, v_xmlattribute):
			return wrap(self._node.setAttributeNodeNS(namespaceuri.as_string, node))
		else:
			raise errors.invalid_procedure_call(name="setattributenode")

	def v_removeattribute(self, name):
		self._node.removeAttribute(name.as_string)
		return v_mismatch

	def v_removeattributens(self, namespaceuri, name):
		self._node.removeAttributeNS(namespaceuri.as_string, name.as_string)
		return v_mismatch



class v_xmldocument(v_xmlelement):

	def __init__(self):
		self._document=xml.dom.minidom.Document()
		self._node=self._document.documentElement

	def v_parse(self, value):
		value=value.as_string
		self._document=xml.dom.minidom.parseString(value.encode("utf-8") \
			if isinstance(value, str) else value)
		self._node=self._document.documentElement
		return v_mismatch

	def v_doctype(self):
		raise errors.not_implemented

	def v_createelement(self, name):
		return v_xmlelement(self._document.createElement(name.as_string))

	def v_createelementns(self, namespaceuri, name):
		return v_xmlelement(
			self._document.createElementNS(namespaceuri.as_string, name.as_string))

	def v_createtextnode(self, value):
		return v_xmlnode(self._document.createTextNode(value.as_string))

	def v_createcomment(self, value):
		return v_xmlnode(self._document.createTextNode(value.as_string))

	def v_createprocessinginstruction(self, target, value):
		raise errors.not_implemented

	def v_createattribute(self, name):
		return v_xmlattribute(self._document.createAttribute(name.as_string))

	def v_createattributens(self, namespaceuri, name):
		return v_xmlattribute(
			self._document.createAttributeNS(namespaceuri.as_string, name.as_string))
