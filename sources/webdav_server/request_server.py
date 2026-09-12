"""Surcharge de RequestServer, **non cablee**.

wsgidav 4 instancie son propre RequestServer depuis RequestResolver, le dernier
element de la pile d'intergiciels ; ce module n'est importe que par __init__ et
sa classe n'est utilisee nulle part. Ses noms d'API ont ete portes vers wsgidav
4 pour qu'il ne soit pas un piege si quelqu'un le rebranche, mais **rien ici
n'est exerce** : ne pas le rebrancher sans le tester.
"""


import wsgidav.request_server
from wsgidav.request_server import RequestServer, util, HTTP_NOT_FOUND, HTTP_BAD_REQUEST, HTTP_BAD_GATEWAY, HTTP_FORBIDDEN, HTTP_CONFLICT, \
    HTTP_CREATED, HTTP_NO_CONTENT, HTTP_PRECONDITION_FAILED, as_DAVError
import urllib.request
import urllib.parse
import urllib.error
from urllib.parse import urlparse
_logger = wsgidav.request_server._logger


class VDOM_webdav_request_server(RequestServer):

    def _copyOrMove(self, environ, start_response, isMove):
        """
        @see: http://www.webdav.org/specs/rfc4918.html#METHOD_COPY
        @see: http://www.webdav.org/specs/rfc4918.html#METHOD_MOVE
        """
        srcPath = environ["PATH_INFO"]
        provider = self._davProvider
        srcRes = provider.get_resource_inst(srcPath, environ)
        srcParentRes = provider.get_resource_inst(
            util.get_uri_parent(srcPath), environ)

        # --- Check source -----------------------------------------------------

        if srcRes is None:
            self._fail(HTTP_NOT_FOUND)
        if "HTTP_DESTINATION" not in environ:
            self._fail(HTTP_BAD_REQUEST,
                       "Missing required Destination header.")
        if not environ.setdefault("HTTP_OVERWRITE", "T") in ("T", "F"):
            # Overwrite defaults to 'T'
            self._fail(HTTP_BAD_REQUEST, "Invalid Overwrite header.")
        if util.get_content_length(environ) != 0:
            # RFC 2518 defined support for <propertybehavior>.
            # This was dropped with RFC 4918.
            # Still clients may send it (e.g. DAVExplorer 0.9.1 File-Copy) sends
            # <A:propertybehavior xmlns:A="DAV:"> <A:keepalive>*</A:keepalive>
            body = environ["wsgi.input"].read(util.get_content_length(environ))
            environ["wsgidav.all_input_read"] = 1
            _logger.info("Ignored copy/move  body: '%s'..." % body[:50])

        if srcRes.isCollection:
            # The COPY method on a collection without a Depth header MUST act as
            # if a Depth header with value "infinity" was included.
            # A client may submit a Depth header on a COPY on a collection with
            # a value of "0" or "infinity".
            environ.setdefault("HTTP_DEPTH", "infinity")
            if not environ["HTTP_DEPTH"] in ("0", "infinity"):
                self._fail(HTTP_BAD_REQUEST, "Invalid Depth header.")
            if isMove and environ["HTTP_DEPTH"] != "infinity":
                self._fail(
                    HTTP_BAD_REQUEST, "Depth header for MOVE collection must be 'infinity'.")
        else:
            # It's an existing non-collection: assume Depth 0
            # Note: litmus 'copymove: 3 (copy_simple)' sends 'infinity' for a
            # non-collection resource, so we accept that too
            environ.setdefault("HTTP_DEPTH", "0")
            if not environ["HTTP_DEPTH"] in ("0", "infinity"):
                self._fail(HTTP_BAD_REQUEST, "Invalid Depth header.")
            environ["HTTP_DEPTH"] = "0"

        # --- Get destination path and check for cross-realm access ------------

        # Destination header may be quoted (e.g. DAV Explorer sends unquoted,
        # Windows quoted)
        destinationHeader = urllib.parse.unquote(environ["HTTP_DESTINATION"])

        # Return fragments as part of <path>
        # Fixes litmus -> running `basic': 9. delete_fragment....... WARNING: DELETE removed collection resource withRequest-URI including fragment; unsafe
        destHeaderTuple = urlparse(destinationHeader, allow_fragments=False)
        destScheme, destNetloc, destPath, \
            _destParams, _destQuery, _destFrag = destHeaderTuple

        http_host = destHeaderTuple.hostname
        if srcRes.isCollection:
            destPath = destPath.rstrip("/") + "/"

        if destScheme and not destScheme.lower().startswith(environ["wsgi.url_scheme"].lower()):
            self._fail(HTTP_BAD_GATEWAY,
                       "Source and destination must have the same scheme.")
        elif destNetloc and http_host.lower() != environ["HTTP_HOST"].lower():
            # TODO: this should consider environ["SERVER_PORT"] also
            self._fail(HTTP_BAD_GATEWAY,
                       "Source and destination must have the same host name.")
        elif not destPath.startswith(provider.mountPath + provider.sharePath):
            # Inter-realm copying not supported, since its not possible to
            # authentication-wise
            self._fail(HTTP_BAD_GATEWAY,
                       "Inter-realm copy/move is not supported.")

        destPath = destPath[len(provider.mountPath + provider.sharePath):]
        assert destPath.startswith("/")

        # destPath is now relative to current mount/share starting with '/'

        destRes = provider.get_resource_inst(destPath, environ)
        destExists = destRes is not None

        destParentRes = provider.get_resource_inst(
            util.get_uri_parent(destPath), environ)

        if not destParentRes or not destParentRes.isCollection:
            self._fail(HTTP_CONFLICT,
                       "Destination parent must be a collection.")

        self._evaluateIfHeaders(srcRes, environ)
        self._evaluateIfHeaders(destRes, environ)
        # Check permissions
        # http://www.webdav.org/specs/rfc4918.html#rfc.section.7.4
        if isMove:
            self._checkWritePermission(srcRes, "infinity", environ)
            # Cannot remove members from locked-0 collections
            if srcParentRes:
                self._checkWritePermission(srcParentRes, "0", environ)

        # Cannot create or new members in locked-0 collections
        if not destExists:
            self._checkWritePermission(destParentRes, "0", environ)
        # If target exists, it must not be locked
        self._checkWritePermission(destRes, "infinity", environ)

        if srcPath == destPath:
            self._fail(HTTP_FORBIDDEN, "Cannot copy/move source onto itself")
        elif util.is_equal_or_child_uri(srcPath, destPath):
            self._fail(HTTP_FORBIDDEN, "Cannot copy/move source below itself")

        if destExists and environ["HTTP_OVERWRITE"] != "T":
            self._fail(HTTP_PRECONDITION_FAILED,
                       "Destination already exists and Overwrite is set to false")

        # --- Let provider handle the request natively -------------------------

        # Errors in copy/move; [ (<ref-url>, <DAVError>), ... ]
        errorList = []
        successCode = HTTP_CREATED
        if destExists:
            successCode = HTTP_NO_CONTENT

        try:
            if isMove:
                handled = srcRes.handleMove(destPath)
            else:
                isInfinity = environ["HTTP_DEPTH"] == "infinity"
                handled = srcRes.handleCopy(destPath, isInfinity)
            assert handled in (True, False) or type(handled) is list
            if type(handled) is list:
                errorList = handled
                handled = True
        except Exception as e:
            errorList = [(srcRes.getHref(), as_DAVError(e))]
            handled = True
        if handled:
            return self._sendResponse(environ, start_response,
                                      srcRes, successCode, errorList)

        # --- Cleanup destination before copy/move -----------------------------

        srcList = srcRes.getDescendants(addSelf=True)

        srcRootLen = len(srcPath)
        destRootLen = len(destPath)

        if destExists:
            if (isMove or not destRes.isCollection or not srcRes.isCollection):
                # MOVE:
                # If a resource exists at the destination and the Overwrite
                # header is "T", then prior to performing the move, the server
                # MUST perform a DELETE with "Depth: infinity" on the
                # destination resource.
                _logger.debug("Remove dest before move: '%s'" % destRes)
                destRes.delete()
                destRes = None
            else:
                # COPY collection over collection:
                # Remove destination files, that are not part of source, because
                # source and dest collections must not be merged (9.8.4).
                # This is not the same as deleting the complete dest collection
                # before copying, because that would also discard the history of
                # existing resources.
                reverseDestList = destRes.getDescendants(
                    depthFirst=True, addSelf=False)
                srcPathList = [s.path for s in srcList]
                _logger.debug("check srcPathList: %s" % srcPathList)
                for dRes in reverseDestList:
                    _logger.debug(
                        "check unmatched dest before copy: %s" % dRes)
                    relUrl = dRes.path[destRootLen:]
                    sp = srcPath + relUrl
                    if sp not in srcPathList:
                        _logger.debug(
                            "Remove unmatched dest before copy: %s" % dRes)
                        dRes.delete()

        # --- Let provider implement recursive move ----------------------------
        # We do this only, if the provider supports it, and no conflicts exist.
        # A provider can implement this very efficiently, without allocating
        # double memory as a copy/delete approach would.

        if isMove and srcRes.supportRecursiveMove(destPath):
            hasConflicts = False
            for s in srcList:
                try:
                    self._evaluateIfHeaders(s, environ)
                except Exception:
                    hasConflicts = True
                    break

            if not hasConflicts:
                try:
                    _logger.debug("Recursive move: %s -> '%s'" %
                                  (srcRes, destPath))
                    errorList = srcRes.moveRecursive(destPath)
                except Exception as e:
                    errorList = [(srcRes.getHref(), as_DAVError(e))]
                return self._sendResponse(environ, start_response,
                                          srcRes, successCode, errorList)

        # --- Copy/move file-by-file using copy/delete -------------------------

        # We get here, if
        # - the provider does not support recursive moves
        # - this is a copy request
        #   In this case we would probably not win too much by a native provider
        #   implementation, since we had to handle single child errors anyway.
        # - the source tree is partially locked
        #   We would have to pass this information to the native provider.

        # Hidden paths (paths of failed copy/moves) {<src_path>: True, ...}
        ignoreDict = {}

        for sRes in srcList:
            # Skip this resource, if there was a failure copying a parent
            parentError = False
            for ignorePath in list(ignoreDict.keys()):
                if util.is_equal_or_child_uri(ignorePath, sRes.path):
                    parentError = True
                    break
            if parentError:
                _logger.debug(
                    "Copy: skipping '%s', because of parent error" % sRes.path)
                continue

            try:
                relUrl = sRes.path[srcRootLen:]
                dPath = destPath + relUrl

                self._evaluateIfHeaders(sRes, environ)

                # We copy resources and their properties top-down.
                # Collections are simply created (without members), for
                # non-collections bytes are copied (overwriting target)
                sRes.copyMoveSingle(dPath, isMove)

                # If copy succeeded, and it was a non-collection delete it now.
                # So the source tree shrinks while the destination grows and we
                # don't have to allocate the memory twice.
                # We cannot remove collections here, because we have not yet
                # copied all children.
                if isMove and not sRes.isCollection:
                    sRes.delete()

            except Exception as e:
                ignoreDict[sRes.path] = True
                # TODO: the error-href should be 'most appropriate of the source
                # and destination URLs'. So maybe this should be the destination
                # href sometimes.
                # http://www.webdav.org/specs/rfc4918.html#rfc.section.9.8.5
                errorList.append((sRes.getHref(), as_DAVError(e)))

        # MOVE: Remove source tree (bottom-up)
        if isMove:
            reverseSrcList = srcList[:]
            reverseSrcList.reverse()
            util.status("Delete after move, ignore=", var=ignoreDict)
            for sRes in reverseSrcList:
                # Non-collections have already been removed in the copy loop.
                if not sRes.isCollection:
                    continue
                # Skip collections that contain errors (unmoved resources)
                childError = False
                for ignorePath in list(ignoreDict.keys()):
                    if util.is_equal_or_child_uri(sRes.path, ignorePath):
                        childError = True
                        break
                if childError:
                    util.status(
                        "Delete after move: skipping '%s', because of child error" % sRes.path)
                    continue

                try:
                    #                    _logger.debug("Remove source after move: %s" % sRes)
                    util.status("Remove collection after move: %s" % sRes)
                    sRes.delete()
                except Exception as e:
                    errorList.append((srcRes.getHref(), as_DAVError(e)))
            util.status("ErrorList", var=errorList)

        # --- Return response --------------------------------------------------

        return self._sendResponse(environ, start_response,
                                  srcRes, successCode, errorList)


wsgidav.request_server.RequestServer = VDOM_webdav_request_server
