
#define release_python_object(object) Py_DECREF(object)


/* Pyhton Objects */

static PyObject *
hold_python_object(PyObject *object)
{
    Py_INCREF(object);
    return object;
}

static int
create_or_update_python_dictionary(PyObject **attributes, PyObject *name, PyObject *value)
{
    if (!*attributes)
    {
        *attributes = PyDict_New();
        if (!*attributes)
            return 1;
    }

    if (PyDict_SetItem(*attributes, name, value))
        return 1;

    return 0;
}

static int
invert_python_object(PyObject *object)
{
    PyObject *result;
    result = PyNumber_Invert(object);
    if (!result)
        return 1;
    return 0;
}

static PyObject *
decode_utf8_python_string(PyObject *object)
{
    if (PyBytes_CheckExact(object)) {
        return PyUnicode_DecodeUTF8(
            PyBytes_AS_STRING(object),
            PyBytes_GET_SIZE(object),
            "replace");
    } else if (PyUnicode_CheckExact(object)) {
        Py_INCREF(object);
        return object;
    } else {
        PyErr_SetString(PyExc_TypeError, "Expected bytes or unicode");
        return NULL;
    }
}


/* Memory Objects */

static PyObject *
create_new_memory_object(PyObject *parent, PyObject *name)
{
    PyObject *object_type, *objects, *new_sketch;
    PyObject *arguments, *keywords, *object;

    arguments = PyTuple_Pack(1, name);
    if (!arguments)
        return NULL;

    object_type = PyObject_CallObject(memory_types_search, arguments);
    Py_DECREF(arguments);
    if (!object_type)
        return NULL;

    if (object_type == Py_None)
    {
        PyErr_SetString(TypeNotFoundError, "No type available");
        return NULL;
    }

    objects = PyObject_GetAttrString(parent, "objects");
    if (!objects)
    {
        Py_DECREF(object_type);
        return NULL;
    }

    new_sketch = PyObject_GetAttrString(objects, "new_sketch");
    Py_DECREF(objects);
    if (!new_sketch)
    {
        Py_DECREF(object_type);
        return NULL;
    }

    arguments = PyTuple_Pack(1, object_type);
    Py_DECREF(object_type);
    if (!arguments)
    {
        Py_DECREF(new_sketch);
        return NULL;
    }

    keywords = PyDict_New();
    if (!keywords)
    {
        Py_DECREF(new_sketch);
        Py_DECREF(arguments);
        return NULL;
    }

    Py_INCREF(Py_True);
    if (PyDict_SetItemString(keywords, "virtual", Py_True))
    {
        Py_DECREF(Py_True);
        Py_DECREF(new_sketch);
        Py_DECREF(arguments);
        Py_DECREF(keywords);
        return NULL;
    }

    object = PyObject_Call(new_sketch, arguments, keywords);
    Py_DECREF(new_sketch);
    Py_DECREF(arguments);
    Py_DECREF(keywords);
    if (!object)
        return NULL;

    return object;
}

static int
set_memory_object_name(PyObject *object, PyObject *name)
{
    if (PyObject_SetAttrString(object, "name", name))
        return 1;
    return 0;
}

static int
update_memory_object_attributes(PyObject *object, PyObject *attributes)
{
    PyObject *object_attributes, *result;

    object_attributes = PyObject_GetAttrString(object, "attributes");
    if (!object_attributes)
        return 1;

    result = PyObject_CallMethod(object_attributes, "update", "(O)", attributes);
    Py_DECREF(object_attributes);
    if (!result)
        return 1;

    Py_DECREF(result);
    return 0;
}


/* Error Handling */

static void
create_or_update_error(int line, int column)
{
    PyObject *type, *value, *traceback;
    PyErr_Fetch(&type, &value, &traceback);
    if (type)
    {
        PyObject *line_object, *column_object;
        line_object = Py_BuildValue("i", line);
        if (line_object)
        {
            PyObject_SetAttrString(type, "line", line_object);
            Py_DECREF(line_object);
        }
        if (column)
        {
            column_object = Py_BuildValue("i", column);
            if (column_object)
            {
                PyObject_SetAttrString(type, "column", column_object);
                Py_DECREF(column_object);
            }
        }
        PyErr_Restore(type, value, traceback);
    }
    else
    {
        PyErr_SetString(PyExc_RuntimeError, "Internal error");
    }
}
