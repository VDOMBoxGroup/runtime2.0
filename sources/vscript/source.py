from copy import deepcopy
from importlib import import_module
from . import errors, lexemes, error
from .register import register

import settings


__all__ = ["vname", "vmybase", "vme", "vmyclass", "vnames",
           "vexpression", "vexpressions",
           "vsubscripts", "varguments", "vstatements", "vdeclarations", "vredim",
           "verase", "vlet", "vset", "vuse", "vpython", "vconstant", "vcall",
           "velseif", "velseifs", "vifthen", "vifthenelse",
           "vselectcase", "vselectcases", "vselect", "vselectelse",
           "vdoloop", "vdowhileloop", "vdountilloop", "vdoloopwhile", "vdoloopuntil",
           "vforeach", "vfor", "vforstep",
           "vtrycatch", "vtrycatches", "vtry", "vtryfinally", "vthrow",
           "vwith", "vexitfunction", "vexitsub", "vexitproperty", "vexitdo", "vexitfor",
           "vrandomize", "vprint", "vtouch", "vglobals",
           "vfunction", "vsub", "vpropertyget", "vpropertylet", "vpropertyset",
           "vinherits", "vclass", "vsource"]


no_explicit = 1  # try to emulate OPTION EXPLICIT OFF behaviour

absent = "ABSENT"

vscript_constructor = "%sclass_initialize" % lexemes.prefix
vscript_destructor = "%sclass_terminate" % lexemes.prefix

python_default = "__call__"
python_constructor = "__init__"
python_destructor = "__del__"
python_result = "result"
python_value = "subtype"


class vself:

    def __init__(self, line=None):
        pass

    def scope_names(self, mysource, myclass, myprocedure):
        pass

    def __str__(self):
        return "self"


class vname:

    def __init__(self, base, line=None):
        self.line = line
        self.base = base
        self.string = "%s"
        self.values = ()
        self.check = 1

    def join(self, value):
        if isinstance(value, (vexpression, vexpressions)):
            self.string += "(%s)"
            self.values += (value, )
            self.check = 0
        else:
            if self.check:
                self.string = "check(%s)" % self.string
            self.string = "%s.%s" % (self.string, value)
            self.check = 1
        return self

    def let(self, value):
        if not self.values:
            self.join(vexpressions())
        self.values[-1].let(value)
        return self

    def set(self, value):
        if not self.values:
            self.join(vexpressions())
        self.values[-1].set(value)
        return self

    def scope_names(self, mysource, myclass, myprocedure):
        if self.base is None:
            if not mysource.withs:
                raise errors.syntax_error(
                    "Invalid or unqualified reference", line=self.line)
            self.member = 0
            self.base = mysource.withs[-1]
        elif self.base in mysource.trys:
            self.member = 0
        elif myprocedure and self.base in myprocedure.names:
            self.member = 0
            if self.base == myprocedure.name:
                if self.values:
                    if myclass and myclass.check_name_deeply(self.base):
                        self.member = 1
                else:
                    self.base = python_result
        # self.base in myclass.names
        elif myclass and myclass.check_name_deeply(self.base):
            self.member = 1
        elif self.base in mysource.names:
            self.member = 0
            if myprocedure:
                myprocedure.globals.append(self.base)
        elif self.base in mysource.using:
            self.member = 0
            if self.base not in mysource.using[self.base].import_names:
                mysource.using[self.base].import_names.append(self.base)
        elif myprocedure and no_explicit:
            self.member = 0
            myprocedure.names[self.base] = "variant()"
        elif no_explicit:
            self.member = 0
            mysource.names[self.base] = "variant()"
        else:
            raise errors.variable_is_undefined(self.base, line=self.line)

        for expressions in self.values:
            expressions.scope_names(mysource, myclass, myprocedure)

    def __str__(self):
        result = self.string % (
            ("self.%s" % self.base if self.member else self.base, ) + self.values)
        return "check(%s)" % result if self.check else result


class vnames(list):

    def __init__(self, line=None):
        self.line = line

    def join(self, name):
        self.append(vname(name))
        return self

    def scope_names(self, mysource, myclass, myprocedure):
        for name in self:
            name.scope_names(mysource, myclass, myprocedure)

    def __str__(self):
        return ", ".join([str(name) for name in self])


class vme(vname):

    def __init__(self, line=None):
        vname.__init__(self, None, line=line)
        self.expression = None
        self.check = 0

    def join(self, value):
        if isinstance(value, vexpressions) and self.expression is None:
            self.expressions = value.classify()
        return vname.join(self, value)

    def scope_names(self, mysource, myclass, myprocedure):
        if myclass is None:
            raise error.object_required(name="my", line=self.line)
        self.member = 0
        self.base = "self"

        for expressions in self.values:
            expressions.scope_names(mysource, myclass, myprocedure)


