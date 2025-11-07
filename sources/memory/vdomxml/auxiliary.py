
from uuid import uuid4
import managers


def create_object(parent_objects, name, attributes):
    object_type = managers.memory.types.search(name)
    if object_type is None:
        raise Exception("Unknown type: %s" % name)

    try:
        object_name = attributes.pop("name")
    except KeyError:
        raise Exception("Require name")

    object = parent_objects.new_sketch(object_type, virtual=True)
    object.id = str(uuid4())
    object.name = object_name

    object.attributes.update(attributes)
    attributes.clear()

    return object
