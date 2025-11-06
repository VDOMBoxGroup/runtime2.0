import managers
from traceback import print_exc


class InvalidParamsException(Exception):
    pass


def run(request):
    args = request.arguments().arguments()
    request.render_type = "e2vdom"
    #auth = request.headers().headers().get("Authorization")
    #if not auth:
        #request.add_header("WWW-Authenticate","Basic realm=\"vdom\"")
        #request.send_htmlcode(401)

        #return
    #else:
        #if auth[:len("Basic ")]=="Basic ":
            #user,login = base64.b64decode(auth[len("Basic "):]).split(":")
            #sem = VDOM_semaphore()
            #sem.lock()
            #try:
                #if not managers.user_manager.match_user_md5(user, hashlib.md5(login).hexdigest()):
                    #time.sleep(1)
                    #request.send_htmlcode(401)
                    #return
            #finally:
                #sem.unlock()
    appid = args.get("appid")[0] if args.get("appid") else request.app_id()
    container = args.get("objid")[0] if args.get("objid") else "API"
    action = args.get("action_name")[0] if args.get("action_name") else ""
    xml_param = args.get("xml_param")[0] if args.get("xml_param") else ""
    xml_data = args.get("xml_data")[0] if args.get("xml_data") else ""
    callback = args.get("callback")[0] if args.get("callback") else ""

    if not (appid != '' and container != '' and action != ''):
        request.write("<ERROR>Invalid params</ERROR>")
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
                ret = request.session().value("response")
                request.session().remove("response")
                if isinstance(ret, str):
                    ret = ret.encode("utf8", "ignore")
        except InvalidParamsException as ex:
            request.write("<ERROR>%s</ERROR>" % ex.message)
        except Exception as e:
            print_exc()
            request.write("<ERROR>%s</ERROR>"%e)
        else:
            request.write("/**/ %s(%s);" % (callback, ret) if callback else ret)
