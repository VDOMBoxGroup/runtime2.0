from ..subtypes import string
from utils.csrf import verify_csrf_token, csrf_token_arg_name

v_csrf_token_arg_name = string(csrf_token_arg_name)


def v_verify_csrf_token(token=''):
    return verify_csrf_token(token)
