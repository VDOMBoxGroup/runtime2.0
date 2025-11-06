
from builtins import object
import managers


class VDOM_log(object):

    def write(self, message, *arguments, **keywords):
        uuid = managers.engine.application.id
        user = keywords.get("user")
        managers.log_manager.logs.application(uuid).write(message % arguments, module=uuid, user=user)

    def debug(self, message, *arguments, **keywords):
        uuid = managers.engine.application.id
        user = keywords.get("user")
        managers.log_manager.logs.application(uuid).debug(message % arguments, module=uuid, user=user)

    def warning(self, message, *arguments, **keywords):
        uuid = managers.engine.application.id
        user = keywords.get("user")
        managers.log_manager.logs.application(uuid).warning(message % arguments, module=uuid, user=user)

    def error(self, message, *arguments, **keywords):
        uuid = managers.engine.application.id
        user = keywords.get("user")
        managers.log_manager.logs.application(uuid).error(message % arguments, module=uuid, user=user)
