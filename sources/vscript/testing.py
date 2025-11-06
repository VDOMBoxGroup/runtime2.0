
from builtins import object
from unittest import TestCase
from .engine import vexecute, vcompile
from .variables import variant


class Raises(object):
	
	def __init__(self, exception):
		self._exception=exception

	def __enter__(self):
		pass

	def __exit__(self, exception_class, exception, traceback):
		assert exception is not None
		return isinstance(exception, self._exception)

def raises(exception_class):
	return Raises(exception_class)

class VScriptTestCase(TestCase):
	
	def execute(self, source, value=None, want=None, quiet=1, **keywords):
		environment={"v_%s"%name: value for name, value in keywords.items()}
		if want:
			want="v_%s"%want
		else:
			environment["v_result"]=result=variant()
		if value: source="%s\n%s"%(source, value)
		code, vsource=vcompile(source, environment=environment, anyway=None, quiet=quiet)
		vexecute(code, vsource, environment=environment, quiet=quiet)
		if want:
			assert want in environment
			return environment[want].subtype
		else:
			assert environment.get("v_result") is result
			return result.subtype
	
	def evaluate(self, expression=None, let=None, set=None, quiet=1, **keywords):
		environment={"v_%s"%name: value for name, value in keywords.items()}
		environment["v_result"]=result=variant()
		expression=(u"%s\nresult=%s"%(expression, let) if expression else u"result=%s"%let) if let \
			else (u"%s\nset result=%s"%(expression, set) if expression else u"set result=%s"%set) if set \
			else (u"result=%s"%expression if expression else u"result=null")
		code, vsource=vcompile(expression, environment=environment, anyway=None, quiet=quiet)
		vexecute(code, vsource, environment=environment, quiet=quiet)
		assert environment["v_result"] is result
		return result.subtype