class vmybase(vname):

    def __init__(self, line=None):
        vname.__init__(self, None, line=line)
        self.expression = None
        self.check = 0

    def join(self, value):
        if isinstance(value, vexpressions) and self.expression is None:
            self.expressions = value.classify()
        return vname.join(self, value)

    def scope_names(self, mysource, myclass, myprocedure):
        if myclass is None:
            raise error.object_required(name="mybase", line=self.line)
        self.member = 0
        self.base = myclass.inherits

        for expressions in self.values:
            expressions.scope_names(mysource, myclass, myprocedure)


class vmyclass(vname):

    def __init__(self, line=None):
        vname.__init__(self, None, line=line)
        self.expression = None
        self.check = 0

    def join(self, value):
        if isinstance(value, vexpressions) and self.expression is None:
            self.expressions = value.classify()
        return vname.join(self, value)

    def scope_names(self, mysource, myclass, myprocedure):
        if myclass is None:
            raise error.object_required(name="myclass", line=self.line)
        self.member = 0
        self.base = myclass.name

        for expressions in self.values:
            expressions.scope_names(mysource, myclass, myprocedure)


class vexpression:

    def __init__(self, string, values=None, line=None):
        self.line = line
        self.string = string
        self.values = values or ()

    def join(self, string, value):
        if isinstance(value, vexpression):
            self.string = string % (self.string, value.string)
            self.values += value.values
        else:
            self.string = string % (
                self.string, " ,".join(["%s"] * len(value)))
            self.values += tuple(value)
        return self

    def apply(self, string):
        self.string = string % self.string
        return self

    def scope_names(self, mysource, myclass, myprocedure):
        for value in self.values:
            value.scope_names(mysource, myclass, myprocedure)

    def __str__(self):
        return self.string % self.values


class vexpressions(list):

    def __init__(self, line=None):
        self.line = line

    def join(self, expression):
        self.append(expression)
        return self

    def let(self, value):
        self.append(value.apply("let=%s"))
        return self

    def set(self, value):
        self.append(value.apply("set=%s"))
        return self

    def classify(self):
        self.insert(0, vself())
        return self

    def scope_names(self, mysource, myclass, myprocedure):
        for expression in self:
            expression.scope_names(mysource, myclass, myprocedure)

    def __str__(self):
        return ", ".join(map(str, self))


class vsubscripts(list):

    def __init__(self):
        pass

    def join(self, dimension):
        self.append(dimension)
        return self

    def scope_names(self, mysource, myclass, myprocedure):
        pass

    def __str__(self):
        return "[%s]" % ", ".join(map(str, self))


class varguments(list):

    def __init__(self):
        pass

    def join(self, argument):
        self.append(argument)
        return self

    """
    initialization=property(lambda self: u"=".join(filter(None,
        [u", ".join([name for name, type in self if type]),
        u", ".join([u"%s(%s)"%(type, name) for name, type in self if type])])))
    """
    initialization = property(lambda self: "=".join([_f for _f in [", ".join([name for name, type in self if type]),
                                                                    ", ".join(["%s.%s" % (name, type) for name, type in self if type])] if _f]))

    def __str__(self):
        return ", ".join([argument[0] for argument in self])


class vstatements(list):

    def __init__(self):
        pass

    def join(self, statement):
        if statement:
            self.append(statement)
        return self

    def collect_names(self, names):
        for statement in self:
            statement.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        for statement in self:
            statement.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident, precede=None, follow=None):
        contents = []
        if precede:
            contents.extend(precede)
        for statement in self:
            contents.extend(statement.compose(ident))
        if follow:
            contents.extend(follow)
        contents = [line for line in contents if line[2]]
        return contents if contents else [(None, ident, "pass")]


class vstatement:

    def __init__(self, line=None):
        self.line = line

    def collect_names(self, names):
        pass

    def scope_names(self, mysource, myclass, myprocedure):
        pass

    def compose(self, ident):
        return tuple()


class vdeclarations(dict, vstatement):

    def __init__(self, line=None):
        vstatement.__init__(self, line)

    def join(self, name, value):
        if name in self:
            raise errors.name_redefined(name, line=self.line)
        self[name] = value
        return self

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        conflicts = set(self).intersection(names)
        if conflicts:
            raise errors.name_redefined(name=conflicts.pop(), line=self.line)
        names.update(self)


class vredim(list, vstatement):

    def __init__(self, preserve, line=None):
        vstatement.__init__(self, line)
        self.preserve = preserve

    def join(self, name, value):
        self.append((name, value))
        return self

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        for name, value in self:
            name.scope_names(mysource, myclass, myprocedure)
            value.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        """
        preserve=", preserve=True" if self.preserve else ""
        return [(self.line, ident, u"redim(%s, [%s]%s)"%\
                (name, value, preserve)) for name, value in self]
        """
        return [(self.line, ident, "%s.redim(%s%s)" %
                (name, self.preserve, ", %s" % value if value else ""))
                for name, value in self]


