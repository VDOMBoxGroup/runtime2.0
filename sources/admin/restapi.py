import re
import managers
from traceback import print_exc
from utils.exception import exception_message


RE_CALLBACK = re.compile(r"^[A-Za-z_$][0-9A-Za-z_$.]{0,127}$")


class InvalidParamsException(Exception):
    pass


def run(request):
    args = request.arguments().arguments()
    request.render_type = "e2vdom"
    # auth = request.headers().headers().get("Authorization")
    # if not auth:
    #     request.add_header("WWW-Authenticate","Basic realm=\"vdom\"")
    #     request.send_htmlcode(401)

    #     return
    # else:
    #     if auth[:len("Basic ")]=="Basic ":
    #         user,login = base64.b64decode(auth[len("Basic "):]).split(":")
    #         sem = VDOM_semaphore()
    #         sem.lock()
    #         try:
    #             if not managers.user_manager.match_user_md5(user, hashlib.md5(login).hexdigest()):
    #                 time.sleep(1)
    #                 request.send_htmlcode(401)
    #                 return
    #         finally:
    #             sem.unlock()
    appid = args.get("appid")[0] if args.get("appid") else request.app_id()
    container = args.get("objid")[0] if args.get("objid") else "API"
    action = args.get("action_name")[0] if args.get("action_name") else ""
    xml_param = args.get("xml_param")[0] if args.get("xml_param") else ""
    xml_data = args.get("xml_data")[0] if args.get("xml_data") else ""
    callback = args.get("callback")[0] if args.get("callback") else ""

    if not (appid != '' and container != '' and action != ''):
        request.write(b"<ERROR>Invalid params</ERROR>")
    else:
        try:
            if appid not in managers.memory.applications:
                raise InvalidParamsException("Invalid params")
            request.set_application_id(appid)
            app = request.application()
            if container.lower() == 'api':
                obj = app.objects.select(container)
            else:
                obj = app.objects.catalog.get(container)
            if not obj or obj.name.lower() != "api":
                raise InvalidParamsException("Invalid params")
            else:
                if action not in obj.actions:
                    raise InvalidParamsException("Invalid params")

                if not xml_data and request.method == "post":
                    xml_data = {k: v for k, v in list(args.items()) if k not in ("appid", "objid", "action_name", "xml_param", "callback", "sid")}
                request.arguments().arguments({"xml_param": [xml_param], "xml_data": [xml_data]})
                request.container_id = obj.id
                result = managers.engine.execute(obj.actions[action])
                ret = request.session().value("response") or result
                request.session().remove("response")
                if isinstance(ret, str):
                    ret = ret.encode("utf8", "ignore")
        except InvalidParamsException as ex:
            request.write(f"<ERROR>{exception_message(ex)}</ERROR>".encode())
        except Exception as e:
            print_exc()
            # `%` on an f-string raised TypeError here, so an action that
            # failed answered nothing at all instead of its error
            request.write(f"<ERROR>{exception_message(e)}</ERROR>".encode("utf8", "ignore"))
        else:
            # the output is a BytesIO: a str (the JSONP wrapper, or an action
            # returning a number) raised TypeError and the answer was lost
            if isinstance(ret, bytes):
                body = ret
            elif ret is None:
                body = b""
            else:
                body = str(ret).encode("utf8", "ignore")
            if callback:
                # a JSONP callback is a name, never code from the address
                if not RE_CALLBACK.match(callback):
                    request.write(b"<ERROR>Invalid params</ERROR>")
                    return
                body = b"/**/ " + callback.encode("ascii") + b"(" + body + b");"
            request.write(body)
