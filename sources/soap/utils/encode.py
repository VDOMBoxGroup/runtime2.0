"""encode module - implements all required encoding algorithms"""

import zlib
import base64


def encode_resource(data):
    """encode resource to be sent through web services"""
    return base64.b64encode(zlib.compress(data))


def need_xml_escape(data):
    if isinstance(data, bytes) and ('<' in data or '>' in data or '&' in data or '\'' in data or '\"' in data or '\n' in data):
        return True
    return False


def write_to_xml_node(doc, node, data):
    # remove all child nodes
    while node.hasChildNodes():
        node.removeChild(node.firstChild)
# parts = []
    start = 0
    while True:
        i = data.find("]]>", start)
        if -1 == i:
            break
# parts.append(data[start:i+2])
        node.appendChild(doc.createCDATASection(data[start:i + 2]))
        start = i + 2
# parts.append(data[start:])
    node.appendChild(doc.createCDATASection(data[start:]))
    # debug("")
    # debug(data)
    # debug(str(parts))
    # debug("")
# for p in parts:
# node.appendChild(doc.createCDATASection(p))


def attrvalue(data):
    if need_xml_escape(data):
        result = data.replace("]]>", "]]]]><![CDATA[>")
        return "<![CDATA[" + result + "]]>"
    return data
