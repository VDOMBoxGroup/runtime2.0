from __future__ import absolute_import
from Crypto import Random
from Crypto.Hash import SHA256

import managers
from .exception import VDOM_exception


csrf_secret_sess_var_name = 'VDOM_csrf_secret' # name of the session variable storing the csrf key
csrf_token_arg_name = 'vdomcsrftoken' # name of the POST argument passing the csrf token
csrf_secret_len = 32
csrf_salt_len = 16
digest_size = SHA256.digest_size


class VDOM_csrf_exception(VDOM_exception):
	pass


def gen_csrf_secret():
	"""Generate random bytes to use as csrf secret"""
	return Random.new().read(csrf_secret_len)


def get_csrf_secret():
	"""Read csrf secret from session if it exists; otherwise generate
	it and store in session"""
	sess = managers.request_manager.get_request().session()
	secret = sess.get(csrf_secret_sess_var_name, None)
	if not secret:
		secret = gen_csrf_secret()
		sess[csrf_secret_sess_var_name] = secret
	return secret


def create_csrf_token(salt=''):
	"""Generate csrf token based on existing/new csrf secret and
	provided/new salt"""
	if not salt:
		salt = Random.new().read(csrf_salt_len).encode('hex')
	h = SHA256.new()
	h.update(get_csrf_secret() + salt)
	return h.hexdigest() + salt


def verify_csrf_token(token=''):
	"""Verify csrf token against csrf secret from the session; if token is
	not provided it's read from request arguments"""
	if not token:
		token = managers.request_manager.get_request().arguments().arguments().get(csrf_token_arg_name, "")
		if token:
			token = token[0]
	if len(token) != 2 * digest_size + 2 * csrf_salt_len:
		debug('Incorrect csrf token length')
		raise VDOM_csrf_exception()
	salt = token[2*digest_size:]
	if token != create_csrf_token(salt):
		debug('Incorrect csrf token value')
		raise VDOM_csrf_exception()
