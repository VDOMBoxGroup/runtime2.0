import os
from xml.dom.minidom import parse
from xml.dom.minidom import parseString
from xml.dom import Node
from xml.dom.minidom import DOMImplementation


def need_cdata(data):
    if data != "" and ('<' in data or '>' in data or '"' in data or '&' in data or "'" in data or "\n" in data):
        return True
    return False


def write_text_to_node(doc, node, data):
    while node.hasChildNodes():
        node.removeChild(node.firstChild)
    if need_cdata(data):
        start = 0
        while True:
            i = data.find("]]>", start)
            if -1 == i:
                break
            node.appendChild(doc.createCDATASection(data[start:i+2]))
            start = i + 2
        node.appendChild(doc.createCDATASection(data[start:]))
    else:
        node.appendChild(doc.createTextNode(data))


class _lst(list):

    def __init__(self, _xml_object):
        if not isinstance(_xml_object, xml_object):
            raise ValueError()
        self.xml_object = _xml_object
        list.__init__(self)

    def append(self, some):
        if isinstance(some, xml_object):
            if not hasattr(self.xml_object, "parsing"):
                if not self.xml_object.node or some.node:
                    raise ValueError()
                if not some.name:
                    raise ValueError()
                if len(some.children) > 0:
                    raise ValueError()
                some.parent = self.xml_object  # set parent of the new element
                some.xml_doc = self.xml_object.xml_doc  # set ref to xml document
                some.level = some.parent.level + 1  # increase level
                # element
                some.node = some.xml_doc.createElement(some.name)
                b = some.parent.node.hasChildNodes()
                if not b:
                    some.parent.node.appendChild(some.xml_doc.createTextNode("\n" + "\t"*some.level))
                    some.parent.node.appendChild(some.node)
                    some.parent.node.appendChild(some.xml_doc.createTextNode("\n" + "\t"*some.parent.level))
                else:
                    some.parent.node.insertBefore(some.xml_doc.createTextNode("\n" + "\t"*some.level), some.parent.node.lastChild)
                    some.parent.node.insertBefore(some.node, some.parent.node.lastChild)
                # attributes
                for a in some.attributes:
                    some.node.setAttribute(some.attributes.get_original_key(a), some.attributes[a])
                # value
                if some.value:
                    write_text_to_node(some.xml_doc, some.node, some.value)
            list.append(self, some)
        else:
            raise ValueError()

    def __delitem__(self, i):
        self.pop(i)

    def pop(self, i=-1):
        x = self[i]
        self.remove(x)
        return x

    def remove(self, some):
        if isinstance(some, xml_object) and some in self:
            if not hasattr(self.xml_object, "parsing") and self.xml_object.node and some.node:
                if 1 == len(self):
                    self.xml_object.node.removeChild(some.node.previousSibling)
                    self.xml_object.node.removeChild(some.node.nextSibling)
                    self.xml_object.node.removeChild(some.node)
                else:
                    self.xml_object.node.removeChild(some.node.previousSibling)
                    self.xml_object.node.removeChild(some.node)
            list.remove(self, some)
            some.parent = None
        else:
            raise ValueError()


class _dct(dict):

    def __init__(self, _xml_object):
        if not isinstance(_xml_object, xml_object):
            raise ValueError()
        self.xml_object = _xml_object
        dict.__init__(self)

    def __setitem__(self, key, value):
        if not isinstance(key, basestring):
            raise TypeError()
        if not isinstance(value, basestring):
            raise ValueError()
        if not hasattr(self.xml_object, "parsing") and self.xml_object.node:
            _k = key
            if key.lower() in self:
                _k = self.get_original_key(key)
            self.xml_object.node.setAttribute(_k, value)
        x = (value, key)
        dict.__setitem__(self, key.lower(), x)

    def __getitem__(self, key):
        if not isinstance(key, basestring):
            raise TypeError()
        x = dict.__getitem__(self, key.lower())
        return x[0]

    def __delitem__(self, key):
        if not hasattr(self.xml_object, "parsing") and self.xml_object.node and key in self:
            self.xml_object.node.removeAttribute(key)
        dict.__delitem__(self, key.lower())

    def get_original_key(self, key):
        if not isinstance(key, basestring):
            raise TypeError()
        x = dict.__getitem__(self, key.lower())
        return x[1]

    def get(self, key, x=None):
        if key in self:
            y = dict.__getitem__(self, key.lower())
            return y[0]
        return x


class xml_object(object):

    def __init__(self, source=None, parent=None, name=None, srcdata=None):
        self.node = None
        self.level = None
        self.parent = parent
        self.xml_doc = None

        self.name = name
        if self.name:
            self.lname = self.name.lower()
        else:
            self.lname = None
        self.value = ""
        self.attributes = _dct(self)
        self.children = _lst(self)

        setattr(self, "parsing", None)

        if srcdata and isinstance(srcdata, basestring):
            self.xml_doc = parseString(srcdata)
            self.node = self.xml_doc.documentElement
            self.level = 0
        else:
            # if source is a string, consider it a file name and parse
            if isinstance(source, basestring):
                self.xml_doc = parse(source)
                self.node = self.xml_doc.documentElement
                self.level = 0
            else:
                self.node = source

        if self.parent:
            self.level = self.parent.level + 1
            self.xml_doc = self.parent.xml_doc

        if self.node:
            self.__parse()

        delattr(self, "parsing")

