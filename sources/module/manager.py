"""Module Manager module"""
from __future__ import absolute_import


import shutil
import re
from contextlib import contextmanager

import managers

import settings
from utils.exception import VDOM_exception
from utils.tracing import show_exception_trace
from utils.body import write_in_blocks

from .resource import VDOM_module_resource
from .python import VDOM_module_python
# from .post_processing import VDOM_post_processing


RE_GUID = re.compile(
    "[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)


def _close_sent(request_object):
    """Close the file a response was sent from (response.send_file). It was
    left open until collected: on Windows an open file cannot be renamed or
    deleted, so a resource just served could not be renamed (WinError 32)."""
    handler, request_object.fh = request_object.fh, None
    try:
        handler.close()
    except Exception:  # noqa - a handler without close, or closed already
        pass


@contextmanager
def start_stop_request(actions):
    on_request_start = actions.get("requestonstart")
    if on_request_start and on_request_start.source_code:
        managers.engine.execute(on_request_start)

    yield

    on_request_stop = actions.get("requestonstop")
    if on_request_stop and on_request_stop.source_code:
        managers.engine.execute(on_request_stop)


def onerror_handler(request_object, app):
    action = app.actions.get("requestonerror")
    if action and action.source_code:
        request = managers.request_manager.get_request()
        request.arguments().arguments()["error"] = [
            PathNotFound(request_object.container_id)]
        managers.engine.execute(action)
        if request_object.wholeAnswer:
            return (None, request_object.wholeAnswer.encode("utf-8"))
        else:
            if request_object.fh:
                # Bounded blocks, not shutil.copyfileobj: see utils/body.
                try:
                    write_in_blocks(request_object.fh, request_object.wfile,
                                    announced=_announced_length(request_object),
                                    where=_request_path(request_object), trace=debug)
                finally:
                    _close_sent(request_object)
                return (None, "")
            outp = request_object.output()
            if outp:
                if request_object.binary():
                    return (None, outp)
                else:
                    return (None, outp.encode("utf-8"))

    return (404, None)  # _("Container not found")



def _announced_length(request_object):
    """The length told to the client, if one was set - to compare against."""
    try:
        for name, value in request_object.headers_out().headers().items():
            if name.lower() == "content-length":
                return int(value)
    except Exception:
        pass
    return None


def _request_path(request_object):
    try:
        return request_object.environment().environment().get("REQUEST_URI", "?")
    except Exception:
        return "?"


class PathNotFound(Exception):
    pass


class VDOM_module_manager(object):
    """Module Manager class"""

    def process_request(self, request_object):
        """process request"""
        script_name = request_object.environment().environment()["SCRIPT_NAME"]
        if "127.0.0.1" != request_object.handler().client_address[0]:
            debug("Requested URL: '" + script_name + "'")
        # if script_name.lower().startswith("/images/"):
            # e = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif",
            # "png": "image/png", "js": "text/javascript"}
            # file = open("../images/" + script_name.split("/")[-1], "rb")
            # ext = script_name.split(".")[-1].lower()
            # data = file.read()
            # file.close()
            # if ext in e:
            # request_object.add_header("Content-Type", e[ext])
            # request_object.add_header("Cache-Control", "max-age=86400")
            # else:
            # raise AttributeError(ext)
            # request_object.add_header("Content-Length", str(len(data)))
            # return (None, data)
        if "/favicon.ico" == script_name:
            app = request_object.application()
            if not app or not app.icon:
                return (404, None)
            try:
                request_object.environment().environment()[
                    "REQUEST_URI"] = "/%s.res" % app.icon
                module = VDOM_module_resource()
                return (None, module.run(request_object, "res"))
            except Exception as e:
                debug(_("Module manager: resource module error: %s") % e)
                return (404, None)

        url_parts = [x for x in script_name.split("/") if "" != x]

        # parts = parts1[-1]
        # parts = parts.split(".")
        # if len(parts) == 1 and parts[0] != "":
        #    parts.append("vdom")
        # request_type = parts[-1].lower()
        # request_object.request_type = request_type
        # if "127.0.0.1" != request_object.handler().client_address[0]:
        #    debug("Request type: " + request_type)

        # a BlueMail session (admin/bluedynamic.py) acts on its own dynamic
        # interface only: through e2vdom.py, and the resources its page loads
        # by guid. No container, no API, no page of the application: they
        # would run with a session that its plugin's page names in the clear.
        session = request_object.session()
        if session is not None and session.bd_scope:
            allowed = script_name.lower() in ("/e2vdom.py", "/bluedynamic.py") or (
                1 == len(url_parts) and "." in url_parts[0]
                and RE_GUID.match(url_parts[0].partition(".")[0]))
            if not allowed:
                debug("BlueMail session refused on %s" % script_name)
                return (403, None)

        # preview mode: /<application>/<container> is /<container>, with the
        # same checks and the same hooks. It used to render the container
        # straight away: any top level container of any installed
        # application, without requestonstart or sessiononstart - where an
        # application checks who is asking.
        if 2 == len(url_parts) and RE_GUID.search(url_parts[0]) and RE_GUID.search(url_parts[1]):
            preview_id = url_parts[0].lower()
            if preview_id != (request_object.app_id() or "").lower():
                if not settings.PREVIEW_ANY_APPLICATION:
                    return (404, None)
                try:
                    preview_application = managers.memory.applications[preview_id]
                except KeyError:
                    return (404, None)
                request_object.set_application_id(preview_application.id)
                session.context["application_id"] = preview_application.id
            url_parts = [url_parts[1]]

        # check if container is present
        app = request_object.application()
        if not url_parts:
            if not app:
                ret = "Application not found"
                debug(ret)
                return (None, ret)
            # "/" is the index container (or else the first one), answered in
            # place: a redirect to /<name>.vdom showed the container name in
            # the address, and the application never saw the request for "/".
            index = app.objects.catalog.get(app.index) if app.index else None
            if index is None and not app.index and app.objects:
                index = next(iter(app.objects.values()))
            if index is None:
                return (404, None)  # empty request
            url_parts = [index.name.lower()]

        request_type = url_parts[0].rpartition(
            ".")[2] if '.' in url_parts[0] else 'vdom'
        request_object.request_type = request_type

        # this acts as Communication Dispatcher
        if request_type == "vdom":  # VDOM container request
            # first chek if application is OK
            if not request_object.app_id():  # application not registered
                # first check if application is OK
                ret = "No application registered with virtual host '%s'" % request_object.app_vhname
                debug(ret)
                return (None, ret)
            if not app:
                ret = "Application not found"
                debug(ret)
                return (None, ret)
            if not app.active:  # CHECK: if "1" != app.active:   # application not active
                ret = "Application not active"
                debug(ret)
                return (None, ret)
            target = url_parts[0]
            if target.endswith('.vdom'):
                target = target[:-5]
            container_id = target
            # request_object.container_id = container_id
            # debug("Container id: " + container_id)
            # get container object and check if it can be a top level container
            _a = managers.memory.applications[request_object.app_id()]
            # check for both guid, low case and original case
            obj = _a.objects.get(container_id) \
                or _a.objects.catalog.get(container_id) \
                or _a.objects.catalog.get(url_parts[0])

            # CHECK: if not obj:
            # CHECK:    for _i in _a.objects:
            # CHECK:        if _a.objects[_i].name == container_id:
            # CHECK:            obj = _a.objects[_i]
            # CHECK:            break

            if not obj:
                # check for onerror handler
                return onerror_handler(request_object, _a)

            if obj.parent is not None:
                return (404, None)  # _("This is not a top level container")

            # = len(obj.get_all_children()):
            if "1" == system_options["server_license_type"] and request_object.number_of_connections > 2:
                return (503, None)

            # set content type of container
            if obj.type.http_content_type == "":
                return (None, _("Unknown content type"))
            request_object.add_header(
                "Content-type", obj.type.http_content_type.lower())

            request_object.container_id = obj.id
            debug("Container id: " + obj.id)

            # execute session start action
            if not request_object.session().on_start_executed:
                action = _a.actions.get("sessiononstart")
                if action and action.source_code:
                    managers.engine.execute(action)
                    request_object.session().on_start_executed = True
            with start_stop_request(_a.actions):
                result = ""
                try:
                    result = managers.engine.render(
                        obj, render_type=obj.type.render_type.lower())

                except VDOM_exception as e:
                    # result = managers.engine.render(obj, None, obj.type.render_type.lower())
                    # CHECK: result = managers.engine.render(_a, obj, None, obj.type.render_type.lower())
                    debug("Render exception: " + str(e))
                    show_exception_trace(
                        caption="Module Manager: Render exception", locals=True)
                    return (None, str(e))
                except Exception:
                    show_exception_trace(
                        caption="Module Manager: Render exception", locals=True)

                    code, ret = onerror_handler(request_object, _a)
                    if ret:
                        return code, ret
                    raise
                # finally:
                #     for key in request_object.files:
                #         if getattr(request_object.files[key][0],"name", None):
                #             if not request_object.files[key][0].closed:
                #                 request_object.files[key][0].close()
                #             os.remove(request_object.files[key][0].name)

                if request_object.fh:
                    # Bounded blocks, not shutil.copyfileobj: see utils/body.
                    # This is the path that serves an application's resources -
                    # a one-megabyte app.js went out in a single write and
                    # arrived truncated with nothing anywhere saying so.
                    try:
                        write_in_blocks(request_object.fh, request_object.wfile,
                                        announced=_announced_length(request_object),
                                        where=_request_path(request_object),
                                        trace=debug)
                    finally:
                        _close_sent(request_object)
                    return (None, "")

                outp = request_object.output()
                if outp:
                    if request_object.binary():
                        return (None, outp)
                    else:
                        if isinstance(outp, str):
                            return (None, outp.encode("utf-8"))
                        else:
                            return (None, outp)

                # debug("Result is: " + result.encode("utf-8"))

                # now do module post processing
    #           module = VDOM_post_processing()
    #           try:
    #               result = module.run(result)
    #           except:
    #               debug(("Module manager: post processing error: %s") % sys.exc_info()[0])
    #               traceback.print_exc(file=debugfile)

                return None, result.encode("utf-8")

        elif "py" == request_type:  # dynamic python script, this doesn't require an application to be registered
            app_id = request_object.app_id()
            _a = managers.memory.applications[app_id].actions if app_id else {}
            with start_stop_request(_a):
                try:  # TODO: PY3
                    module = VDOM_module_python()
                    return (None, module.run(request_object))
                except Exception:
                    raise
                #    debug(("Module manager: python module error: %s") % str(e))
                #    #traceback.print_exc(file=debugfile)
                #    return 500, None
                # finally:
                #     for key in request_object.files:
                #         if not request_object.files[key][0].closed:
                #             request_object.files[key][0].close()
                #         os.remove(request_object.files[key][0].name)

        elif request_type:  # pass to resource module
            module = VDOM_module_resource()
            ret = module.run(request_object, request_type)
            if not ret and settings.HANDLE_NO_RESOURCE:
                return onerror_handler(request_object, request_object.application())
            return (None, ret) if ret else (404, None)

        return (404, None)
