

import re
import json


ERROR_REGEX = re.compile(r"(.+): line (\d+) column \d+ \(char (\d+)\)$")


class ParsingException(Exception):

    def __init__(self, message, line=None, column=None):
        super(ParsingException, self).__init__(message)
        self.message = message
        self.line = line
        self.column = column


def loads(vdomjson, object, catch, handler=None):
    try:
        actions = json.loads(vdomjson)
    except Exception as error:
        message = str(error)
        match = ERROR_REGEX.match(message)
        if match:
            message, line, column = match.groups()
            raise ParsingException(message, int(line), int(column))
        elif isinstance(error, ValueError):
            raise ParsingException(message)
        else:
            raise

    if not actions:
        return ()

    bindings = []
    for event_declaration, event_actions in actions.items():
        try:
            source_name, event_name = event_declaration.split(":")
        except Exception:
            raise Exception("Invalid event declaration: %s" % event_declaration)

        source = object.select_original(*source_name.split("."))
        if not source:
            raise Exception("Unable to find object: %s" % source_name)

        if isinstance(event_actions, str):
            source.actions.new(event_name, source_code=event_actions, handler=handler)
        else:
            event = source.events.new(event_name)
            for action in event_actions:
                if isinstance(action, list):
                    try:
                        target_name, action_name = action[0].split(":")
                    except Exception:
                        raise Exception("Invalid action declaration: %s" % action[0])

                    target = object.select_original(*target_name.split("."))
                    if not target:
                        raise Exception("Can't find object by name: %s" % target_name)

                    binding = event.callees.new(target, action_name, parameters=action[1:])
                else:
                    binding = event.callees.new(catch, "catchEvent", parameters=("\"%s\"" % action, "evt_param(\"evt_ref\")"))
                bindings.append(binding)

    return bindings
