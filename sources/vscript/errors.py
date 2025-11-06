
from builtins import str
python = Exception
python_using_abstract = NotImplementedError
python_avoid_using = RuntimeError


class generic(python):

    compilation = u"compilation"
    runtime = u"runtime"

    number = 1

    source = runtime
    library = None
    line = None
    near = None

    # vscript traceback source lines
    traceback = None

    # internal error report and original exception
    report = None
    cause = None

    def __init__(self, message=u"Unknown error", details=None, line=None):
        self.message = message
        self.line = line

    def __str__(self):
        return str(self).encode("ascii", errors="replace")

    def __unicode__(self):
        if self.near:
            if isinstance(self.near, tuple):
                character = "near \"%s\"" % self.near[1]
                column = "column %d" % self.near[0]
            else:
                character = None
                column = "near column %d" % self.near
        else:
            character = None
            column = None
        details = ", ".join(
            [_f for _f in (
                None if self.library is None else "library \"%s\"" % self.library,
                None if self.line is None else "line %s" % self.line,
                character,
                column) if _f])
        return u"VScript %s error%s: %s" % (
            self.source,
            (u" (%s)" % details if details else u""),
            self.message)


class internal_error(generic):

    number = 51

    def __init__(self, message=None, replace=None, cause=None, report=None, line=None):
        generic.__init__(self,
                message=replace or u"Internal error%s" % (": %s" % message if message else ""),
                line=line)
        if report:
            self.report = report
        if cause:
            self.cause = cause


class lock_error(internal_error):

    def __init__(self, line=None):
        internal_error.__init__(self,
                message="Lock error",
                line=line)


class object_variable_not_set(generic):

    number = 91

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Object variable not set",
                line=line)


class system_error(generic):

    number = 507

    def __init__(self, message, line=None):
        generic.__init__(self,
                message=u"System error: %s" % message,
                line=line)


class invalid_character(generic):

    number = 1032

    def __init__(self, character, line=None):
        generic.__init__(self,
                message=u"Invalid character '%s'" % character,
                line=line)


class syntax_error(generic):

    number = 1002

    def __init__(self, token, line=None):
        generic.__init__(self,
                message=u"Invalid token '%s'" % token,
                line=line)


class unknown_syntax_error(generic):

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Invalid token",
                line=line)


class expected_statement(generic):

    number = 1024

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Expected statement",
                line=line)


class class_have_multiple_default(generic):

    number = 1052

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Cannot have multiple default property/method in a Class",
                line=line)


class property_have_no_arguments(generic):

    number = 1054

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Property set or let must have at least one argument",
                line=line)


class use_parentheses_when_calling_sub(generic):

    number = 1044

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Cannot use parentheses when calling a Sub",
                line=line)


class constructor_or_destructor_have_arguments(generic):

    number = 1053

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Class initialize or terminate do not have arguments",
                line=line)


class default_not_a_property_get(generic):

    number = 1057

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"'Default' specification can only be on Property Get",
                line=line)


class default_not_a_public(generic):

    number = 1058

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"'Default' specification must also specify 'Public'",
                line=line)


class expected_function(generic):

    number = 1015

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Expected 'Function'",
                line=line)


class expected_sub(generic):

    number = 1016

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Expected 'Sub'",
                line=line)


class expected_property(generic):

    number = 1050

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Expected 'Property'",
                line=line)


class inconsistent_arguments_number(generic):

    number = 1051

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Number of arguments must be consistent across properties specification",
                line=line)


class invalid_exit_statement(generic):

    number = 1039

    def __init__(self, line=None):
        generic.__init__(self,
                message="Invalid 'Exit' statement",
                line=line)


class not_implemented(internal_error):

    def __init__(self, line=None):
        internal_error.__init__(self,
                "This feature is not implemented",
                line=line)


class variable_is_undefined(generic):

    number = 500

    def __init__(self, name=None, line=None):
        details = u": '%s'" % (name[2:] if name.startswith(u"v_") else name) if name else u""
        generic.__init__(self,
                message=u"Variable is undefined%s" % details,
                line=line)


class name_redefined(generic):

    number = 1041

    def __init__(self, name=None, line=None):
        details = u": '%s'" % (name[2:] if name.startswith(u"v_") else name) if name else u""
        generic.__init__(self,
                message=u"Name redefined%s" % details,
                line=line)


class division_by_zero(generic):

    number = 11

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Division by zero",
                line=line)


class overflow(generic):

    number = 6

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Overflow",
                line=line)


class object_has_no_property(generic):

    number = 438

    def __init__(self, name=None, line=None):
        details = u": '%s'" % (name[2:] if name.startswith(u"v_") else name) if name else u""
        generic.__init__(self,
                message=u"Object doesn't support this property or method%s" % details,
                line=line)


class subscript_out_of_range(generic):

    number = 9

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Subscript out of range",
                line=line)


class type_mismatch(generic):

    number = 13

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Type mismatch",
                line=line)


class object_required(generic):

    number = 424

    def __init__(self, name=None, line=None):
        details = u": '%s'" % (name[2:] if name.startswith(u"v_") else name) if name and name != "__call__" else u""
        generic.__init__(self,
                message=u"Object required%s" % details,
                line=line)


class static_array(generic):

    number = 10

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"This array is fixed or temporarily locked",
                line=line)


class illegal_assigment(generic):

    number = 501

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Illegal assignment",
                line=line)


class wrong_number_of_arguments(generic):

    number = 450

    def __init__(self, name=None, line=None):
        details = u": '%s'" % (name[2:] if name.startswith(u"v_") else name) if name and name != "__call__" else u""
        generic.__init__(self,
                message=u"Wrong number of arguments or invalid assignment%s" % details,
                line=line)


class invalid_procedure_call(generic):

    number = 5

    def __init__(self, name=None, line=None):
        details = u": '%s'" % (name[2:] if name.startswith(u"v_") else name) if name else u""
        generic.__init__(self,
                message=u"Invalid procedure call or argument%s" % details,
                line=line)


class multiple_inherits(syntax_error):

    number = 40001

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"'Inherits' can appear only once within a 'Class' statement and can only specify one class",
                line=line)


class element_not_found(generic):

    number = 32811

    def __init__(self, line=None):
        generic.__init__(self,
                message=u"Element not found",
                line=line)