class verase(vstatement):

    def __init__(self, name, expressions=None, line=None):
        vstatement.__init__(self, line)
        self.name = name
        self.expressions = expressions

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.name.scope_names(mysource, myclass, myprocedure)
        if self.expressions:
            self.expressions.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        """
        return ((self.line, ident, u"erase(%s)"%self.name),)
        """
        return ((self.line, ident, "%s.erase(%s)" % (self.name, self.expressions or "")),)


class vlet(vstatement):

    def __init__(self, name, value, line=None):
        vstatement.__init__(self, line)
        self.name = name
        self.name.check = 0
        self.value = value

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.name.scope_names(mysource, myclass, myprocedure)
        self.value.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        return ((self.line, ident, "%s(let=%s)" % (self.name, self.value)),)


class vset(vstatement):

    def __init__(self, name, value, line=None):
        vstatement.__init__(self, line)
        self.name = name
        self.name.check = 0
        self.value = value

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.name.scope_names(mysource, myclass, myprocedure)
        self.value.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        return ((self.line, ident, "%s(set=%s)" % (self.name, self.value)),)


class vuse(vstatement):

    def __init__(self, name, line, package=None, environment=None):
        vstatement.__init__(self, line)
        self.name = name[2:]
        self.package = package
        self.module = import_module("%s.%s" % (self.package, self.name)) \
            if package else import_module(self.name)
        self.names = []
        internal = register.names
        for name in dir(self.module):
            if name.startswith(lexemes.prefix):
                if name in internal:
                    continue
                if name in environment:
                    continue
                self.names.append(name)

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        mysource.uses.append(self)
        for name in self.names:
            mysource.using[name] = self
        self.import_names = []

    def compose(self, ident):
        return ((self.line, ident, "from %s import %s" % (self.name, ", ".join(self.import_names))),) \
            if self.import_names else ()


class vpython(vstatement):

    def __init__(self, source, line=None):
        vstatement.__init__(self, line)
        self.source = source

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)

    def compose(self, ident):
        if settings.ENABLE_PYTHON_INLINES:
            string = self.source
            return ((self.line, ident, string),)
        else:
            return ()


class vconstant(vstatement):

    def __init__(self, name, value, line=None):
        vstatement.__init__(self, line)
        self.name = name
        self.name.check = 0
        self.value = value

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        if self.name.base in names:
            raise errors.name_redefined(self.name.base, line=self.line)
        names[self.name.base] = None

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.name.scope_names(mysource, myclass, myprocedure)
        self.value.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        return ((self.line, ident, "%s=constant(%s)" % (self.name, self.value)),)


class vcall(vstatement):

    def __init__(self, expression, line=None):
        vstatement.__init__(self, line)
        self.expression = expression

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.expression.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        return ((self.line, ident, "%s" % self.expression),)


class velseif(vstatement):

    def __init__(self, condition, statements, line=None):
        vstatement.__init__(self, line)
        self.condition = condition
        self.statements = statements

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        self.statements.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.condition.scope_names(mysource, myclass, myprocedure)
        self.statements.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = [(self.line, ident, "elif bool(%s):" % self.condition)]
        contents.extend(self.statements.compose(ident + 1))
        return contents


class velseifs(list):

    def __init__(self):
        pass

    def join(self, elseif):
        self.append(elseif)
        return self

    def collect_names(self, names):
        for elseif in self:
            elseif.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        for elseif in self:
            elseif.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = []
        for elseif in self:
            contents.extend(elseif.compose(ident))
        return contents


class vifthen(vstatement):

    def __init__(self, condition, statements, elseifs=None, line=None):
        vstatement.__init__(self, line)
        self.condition = condition
        self.statements = statements
        self.elseifs = elseifs

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        self.statements.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.condition.scope_names(mysource, myclass, myprocedure)
        self.statements.scope_names(mysource, myclass, myprocedure)
        if self.elseifs:
            self.elseifs.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = [(self.line, ident, "if bool(%s):" % self.condition)]
        contents.extend(self.statements.compose(ident+1))
        if self.elseifs:
            contents.extend(self.elseifs.compose(ident))
        return contents


class vifthenelse(vifthen):

    def __init__(self, condition, statements, else_statements, elseifs=None, line=None):
        vifthen.__init__(self, condition, statements,
                         elseifs=elseifs, line=line)
        self.else_statements = else_statements

    def collect_names(self, names):
        vifthen.collect_names(self, names)
        self.else_statements.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vifthen.scope_names(self, mysource, myclass, myprocedure)
        self.else_statements.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = vifthen.compose(self, ident)
        contents.append((self.line, ident, "else:"))
        contents.extend(self.else_statements.compose(ident+1))
        return contents


