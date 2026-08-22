
from .subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing, \
    v_true_value, v_false_value, ordereddictionary # noqa
from .variables import variant, constant, permanent, shadow # noqa
from .essentials import check, randomize, echo, concat, exitloop, exitdo, exitfor, vand, vor, vcoalesce, vget, vitems, venum_build, vfuncref, vcall0 # noqa
from .conversions import as_is, as_value, as_specific, as_array, as_binary, \
    as_boolean, as_date, as_double, as_generic, as_integer, as_string, pack, unpack # noqa
from .decorators import auto, native, vclass, vfunction, vsub, vproperty, vcollection # noqa
from .exceptions import v_genericerror, v_servererror, v_scripterror, \
    v_notimplementederror, v_variableisundefinederror, v_nameredefinederror, \
    v_divisionbyzero, v_overflow, v_objecthasnopropertyerror, v_subscriptoutofrange, \
    v_typemismatcherror, v_objectrequirederror, v_illegalassigmenterror, \
    v_wrongnumberofargumentserror, v_invalidprocedurecallerror # noqa
from .library import *  # noqa


# Issue Ignore List

# Pass argument as value when enclosed in parentheses
#
# A ByRef parameter is passed by value if the argument is enclosed in parentheses
# and the parentheses do not apply to the argument list. The parentheses apply to the
# argument list if one of the following is true:
# * The statement is a function call that has an assignment to the returned value.
# * The statement uses the Call keyword. (The Call keyword can optionally be used
# for a subroutine call, or for a function call without an assignment.)
#
# Sub MySub(Argument1, ByRef Argument2, Argument3)
# Argument2=321
# End Sub
# MyVariable=123
# MySub 1, (MyVariable), 3
# Print MyVariable
#
# Link: http://msdn.microsoft.com/en-us/library/ie/ee478101%28v=vs.84%29.aspx

# Private statement
#
# Declares private variables in a class. Private statement variables are
# available only to the script in which they are declared.
#
# Class Sample
# Private MyNumber, MyArray(9)
# End Class
#
# Link: http://msdn.microsoft.com/en-us/library/9h9bf56c%28v=vs.85%29.aspx

# Public statement
#
# Declares public variables in a class. Public statement variables are available
# to all procedures in all scripts.
#
# Class MyClass
# Public MyNumber, MyArray(9)
# End Class
#
# Link: http://msdn.microsoft.com/en-us/library/9h9bf56c%28v=vs.85%29.aspx

# Private Functions, Subs and Properties

# Indicates that the function, procedure or property is accessible only to other
# procedures in the script where it is declared.
#
# Class Sample
# Private Function MyFunction
# End Function
# End Class
#
# Link: http://msdn.microsoft.com/en-us/library/x7hbf8fa%28v=vs.85%29.aspx
# Link: http://msdn.microsoft.com/en-us/library/tt223ahx%28v=vs.85%29.aspx
# Link: http://msdn.microsoft.com/en-us/library/613k2d48%28v=vs.85%29.aspx

# Err Object
#
# Contains information about run-time errors. Accepts the Raise and Clear methods
# for generating and clearing run-time errors. The default property of the Err
# object is Number.
#
# Err.Raise 6
#
# Reason: VScript support exceptions.
# Link: http://msdn.microsoft.com/en-us/library/sbf5ze0e%28v=vs.85%29.aspx

# On Error Statement

# Enables or disables error-handling. If you don't use an On Error Resume Next
# statement anywhere in your code, any run-time error that occurs can cause an error
# message to be displayed and code execution stopped. However, the host running the
# code determines the exact behavior.
#
# On Error Resume Next
# Err.Raise 6
# MsgBox "Error # " & CStr(Err.Number) & " " & Err.Description
# Err.Clear
#
# Reason: VScript support exceptions.
# Link: http://msdn.microsoft.com/en-us/library/53f3k80h%28v=vs.85%29.aspx

