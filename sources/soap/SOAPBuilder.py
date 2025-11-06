"""SOAPpy types bug fixed: SOAPBuilderE.dump reimplementing dump method that is broken in library"""


import SOAPpy
from SOAPpy.Config import Config
from SOAPpy.NS     import NS
from SOAPpy.Types  import *

from SOAPpy.SOAPBuilder import SOAPBuilder,pythonHasBooleanType


class SOAPBuilderE( SOAPBuilder ):

	def dump(self, obj, tag = None, typed = 1, ns_map = {}):
		ns_map = ns_map.copy()
		self.depth += 1

		if type(tag) not in (NoneType, StringType, UnicodeType ):
			raise KeyError("tag must be a string or None")

		try:
			if type(obj).__name__ in ["arrayType", "faultType", "voidType", "structType", "bodyType", "anyType"]:
				meth = getattr(self, "dump_instance" );
			else:
				meth = getattr(self, "dump_" + type(obj).__name__)
		except AttributeError:
			if type(obj) == LongType:
				obj_type = "integer"
			elif pythonHasBooleanType and type(obj) == BooleanType:
				obj_type = "boolean"
			else:
				obj_type = type(obj).__name__

			self.out.append(self.dumper(None, obj_type, obj, tag, typed,
						    ns_map, self.genroot(ns_map)))
		else:
			meth(obj, tag, typed, ns_map)


		self.depth -= 1

def buildSOAPE(args=(), kw={}, method=None, namespace=None,
	       header=None, methodattrs=None, envelope=1, encoding='UTF-8',
	       config=Config, noroot = 0):
	t = SOAPBuilderE(args=args, kw=kw, method=method, namespace=namespace,
			 header=header, methodattrs=methodattrs,envelope=envelope,
			 encoding=encoding, config=config,noroot=noroot)
	return t.build()


SOAPpy.buildSOAP = buildSOAPE