class vselectcase(vstatement):

    def __init__(self, expressions, statements, line=None):
        vstatement.__init__(self, line)
        self.expressions = expressions
        self.statements = statements

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        self.statements.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.expressions.scope_names(mysource, myclass, myprocedure)
        self.statements.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident, compare, index):
        contents = []
        conditions = " or ".join(
            ["bool(%s==%s)" % (compare, expression) for expression in self.expressions])
        contents.append((self.line, ident, "%s %s:" %
                        ("elif" if index else "if", conditions)))
        contents.extend(self.statements.compose(ident+1))
        return contents


class vselectcases(list):

    def __init__(self):
        pass

    def join(self, case):
        self.append(case)
        return self

    def collect_names(self, names):
        for case in self:
            case.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        for case in self:
            case.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident, compare):
        contents = []
        for index, case in enumerate(self):
            contents.extend(case.compose(ident, compare, index))
        return contents


class vselect(vstatement):

    def __init__(self, expression, cases, line=None):
        vstatement.__init__(self, line)
        self.expression = expression
        self.cases = cases

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        self.cases.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.expression.scope_names(mysource, myclass, myprocedure)
        self.cases.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = []
        contents.extend(self.cases.compose(ident, self.expression))
        return contents


class vselectelse(vselect):

    def __init__(self, expression, cases, else_statements, line=None):
        vselect.__init__(self, expression, cases, line)
        self.else_statements = else_statements

    def collect_names(self, names):
        vselect.collect_names(self, names)
        self.else_statements.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vselect.scope_names(self, mysource, myclass, myprocedure)
        self.else_statements.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = vselect.compose(self, ident)
        contents.append((self.line, ident, "else:"))
        contents.extend(self.else_statements.compose(ident+1))
        return contents


class vdoloop(vstatement):

    def __init__(self, statements, line=None):
        vstatement.__init__(self, line)
        self.statements = statements

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        self.statements.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.statements.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident, condition=None, follow=None):
        contents = [(self.line, ident, "while %s:" %
                     (condition or "1")), (self.line, ident+1, "try:")]
        contents.extend(self.statements.compose(ident+2, follow=follow))
        contents.append((self.line, ident+1, "except exitdo:"))
        contents.append((self.line, ident+2, "break"))
        return contents


class vdoconditionalloop(vdoloop):

    def __init__(self, condition, statements, line=None):
        vdoloop.__init__(self, statements, line)
        self.condition = condition

    def scope_names(self, mysource, myclass, myprocedure):
        vdoloop.scope_names(self, mysource, myclass, myprocedure)
        self.condition.scope_names(mysource, myclass, myprocedure)


class vdowhileloop(vdoconditionalloop):

    def compose(self, ident):
        return vdoconditionalloop.compose(self, ident,
                                          condition="bool(%s)" % self.condition)


class vdountilloop(vdoconditionalloop):

    def compose(self, ident):
        return vdoconditionalloop.compose(self, ident,
                                          condition="not bool(%s)" % self.condition)


class vdoloopwhile(vdoconditionalloop):

    def compose(self, ident):
        return vdoconditionalloop.compose(self, ident,
                                          follow=[(self.condition.line, ident+2, "if not bool(%s):" % self.condition),
                                                  (self.condition.line, ident+3, "break")])


class vdoloopuntil(vdoconditionalloop):

    def compose(self, ident):
        return vdoconditionalloop.compose(self, ident,
                                          follow=[(self.condition.line, ident+2, "if bool(%s):" % self.condition),
                                                  (self.condition.line, ident+3, "break")])


class vforeach(vstatement):

    def __init__(self, variable, collection, statements, line=None):
        vstatement.__init__(self, line)
        self.variable = variable
        self.variable.check = 0
        self.collection = collection
        self.statements = statements

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.variable.scope_names(mysource, myclass, myprocedure)
        self.collection.scope_names(mysource, myclass, myprocedure)
        self.statements.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = [(self.line, ident, "for %s in %s:" % (self.variable, self.collection)),
                    (self.line, ident+1, "try:")]
        contents.extend(self.statements.compose(ident+2))
        contents.append((self.line, ident+1, "except exitfor:"))
        contents.append((self.line, ident+2, "break"))
        contents.append((self.line, ident+1, "finally:"))
        contents.append((self.line, ident+2, "%s=variant()" % self.variable))
        return contents


class vfor(vstatement):

    def __init__(self, variable, range, statements, line=None):
        vstatement.__init__(self, line)
        self.variable = variable
        self.variable.check = 0
        self.range = range
        self.statements = statements

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.variable.scope_names(mysource, myclass, myprocedure)
        self.range[0].scope_names(mysource, myclass, myprocedure)
        self.range[1].scope_names(mysource, myclass, myprocedure)
        self.statements.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident, step=None):
        contents = [(self.line, ident, "%s(let=integer(int(%s)))" % (self.variable, self.range[0])),
                    (self.line, ident, "while bool(%s<=integer(int(%s))):" %
                     (self.variable, self.range[1])),
                    (self.line, ident+1, "try:")]
        contents.extend(self.statements.compose(ident+2,
                                                follow=[(self.line, ident+2, "%s(let=%s+integer(int(%s)))" % (self.variable, self.variable, step or "1"))]))
        contents.append((self.line, ident+1, "except exitfor:"))
        contents.append((self.line, ident+2, "break"))
        return contents