# Eval Function
#
# Evaluates an expression and returns the result.
#
# Eval "1+2"
#
# Reason: Security reasons.
# Link: http://msdn.microsoft.com/en-us/library/0z5x4094%28v=vs.85%29.aspx

# Execute Statement
#
# Executes one or more specified statements.
#
# Execute "Print 1+2"
#
# Reason: Security reasons.
# Link: http://msdn.microsoft.com/en-us/library/03t418d2%28v=vs.85%29.aspx

# FormatCurrency Function
#
# Returns an expression formatted as a currency value using the currency symbol defined
# in the system control panel.
#
# FormatCurrency(number, -1, vbUseDefault, vbFalse)
#
# Link: http://msdn.microsoft.com/en-us/library/k6skb64t%28v=vs.85%29.aspx

# FormatDateTime Function
#
# Returns an expression formatted as a date or time.
#
# GetCurrentDate=FormatDateTime(Date, 1)
#
# Link: http://msdn.microsoft.com/en-us/library/8aebkz6s%28v=vs.85%29.aspx

# FormatNumber Function
#
# Returns an expression formatted as a number.
#
# FormatNumber (number, 3, , vbTrue)
#
# Link: http://msdn.microsoft.com/en-us/library/ws343esk%28v=vs.85%29.aspx

# FormatPercent Function
#
# Returns an expression formatted as a percentage (multiplied by 100) with a
# trailing % character.
#
# MyPercent = FormatPercent(2/32)
#
# Link: http://msdn.microsoft.com/en-us/library/h943xb4h%28v=vs.85%29.aspx

# InputBox Function
#
# Displays a prompt in a dialog box, waits for the user to input text or click a button,
# and returns the contents of the text box.
#
# Input=InputBox("Enter your name")
#
# Reason: Non interactive environment
# Link: http://msdn.microsoft.com/en-us/library/3yfdhzk5%28v=vs.85%29.aspx

# LoadPicture Function
#
# Returns a picture object. Available only on 32-bit platforms.
#
# LoadPicture("picture.bmp")
#
# Link: http://msdn.microsoft.com/en-us/library/66bd1sx9%28v=vs.85%29.aspx

# MsgBox Function
#
# Displays a message in a dialog box, waits for the user to click a button, and returns
# a value indicating which button the user clicked.
#
# MsgBox "Hello!", vbInformation
#
# Reason: Non interactive environment
# Link: http://msdn.microsoft.com/en-us/library/sfw6660x%28v=vs.85%29.aspx

# CreateObject Function
#
# Creates and returns a reference to an Automation object.
#
# Set ExcelSheet=CreateObject("Excel.Sheet")
#
# Reason: Absence of the Automation objects
# Link: http://msdn.microsoft.com/en-us/library/dcw63t7z%28v=vs.85%29.aspx

# GetObject Function
#
# Returns a reference to an Automation object from a file.
#
# Set CADObject=GetObject("C:\CAD\SCHEMA.CAD")
#
# Reason: Absence of the Automation objects
# Link: http://msdn.microsoft.com/en-us/library/kdccchxa%28v=vs.85%29.aspx

# Option Explicit Statement
#
# Forces explicit declaration of all variables in a script.
#
# Option Explicit
#
# Link: http://msdn.microsoft.com/en-us/library/bw9t3484%28v=vs.85%29.aspx

# Date #0:0:0#
#
# Date #0:0:0# should be recognized as date(0)
#
# Print #0:0:0#*1 ' 0

# Rounding errors
#
# VBScript rounds 0.5 to 0 (correct 1), 1.5 to 2, 2.5 to 2 (correct 3) and so on.
#
# Print Round(0.5) ' 0
# Print Round(1.5) ' 2

# Comparison issues
#
# When compare variable with constant strings are parsed to be a number nor when
# compare variable with variable.
#
# X=123
# Y="123"
# Print 123="123" ' True
# Print X="123" ' True
# Print Y=123 ' True
# Print X=Y ' False

# Miss optional arguments
#
# Call function or sub with optional argumenth without specifiyng value
#
# FormatNumber (123.567, 3, , , vbFalse)
