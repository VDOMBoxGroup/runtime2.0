from __future__ import absolute_import

from codecs import register

from . import htmlcodec
from . import url
from . import xml
from . import cdata
from . import js


register(htmlcodec.search)
register(url.search)
register(xml.search)
register(cdata.search)
register(js.search)
