
from ...testing import VScriptTestCase


"""
set xml=new xmldocument
xml.parse("<xml a1='1' a2='2'><a>A</a><b>B</b><c>C</c></xml>")

for each element in xml.elements
    print element.name
next

print xml.search("b").length

set attribute=xml.getattributenode("a1")
print attribute.name, "=", attribute.value

for each attribute in xml.attributes
    print attribute.name
next

print xml.compose
"""


class TestXmlExtension(VScriptTestCase):

    def test_xmldocument_creation(self):
        assert self.evaluate(set="new xmldocument").is_generic

    def test_xmldocument_parsing(self):
        assert self.execute("""
            set xml=new xmldocument
            xml.parse("<xml><node>node</node></xml>")
            result=xml.search("node")(0).nodes(0).value""").is_string(u"node")
