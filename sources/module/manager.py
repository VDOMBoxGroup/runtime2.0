"""Module Manager module"""
from __future__ import absolute_import

from builtins import str
from builtins import object
from future.utils import raise_
import sys, traceback, shutil, os, types, re

import managers
from utils.exception import VDOM_exception
from utils.tracing import show_exception_trace

from .resource import VDOM_module_resource
from .python import VDOM_module_python
from .post_processing import VDOM_post_processing
from contextlib import contextmanager


guid_regex=re.compile("[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)


@contextmanager
def start_stop_request(actions):
    on_request_start = actions.get("requestonstart")
    if on_request_start and on_request_start.source_code:
        managers.engine.execute(on_request_start)

    yield

    on_request_stop = actions.get("requestonstop")
    if on_request_stop and on_request_stop.source_code:
        managers.engine.execute(on_request_stop)


class PathNotFound(Exception):
    pass


class VDOM_module_manager(object):
    """Module Manager class"""

    def process_request(self, request_object):
        """process request"""
        script_name = request_object.environment().environment()["SCRIPT_NAME"]
        if "127.0.0.1" != request_object.handler().client_address[0]:
            debug("Requested URL: '" + script_name + "'")
        # dirty HACK!!!
        if script_name.lower().startswith("/images/"):
            e = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "png": "image/png", "js": "text/javascript"}
            file = open("../images/" + script_name.split("/")[-1], "rb")
            ext = script_name.split(".")[-1].lower()
            data = file.read()
            file.close()
            if ext in e:
                request_object.add_header("Content-Type", e[ext])
                request_object.add_header("Cache-Control", "max-age=86400")
            else:
                raise_(AttributeError, ext)
            request_object.add_header("Content-Length", str(len(data)))
            return (None, data)
        if "/favicon.ico" == script_name:
            app = request_object.application()
            if not app or not app.icon:
                return (404, None)
            try:
                request_object.environment().environment()["REQUEST_URI"] = "/%s.res" % app.icon
                module = VDOM_module_resource()
                return (None, module.run(request_object, "res"))
            except Exception as e:
                debug(_("Module manager: resource module error: %s") % str(e))
                return (404, None)

        #parts1 = script_name.split("/")
        url_parts= [x for x in script_name.split("/") if "" != x]

        #parts = parts1[-1]
        #parts = parts.split(".")
        #if len(parts) == 1 and parts[0] != "":
        #    parts.append("vdom")
        #request_type = parts[-1].lower()
        #request_object.request_type = request_type
        #if "127.0.0.1" != request_object.handler().client_address[0]:
        #    debug("Request type: " + request_type)

        #parts1 = filter(lambda x: "" != x, parts1)
        if 2 == len(url_parts) and guid_regex.search(url_parts[0]) and guid_regex.search(url_parts[1]):
            try:    # preview
                a1 = managers.memory.applications[url_parts[0]] # CHECK: a1 = managers.xml_manager.get_application(parts1[0])
                request_object.set_application_id(a1.id)
                # o1 = a1.search_object(parts1[1])
                o1 = a1.objects.catalog.get(url_parts[1])
                if o1 and 3 == o1.type.container:
                    request_object.container_id = o1.id
                    request_object.request_type = "vdom"
                    # result = managers.engine.render(a1, o1, None, o1.type.render_type.lower())
                    result = managers.engine.render(o1, render_type=o1.type.render_type.lower())
                    return (None, result.encode("utf-8"))
            except: raise
        # check if container is present
        app = request_object.application()
        if not url_parts:
            if not app:
                ret = "Application not found"
                debug(ret)
                return (None, ret)
            # have no container id, try to redirect to the top level container
            elif app.index: # CHECK: if app.index_page:
                # _o = app.search_object(app.index) # CHECK: _o = app.search_object(app.index_page)
                _o = app.objects.catalog.get(app.index)
                if _o:
                    request_object.redirect("/%s.vdom" % _o.name.lower())
                else:
                    return (404, None)
            elif app.objects: # CHECK: len(app.get_objects_list()) > 0: # redirect to the first container
                request_object.redirect("/%s.vdom" % iter(app.objects.values()).next().name) # CHECK: request_object.redirect("/%s.vdom" % app.get_objects_list()[0].name)
            return (404, None)  # empty request

        request_type = url_parts[0].rpartition(".")[2] if '.' in url_parts[0] else 'vdom'
        request_object.request_type = request_type

        # this acts as Communication Dispatcher
        if "vdom" == request_type:  # VDOM container request
            # first chek if application is OK
            if not request_object.app_id(): # application not registered
                ret = "No application registered with virtual host '%s'" % request_object.app_vhname
                debug(ret)
                return (None, ret)
            if not app:
                ret = "Application not found"
                debug(ret)
                return (None, ret)
            if not app.active: # CHECK: if "1" != app.active:   # application not active
                ret = "Application not active"
                debug(ret)
                return (None, ret)
            target = url_parts[0]
            if target.endswith('.vdom'):
                target = target[:-5]
            container_id = target
            #request_object.container_id = container_id
            #debug("Container id: " + container_id)
            # get container object and check if it can be a top level container
            _a = managers.memory.applications[request_object.app_id()]
            #check for both guid, low case and original case
            obj = _a.objects.get(container_id) or _a.objects.catalog.get(container_id) or _a.objects.catalog.get(url_parts[0])

            # CHECK: if not obj:
            # CHECK:    for _i in _a.objects:
            # CHECK:        if _a.objects[_i].name == container_id:
            # CHECK:            obj = _a.objects[_i]
            # CHECK:            break

            if not obj:
                #check for onerror handler
                action = _a.actions.get("requestonerror")
                if action and action.source_code:
                    ee = PathNotFound(container_id)
                    request = managers.request_manager.get_request()
                    request.arguments().arguments()["error"] = [ee]
                    managers.engine.execute(action)
                    if request_object.wholeAnswer:
                        return (None, request_object.wholeAnswer.encode("utf-8"))
                return (404, None) #_("Container not found")


            if obj.parent != None:
                return (404, None)# _("This is not a top level container")

            if "1" == system_options["server_license_type"] and request_object.number_of_connections >2: # = len(obj.get_all_children()):
                return (503, None)

            # set content type of container
            if obj.type.http_content_type == "":
                return (None, _("Unknown content type"))
            request_object.add_header("Content-type", obj.type.http_content_type.lower())

            request_object.container_id = obj.id
            debug("Container id: " + obj.id)

            # execute session start action
            if not request_object.session().on_start_executed:
                action = _a.actions.get("sessiononstart")
                if action and action.source_code:
                    managers.engine.execute(action)
                    request_object.session().on_start_executed = True
            # CHECK: if not request_object.session().on_start_executed and _a.global_actions["session"]["sessiononstart"].code:
            # CHECK:    managers.engine.special(_a, _a.global_actions["session"]["sessiononstart"])
            # CHECK:    request_object.session().on_start_executed = True

            with start_stop_request(_a.actions):
                result = ""
                try:
                    result = managers.engine.render(obj, render_type=obj.type.render_type.lower())
                    # result = managers.engine.render(obj, None, obj.type.render_type.lower())
                    # CHECK: result = managers.engine.render(_a, obj, None, obj.type.render_type.lower())
                except VDOM_exception as e:
                    debug("Render exception: " + str(e))
                    show_exception_trace(caption="Module Manager: Render exception", locals=True)
                    return (None, str(e))
                except Exception as ee:
                    show_exception_trace(caption="Module Manager: Render exception", locals=True)
                    action = _a.actions.get("requestonerror")
                    if action and action.source_code:
                        request = managers.request_manager.get_request()
                        request.arguments().arguments()["error"] = [ee]
                        managers.engine.execute(action)
                        if request_object.wholeAnswer:
                            return (None, request_object.wholeAnswer.encode("utf-8"))
                    raise
                # finally:
                #     for key in request_object.files:
                #         if getattr(request_object.files[key][0],"name", None):
                #             if not request_object.files[key][0].closed:
                #                 request_object.files[key][0].close()
                #             os.remove(request_object.files[key][0].name)

                if request_object.fh:
                    from logs import log
                    # log.debug("REQUEST FILE HANDLER: %r" % request_object.fh)
                    shutil.copyfileobj(request_object.fh, request_object.wfile)
                    return (None, "")

                outp = request_object.output()
                if outp:
                    if request_object.binary():
                        return (None, outp)
                    else:
                        return (None, outp.encode("utf-8"))

                #debug("Result is: " + result.encode("utf-8"))

                # now do module post processing
    #           module = VDOM_post_processing()
    #           try:
    #               result = module.run(result)
    #           except:
    #               debug(_("Module manager: post processing error: %s") % sys.exc_info()[0])
    #               traceback.print_exc(file=debugfile)

                return None, result.encode("utf-8")

        elif "py" == request_type:  # dynamic python script, this doesn't require an application to be registered
            _a = managers.memory.applications[request_object.app_id()]
            with start_stop_request(_a.actions):
                try:
                    module = VDOM_module_python()
                    return (None, module.run(request_object))
                except Exception as e:
                    debug(("Module manager: python module error: %s") % str(e))
                    #traceback.print_exc(file=debugfile)
                    return 500, None
                # finally:
                #     for key in request_object.files:
                #         if not request_object.files[key][0].closed:
                #             request_object.files[key][0].close()
                #         os.remove(request_object.files[key][0].name)

        elif request_type:# pass to resource module
            module = VDOM_module_resource()
            ret = module.run(request_object, request_type)
            return (None, ret) if ret else (404, None)

        return (404, None)