class vforstep(vfor):

    def __init__(self, variable, range, step, statements, line=None):
        vfor.__init__(self, variable, range, statements, line)
        self.step = step

    def scope_names(self, mysource, myclass, myprocedure):
        vfor.scope_names(self, mysource, myclass, myprocedure)
        self.step.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        return vfor.compose(self, ident, step=self.step)


class vtrycatch(vstatement):

    def __init__(self, statements, exceptions=None, name=None, line=None):
        vstatement.__init__(self, line)
        self.exceptions = exceptions
        if self.exceptions:
            for exception in self.exceptions:
                exception.check = 0
        self.name = name
        self.statements = statements

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        self.statements.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        mysource.trys.enter(self.name)
        if self.exceptions:
            self.exceptions.scope_names(mysource, myclass, myprocedure)
        self.statements.scope_names(mysource, myclass, myprocedure)
        mysource.trys.leave()

    def compose(self, ident):
        contents = [(self.line, ident, "except%s%s:" %
                     (" (%s.exception)" % str(self.exceptions) if self.exceptions else "",
                      " as %s" % self.name if self.name else ""))]
        contents.extend(self.statements.compose(ident+1,
                                                precede=[(self.line, ident+1, "%s=error(%s)" % (self.name, self.name))] if self.name else None))
        return contents


class vtrycatches(list):

    def __init__(self):
        pass

    def join(self, value):
        self.append(value)
        return self

    def collect_names(self, names):
        for value in self:
            value.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        for value in self:
            value.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = []
        for value in self:
            contents.extend(value.compose(ident))
        return contents


class vtry(vstatement):

    def __init__(self, statements, excepts, line=None):
        vstatement.__init__(self, line)
        self.statements = statements
        self.excepts = excepts

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        self.excepts.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.statements.scope_names(mysource, myclass, myprocedure)
        self.excepts.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident, complete=1):
        contents = [(self.line, ident, "try:")]
        contents.extend(self.statements.compose(ident+1))
        if self.excepts:
            contents.extend(self.excepts.compose(ident))
        elif complete:
            contents.append((self.line, ident, "finally:"))
            contents.append((self.line, ident+1, "pass"))
        return contents


class vtryfinally(vtry):

    def __init__(self, statements, excepts, finally_statements, line=None, finally_line=None):
        vtry.__init__(self, statements, excepts, line)
        self.finally_statements = finally_statements
        self.finally_line = finally_line

    def collect_names(self, names):
        vtry.collect_names(self, names)
        self.finally_statements.collect_names(names)

    def scope_names(self, mysource, myclass, myprocedure):
        vtry.scope_names(self, mysource, myclass, myprocedure)
        self.finally_statements.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        contents = []
        contents.extend(vtry.compose(self, ident, complete=0))
        contents.append((self.finally_line, ident, "finally:"))
        contents.extend(self.finally_statements.compose(ident+1))
        return contents


class vthrow(vstatement):

    def __init__(self, name=None, line=None):
        vstatement.__init__(self, line)
        self.name = name

    def compose(self, ident):
        return [(self.line, ident, "raise %s.exception" % self.name if self.name else "raise")]


class vwith(vstatement):

    def __init__(self, name, statements, line=None):
        vstatement.__init__(self, line)
        self.name = name
        self.statements = statements

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        mysource.withs.enter(self.name)
        self.statements.scope_names(mysource, myclass, myprocedure)
        mysource.withs.leave()

    def compose(self, ident):
        contents = []
        contents.extend(self.statements.compose(ident))
        return contents


class vexitfunction(vstatement):

    def __init__(self, line=None):
        vstatement.__init__(self, line)

    def scope_names(self, mysource, myclass, myprocedure):
        if not isinstance(myprocedure, vfunction):
            raise errors.expected_function(line=self.line)
        self.myprocedure = myprocedure

    def compose(self, ident):
        return ((self.line, ident, "return %s.%s" % (python_result, python_value)),)


class vexitsub(vstatement):

    def __init__(self, line=None):
        vstatement.__init__(self, line)

    def scope_names(self, mysource, myclass, myprocedure):
        if not isinstance(myprocedure, vsub):
            raise errors.expected_sub(line=self.line)

    def compose(self, ident):
        return ((self.line, ident, "return v_mismatch"),)