#	def __del__(self):
#		print "Del", self.name

    def get_child_by_name(self, name):
        l = name.lower()
        for c in self.children:
            if c.lname == l:
                return c
        return None

    def get_value_as_xml(self):
        value = ""
        if self.node.hasChildNodes():
            for ch in self.node.childNodes:
                if ch.nodeType == Node.CDATA_SECTION_NODE:
                    value += ch.data
                elif ch.nodeType == Node.TEXT_NODE and not ch.data.strip():
                    pass
                else:
                    value += ch.toxml()
        return value

    def delete(self):
        if self.parent:
            self.exclude()
        if self.children:
            while len(self.children) > 0:
                x = self.children.pop()
                x.delete()
        self.children = None
        self.attributes = None
        self.node = None
        self.xml_doc = None

    def exclude(self):
        if self.parent:
            self.parent.children.remove(self)

    def append_as_copy(self, some):
        if isinstance(some, xml_object):
            if not some.name:
                raise ValueError
            x = xml_object(name=some.name)
            self.children.append(x)
            for a in some.attributes:
                x.attributes[some.attributes.get_original_key(a)] = some.attributes[a]
            if some.value:
                x.value = some.value
            else:
                for y in some.children:
                    x.append_as_copy(y)
            return x
        else:
            raise ValueError

    def as_root(self):
        x = DOMImplementation()
        self.xml_doc = x.createDocument("", self.name, None)
        self.node = self.xml_doc.documentElement
        self.level = 0

    def __setattr__(self, name, value):
        if not hasattr(self, "parsing") and hasattr(self, "node") and self.node:
            if "name" == name:
                if not isinstance(value, basestring):
                    raise ValueError()
                self.node.tagName = value
                self.lname = value.lower()
            elif "value" == name:
                if not isinstance(value, basestring):
                    raise ValueError()
                if len(self.children) > 0:
                    raise ValueError()
                write_text_to_node(self.xml_doc, self.node, value)
        object.__setattr__(self, name, value)

    def __parse(self):
        self.name = self.node.nodeName
        self.lname = self.name.lower()
        for i in xrange(self.node.attributes.length):
            attr = self.node.attributes.item(i)
            self.attributes[attr.name] = self.node.getAttribute(attr.name)
        v = ""
        f = False
        e = True
        i = 0
        while i < len(self.node.childNodes):
            child = self.node.childNodes[i]
            if child.nodeType == Node.ELEMENT_NODE:
                if e:
                    self.node.insertBefore(self.xml_doc.createTextNode("\n" + "\t"*(self.level + 1)), child)
                    i += 1
                e = True
                self.children.append(xml_object(child, self))
            elif child.nodeType in [Node.TEXT_NODE, Node.CDATA_SECTION_NODE] and child.data != "\n":
                e = False
                if child.nodeType == Node.TEXT_NODE:
                    v += child.data.strip()
                else:
                    v += child.data
                f = True
            i += 1
        if f:
            self.value = v
        if e:
            self.node.appendChild(self.xml_doc.createTextNode("\n" + "\t"*self.level))

    def toxml(self, encode=True):
        if encode:
            if not self.parent:
                return self.xml_doc.toxml(encoding="utf-8")
            elif self.node:
                return self.node.toxml(encoding="utf-8")
        else:
            if not self.parent:
                return self.xml_doc.toxml()
            elif self.node:
                return self.node.toxml()
        return ""

    def __repr__(self):
        if not self.node:
            return "empty xml_object instance"
        else:
            return self.__do_repr(self, 0)

    def __do_repr(self, o, l):
        p = '\t'*l
        result = p + o.name + " ["
        r = ""
        for a in o.attributes:
            if r != "":
                r += ", "
            r += a + "=" + o.attributes[a]
        result += r + "]"
        if o.value:
            result += " " + o.value
        result += "\n"
        for a in o.children:
            result += self.__do_repr(a, l + 1)
        return result

    def sync(self, fname, keep_metadata=False):
        if keep_metadata:
            if os.path.exists(fname):
                times = os.stat(fname)[7:9]  # (st_atime, st_mtime)
            else:
                times = None
        f = open(fname, "wb")
        if not self.parent:
            f.write(self.xml_doc.toxml(encoding="utf-8"))
        elif self.node:
            f.write('<?xml version="1.0" ?>')
            f.write(self.node.toxml(encoding="utf-8"))
        f.close()

        if keep_metadata:
            os.utime(fname, times)


def f1():
    x = xml_object("z.xml")
    print x
    return 0


# test
if __name__ == "__main__":
    f1()
    import gc
    gc.collect()
    print len(gc.garbage)
    x = raw_input()
    #import gc
    print "x"
    x = xml_object("z.xml")
    x.children.pop(0)
    print x.toxml()
    x = raw_input()

    a = xml_object()
    a.name = "test"
    a.attributes["gg"] = "ff"
    x.children.append(a)

    c = xml_object()
    c.name = "test!"
    c.attributes["gg"] = "ff"
    x.children.append(c)

    b = xml_object()
    b.name = "test1"
    b.value = "x"
    a.children.append(b)

    d = xml_object()
    d.name = "test3"
    d.value = "x"
    #c.children.append(d)

#	print x
#	print x.toxml()
    b.name = "test2"
    b.value = "y"
    del a.attributes["gg"]
    a.attributes["ff"] = "gg"

    del x.children[1]  # remove(c)
    #c.children.pop()
    #print x
#	print x.toxml()
    x.delete()
    del x
    #c.sync("aaa.xml")
    #del c, d
    x = raw_input()

#	z = xml_object()
#	z.name = "sample"
#	z.as_root()
#	z.children.append(d)
#	print z.toxml()
#	z.sync("bbb.xml")
