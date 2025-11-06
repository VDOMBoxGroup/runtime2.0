import codecs



from io import StringIO


def dumps(object, file=None, profile=None):
    types = set()

    def compose(object, indent=u"", file=None):
        object_type = object.type.name
        object_name = object.name
        attribute_values = " ".join("%s=\"%s\"" % (name, codecs.encode(value, "xml")) for name, value
            in object.attributes.items() if value != object.type.attributes[name].default_value)
        subobjects = object.objects
        if subobjects:
            file.write("%s<%s name=\"%s\" %s>\n" % (indent, object_type, object_name, attribute_values))
            for subobject in subobjects.values():
                compose(subobject, indent=indent + u"    ", file=file)
            file.write("%s</%s>\n" % (indent, object_type))
        else:
            file.write("%s<%s name=\"%s\" %s/>\n" % (indent, object_type, object_name, attribute_values))
        types.add(object.type)

    def write_profile(types):
        profile.write("<profile>\n")
        for type in types:
            profile.write("    <%s version=\"%s\">\n" % (type.name, type.version))
        profile.write("</profile>\n")

    if not file:
        file = StringIO()
        compose(object, file=file)
        if profile:
            write_profile(profile)
        return file.getvalue()
    else:
        compose(object, file=file)
        if profile:
            write_profile(profile)