class vexitproperty(vstatement):

    def __init__(self, line=None):
        vstatement.__init__(self, line)

    def scope_names(self, mysource, myclass, myprocedure):
        if not isinstance(myprocedure, (vpropertyget, vpropertyletset)):
            raise errors.expected_property(line=self.line)
        self.string = "return %s.%s" % (python_result, python_value) \
            if isinstance(myprocedure, vpropertyget) else "return v_mismatch"

    def compose(self, ident):
        return ((self.line, ident, self.string),)


class vexitdo(vstatement):

    def __init__(self, line=None):
        vstatement.__init__(self, line)

    def compose(self, ident):
        return ((self.line, ident, "raise exitdo"),)


class vexitfor(vstatement):

    def __init__(self, line=None):
        vstatement.__init__(self, line)

    def compose(self, ident):
        return ((self.line, ident, "raise exitfor"),)


class vrandomize(vstatement):

    def __init__(self, seed=None, line=None):
        vstatement.__init__(self, line)
        self.seed = seed

    def compose(self, ident):
        return ((self.line, ident, "randomize(%s)" % (self.seed or "")),)


class vprint(vstatement):

    def __init__(self, expressions, line=None):
        vstatement.__init__(self, line)
        self.expressions = expressions

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.expressions.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        string = "echo(%s)" % ", ".join(map(str, self.expressions))
        return ((self.line, ident, string),)


class vtouch(vstatement):

    def __init__(self, expressions, line=None):
        vstatement.__init__(self, line)
        self.expressions = expressions

    def scope_names(self, mysource, myclass, myprocedure):
        vstatement.scope_names(self, mysource, myclass, myprocedure)
        self.expressions.scope_names(mysource, myclass, myprocedure)

    def compose(self, ident):
        string = "print repr(%s)" % ", ".join(map(str, self.expressions))
        return ((self.line, ident, string),)


class vglobals(list):

    def __init__(self):
        pass

    initialization = property(lambda self: (
        "global %s" % ", ".join(self)) if self else "")


class vdefinename(vstatement):

    def __init__(self, name, line=None):
        vstatement.__init__(self, line)
        self.name = name

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        if self.name in names:
            raise errors.name_redefined(name=self.name, line=self.line)
        names[self.name] = None


class vprocedure(vstatement):

    def __init__(self, name, arguments, statements, default=False, line=None):
        vstatement.__init__(self, line)
        self.name = name
        self.vname = name
        self.arguments = arguments
        self.statements = statements
        self.default = default
        self.cachenames = {}
        self.statements.insert(0, vdefinename(self.name))
        self.precede = []

    def insert(self, *lines):
        for line in lines:
            if isinstance(line, (bytes, str)):
                self.precede.append((None, None, line))
            else:
                self.precede.append(line)

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        if self.default:
            if python_default in names:
                raise errors.class_have_multiple_default(line=self.line)
            names[python_default] = self
        for name, xtype in self.arguments:
            # if name in names:
            # raise errors.name_redefined(name, line=self.line)
            self.cachenames[name] = None
        self.statements.collect_names(self.cachenames)

    def scope_names(self, mysource, myclass, myprocedure):
        self.globals = vglobals()
        self.names = deepcopy(self.cachenames)
        self.statements.scope_names(mysource, myclass, self)

    def compose(self, ident, precede=None):
        contents = [(self.line, ident, "def %s(%s):" %
                     (self.vname, self.arguments))]
        for local_line, local_ident, local_string in self.precede:
            contents.append((local_line or self.line, ident + \
                            1 + (local_ident or 0), local_string))  # noqa
        initialization = [(self.line, ident + 1, self.arguments.initialization),
                          (self.line, ident + 1, self.globals.initialization)]
        if precede:
            initialization.extend(precede)
        dims = [(name, value)
                for name, value in self.names.items() if isinstance(value, str)]
        initialization.extend(
            [(self.line, ident + 1, "=".join([_f for _f in [", ".join([name for name, value in dims]),
                                                             ", ".join([value for name, value in dims])] if _f]))])
        contents.extend(self.statements.compose(
            ident + 1, precede=initialization))
        return contents


class vfunction(vprocedure):

    def __init__(self, name, arguments, statements, default=False, line=None):
        vprocedure.__init__(self, name, arguments, statements, default, line)
        self.statements.append(vexitfunction(line=self.line))

    def collect_names(self, names):
        vprocedure.collect_names(self, names)
        if self.name in names:
            raise errors.name_redefined(self.name, line=self.line)
        names[self.name] = self

    def compose(self, ident):
        return vprocedure.compose(self, ident,
                                  precede=[(self.line, ident+1, "%s=variant()" % python_result)])


class vsub(vprocedure):

    def __init__(self, name, arguments, statements, default=False, line=None):
        vprocedure.__init__(self, name, arguments, statements, default, line)

    def collect_names(self, names):
        vprocedure.collect_names(self, names)
        if self.name in names:
            raise errors.name_redefined(self.name, line=self.line)
        names[self.name] = self

    def compose(self, ident):
        return vprocedure.compose(self, ident,
                                  precede=[
                                      (self.line, ident+1, "%s=constant()" % python_result)]
                                  if self.name not in (python_constructor, python_destructor) else None)


