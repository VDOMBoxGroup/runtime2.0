"""BlueDynamic for VScript: scripting/packages/bluedynamic.py, with JSON.

    reponse = BlueDynamic_Declarer(manifeste [, cle_declaration [, proadmin]])
    charge = BlueDynamic_Ticket()          ' "" out of a BlueMail session
    jeton = BlueDynamic_Rendre(mail)
    reponse = BlueDynamic_Evenement(charge)   ' an event of a service (§9.4)
    charge = BlueDynamic_Verifier(jeton, typ) ' "" unless ProAdmin signed it for us (§9.6)

The manifest and the mail are a JSON string or a Dictionary; the answers are
JSON strings.
"""
import json
from importlib import import_module

from .. import errors
from ..subtypes import string
from .util import unwrapp


def _package():
    return import_module("scripting.packages.bluedynamic")


def _value(argument):
    value = unwrapp(argument)
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            raise errors.invalid_procedure_call(name="bluedynamic")
    return value


def _text(argument):
    if argument is None:
        return None
    value = unwrapp(argument)
    return value or None


def v_bluedynamic_declarer(manifeste, cle_declaration=None, proadmin=None):
    answer = _package().declarer(_value(manifeste), _text(cle_declaration), _text(proadmin))
    return string(json.dumps(answer, ensure_ascii=False))


def v_bluedynamic_ticket():
    claims = _package().ticket()
    return string(json.dumps(claims, ensure_ascii=False) if claims else "")


def v_bluedynamic_evenement(charge):
    answer = _package().evenement(_value(charge))
    return string(json.dumps(answer, ensure_ascii=False))


def v_bluedynamic_verifier(jeton, typ):
    claims = _package().verifier(_text(jeton) or "", _text(typ) or "")
    return string(json.dumps(claims, ensure_ascii=False) if claims else "")


def v_bluedynamic_rendre(mail):
    from utils.bluedynamic import BlueDynamicError
    try:
        return string(_package().rendre_mail(_value(mail)))
    except BlueDynamicError as error:
        raise errors.invalid_procedure_call(name="bluedynamic_rendre (%s)" % error)
