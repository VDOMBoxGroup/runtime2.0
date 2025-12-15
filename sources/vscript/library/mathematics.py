
import math
from random import random, seed
from .. import errors
from ..subtypes import integer, double


last_random = random()


def v_abs(number):
    return abs(number)


def v_sgn(number):
    number = number.as_number
    return integer(-1 if number < 0 else 1 if number > 0 else 0)


def v_round(number, digits=None):
    number = number.as_number
    return integer(number) if isinstance(number, int) \
        else double(round(number) if digits is None else round(number, digits.as_integer))


def v_exp(number):
    number = number.as_double
    if number > 709.782712893:  # Highest acceptable value from MSDN
        raise errors.invalid_procedure_call(name=u"exp")
    return double(math.exp(number))


def v_int(number):
    number = number.as_number
    return integer(number) if isinstance(number, int) else double(math.floor(number))


def v_fix(number):
    number = number.as_number
    return integer(number) if isinstance(number, int) else double(math.modf(number)[1])


def v_log(number):
    number = number.as_double
    if number <= 0:
        raise errors.invalid_procedure_call(name=u"log")
    return double(math.log(number))


def v_sqr(number):
    number = number.as_double
    if number < 0:
        raise errors.invalid_procedure_call(name=u"sqr")
    return double(math.sqrt(number))


def v_atn(number):
    return double(math.atan(number.as_double))


def v_cos(number):
    return double(math.cos(number.as_double))


def v_sin(number):
    return double(math.sin(number.as_double))


def v_tan(number):
    return double(math.tan(number.as_double))


def v_rnd(number=None):
    global last_random
    number = 1 if number is None else number.as_double
    if number < 0:
        seed(number)
        value = random()
        last_random = value
    elif number > 0:
        value = random()
        last_random = value
    else:
        value = last_random
    return double(value)
