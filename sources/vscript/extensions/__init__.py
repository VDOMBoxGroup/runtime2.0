
from .wscript import v_wscript
from .regexp import v_regexp
# IIf(condition, truepart, falsepart): the inline if VBScript has and the core
# lacked. Both branches are evaluated, as VBScript does.
from .vails_ext import v_iif
from .list import v_list
from .connection import v_connectionerror, v_proxy, v_connection
from .jsons import v_asjson, v_tojson
from .xmls import v_xmlnode, v_xmlattribute, v_xmlelement, v_xmldocument, \
    v_xmlerror, v_xmldomstirngsizeerror, v_xmlhierarchyrequesterror, \
    v_xmlindexsizeerror, v_xmlinuseattributeerror, v_xmlinvalidaccesserror, \
    v_xmlinvalidcharactererror, v_xmlinvalidmodificationerror, v_xmlinvalidstateerror, \
    v_xmlnamespaceerror, v_xmlnotfounderror, v_xmlnotsupportederror, \
    v_xmlnodataallowederror, v_xmlnodataallowederror, v_xmlsyntaxerror, \
    v_xmlwrongdocumenterror
from .constraint import v_problem
from .evalstring import v_evalstring, v_evalcontext, v_evalvariable, v_evalglobalcontext
from .freepdf import v_fpdf