class vproperty(vstatement):

    def __init__(self, name, get=None, let=None, set=None, line=None):
        vstatement.__init__(self, line)
        self.name = name
        self.get = get
        self.let = let
        self.set = set

    def compose(self, ident):
        arguments = [len(self.get.arguments)+1] if self.get else []
        if self.let:
            arguments.append(len(self.let.arguments))
        if self.set:
            arguments.append(len(self.set.arguments))
        if len(arguments) > 1 and sum(arguments) / 3 != arguments[0]:
            raise errors.inconsistent_arguments_number(line=self.line)
        return [(self.line, ident, "def %s(self, *arguments, **keywords):" % self.name),
                (self.line, ident+1, "if \"let\" in keywords:"),
                (self.line, ident+2,
                 "return self.%s_let(let=keywords[\"let\"], *arguments)" % self.name),
                (self.line, ident+1, "elif \"set\" in keywords:"),
                (self.line, ident+2,
                 "return self.%s_set(set=keywords[\"set\"], *arguments)" % self.name),
                (self.line, ident+1, "else:"),
                (self.line, ident+2, "return self.%s_get(*arguments)" % self.name)]


class vpropertyget(vprocedure):

    def __init__(self, name, arguments, statements, default=False, line=None):
        vprocedure.__init__(self, name, arguments, statements, default, line)
        self.vname = "%s_get" % self.name
        self.statements.append(vexitproperty(line=self.line))

    def collect_names(self, names):
        vprocedure.collect_names(self, names)
        name = names.get(self.name, absent)
        if name is absent:
            names[self.name] = vproperty(self.name, get=self)
        else:
            if not isinstance(name, vproperty) or name.get:
                raise errors.name_redefined(self.name, line=self.line)
            name.get = self

    def compose(self, ident):
        return vprocedure.compose(self, ident,
                                  precede=[(self.line, ident+1, "%s=variant()" % python_result)])


class vpropertyletset(vprocedure):

    def __init__(self, name, arguments, statements, default=False, line=None):
        vprocedure.__init__(self, name, arguments, statements, default, line)
        if len(self.arguments) < 1:
            raise errors.property_have_no_arguments(line=self.line)
        self.value = self.arguments.pop()
        self.statements.insert(0, vdefinename(self.value[0]))


class vpropertylet(vpropertyletset):

    def __init__(self, name, arguments, statements, default=False, line=None):
        vpropertyletset.__init__(
            self, name, arguments, statements, default, line)
        self.vname = "%s_let" % self.name
        self.arguments.join(("let", None))

    def collect_names(self, names):
        vprocedure.collect_names(self, names)
        name = names.get(self.name, absent)
        if name is absent:
            names[self.name] = vproperty(self.name, let=self)
        else:
            if not isinstance(name, vproperty) or name.let:
                raise errors.name_redefined(self.name, line=self.line)
            name.let = self

    def compose(self, ident):
        return vprocedure.compose(self, ident,
                                  precede=[(self.line, ident+1, "%s=variant()" % python_result),
                                           (self.line, ident+1, "%s=let.%s" % (self.value[0], self.value[1]))])


class vpropertyset(vpropertyletset):

    def __init__(self, name, arguments, statements, default=False, line=None):
        vpropertyletset.__init__(
            self, name, arguments, statements, default, line)
        self.vname = "%s_set" % self.name
        self.arguments.join(("set", None))

    def collect_names(self, names):
        vprocedure.collect_names(self, names)
        name = names.get(self.name, absent)
        if name is absent:
            names[self.name] = vproperty(self.name, set=self)
        else:
            if not isinstance(name, vproperty) or name.set:
                raise errors.name_redefined(self.name, line=self.line)
            name.set = self

    def compose(self, ident):
        return vprocedure.compose(self, ident,
                                  precede=[(self.line, ident+1, "%s=variant()" % python_result),
                                           (self.line, ident+1, "%s=set.%s" % (self.value[0], self.value[1]))])


class vinitializations(vstatement):

    def __init__(self, owner, line=None):
        vstatement.__init__(self, line=line)
        self.owner = owner

    def compose(self, ident):
        return [(self.line, ident, "self.%s=%s" % (name, value)) for name, value in self.owner.initializations]


class vinherits(vstatement):

    def __init__(self, name, line=None):
        vstatement.__init__(self, line=line)
        self.name = name
        self.parent = None

    def scope_names(self, mysource, myclass, myprocedure):
        if myclass is None:
            raise error.object_required(name="inherits", line=self.line)
        if myclass.inherits is not None:
            raise error.multiple_inherits(line=self.line)
        myclass.inherits = self.name
        myclass.parent = mysource.names[self.name]


class vclass(vstatement):

    def __init__(self, name, statements, line=None):
        vstatement.__init__(self, line)
        self.name = name
        self.statements = statements
        self.inherits = None
        self.native = None
        self.parent = None

    def collect_names(self, names):
        vstatement.collect_names(self, names)
        if self.name in names:
            raise errors.name_redefined(self.name, line=self.line)
        names[self.name] = self
        self.names = {}
        self.statements.collect_names(self.names)
        self.default = self.names.get(python_default, None)
        self.constructor = self.names.get(vscript_constructor, None)
        self.destructor = self.names.get(vscript_destructor, None)
        for value in self.names.values():
            if isinstance(value, vproperty):
                self.statements.append(value)
        if self.default:
            self.statements.insert(0, vsub(python_default, deepcopy(self.default.arguments),
                                           vstatements().join(vcall(vexpression("return self.%s(%s)" % (self.default.name,
                                                                                self.default.arguments), line=self.line), line=self.line)), line=self.line))
        if self.destructor:
            if not isinstance(self.destructor, vsub):
                raise errors.expected_sub()
            if self.destructor.arguments:
                raise errors.constructor_or_destructor_have_arguments
            self.statements.insert(0, vsub(python_destructor, deepcopy(self.destructor.arguments),
                                           vstatements().join(vcall(vexpression("self.%s()" % vscript_destructor, line=self.line),
                                                                    line=self.line)), line=self.line))
        self.initializations = [
            (name, value) for name, value in self.names.items() if isinstance(value, str)]
        if self.constructor or self.initializations:
            statements = vstatements()
            if self.initializations:
                statements.join(vinitializations(self, line=self.line))
            if self.constructor:
                if not isinstance(self.constructor, vsub):
                    raise errors.expected_sub("Sub")
                if self.constructor.arguments:
                    raise errors.constructor_or_destructor_have_arguments
                arguments = deepcopy(self.constructor.arguments)
                statements.join(vcall(vexpression(
                    "self.%s()" % vscript_constructor, line=self.line), line=self.line))
            else:
                arguments = varguments()
            self.native = vsub(python_constructor, arguments,
                               statements, line=self.line)
            self.statements.insert(0, self.native)
        for procedure in [statement for statement in self.statements if isinstance(statement, vprocedure)]:
            procedure.arguments.insert(0, ("self", None))

    def check_name_deeply(self, name):
        if name in self.names:
            return True
        if self.inherits:
            return self.parent.check_name_deeply(name)
        return False

    def scope_names(self, mysource, myclass, myprocedure):
        self.statements.scope_names(mysource, self, myprocedure)
        if self.inherits and self.native:
            self.native.insert("super(%s, self).__init__()" % self.name)

    def compose(self, ident):
        contents = [(self.line, ident, "class %s(%s):" %
                     (self.name, self.inherits or "generic"))]
        contents.extend(self.statements.compose(ident+1))
        return contents


class vnamestack(list):

    def enter(self, name):
        self.append(name)

    def leave(self):
        self.pop()


class vsourcenames:

    def __init__(self, environment):
        self.internal = register.names
        self.environment = environment
        self.names = {}
        self.imports = {}

    def update(self, names):
        self.names.update(names)

    def __iter__(self):
        return iter(self.names)

    def __getitem__(self, name):
        return self.names[name]

    def __setitem__(self, name, value):
        self.names[name] = value

    def __contains__(self, name):
        alias = self.internal.get(name, KeyError)
        if alias is KeyError:
            alias = self.environment.get(name, KeyError)
            if alias is KeyError:
                return name in self.names
        if isinstance(alias, (bytes, str)):
            try:
                names = self.imports[alias]
            except KeyError:
                names = self.imports[alias] = set()
            names.add(name)
        return True

    def compose(self, ident):
        contents = [(None, ident, "from vscript.%s import %s" % (name, ", ".join(names)))
                    for name, names in self.imports.items() if name is not None]
        contents.extend((None, ident, "globals().setdefault(%s, %s)" % (repr(name), value))
                        for name, value in self.names.items() if isinstance(value, str))
        return contents


class vsource:

    def __init__(self, statements, package=None, environment=None):
        self.line = 0
        self.names = vsourcenames(environment)
        self.statements = statements
        self.package = package
        self.collect_names()

    def collect_names(self):
        self.statements.collect_names(self.names)

    def scope_names(self):
        self.uses = []
        self.using = {}
        try:
            self.trys = vnamestack()
            self.withs = vnamestack()
            self.statements.scope_names(self, None, None)
        finally:
            self.trys = None
            self.withs = None

    def compose(self, ident):
        self.scope_names()
        contents = [(None, ident, "from vscript import *")]
        if self.package:
            contents.insert(0, (None, 0, "__package__=\"%s\"" % self.package))
        contents.extend(self.statements.compose(
            ident=0, precede=self.names.compose(ident)))
        return contents
