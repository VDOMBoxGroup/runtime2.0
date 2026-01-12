
#include <Python.h>

#include <structmember.h>
#include <stdio.h>

#ifdef WORDS_BIGENDIAN
#   error "Big-endian platforms are not supported"
#endif

#if ULONG_MAX < 0x3FFFFFFF
#   error "Require at least 31 bits to keep hashes"
#endif

#define DEBUG
#define DECODE_STRING

#define BUFFER_LENGTH 16
#define ELEMENTS_BATCH_SIZE 64
#define SUBSTRINGS_BATCH_SIZE 256
#define OBJECTS_BATCH_SIZE 1024


/* Exceptions */

static PyObject *BaseException = NULL;
static PyObject *UnableToParseError = NULL;
static PyObject *WrongCharacterError = NULL;
static PyObject *NameDoesNotMatchError = NULL;
static PyObject *TypeNotFoundError = NULL;


/* External Methods */

static PyObject *memory_types_search = NULL;


/* Types & Functions */

#include "states.h"
#include "symbols.h"
#include "types.h"
#include "auxiliary.h"
#include "strings.h"
#include "memory.h"
#include "wrappers.h"
#include "parsing.h"
#include "callbacks.h"
#include "table.h"


/* Import */

static int
import_objects(void)
{
    PyObject *managers, *memory, *types;

    managers = PyImport_ImportModule("managers");
    if (!managers)
        return 1;

    memory = PyObject_GetAttrString(managers, "memory");
    Py_DECREF(managers);
    if (!memory)
        return 1;

    types = PyObject_GetAttrString(memory, "types");
    Py_DECREF(memory);
    if (!types)
        return 1;

    memory_types_search = PyObject_GetAttrString(types, "search");
    Py_DECREF(types);
    if (!memory_types_search)
        return 1;

    return 0;
}


/* Finalization */

static int
finalize_object(PyObject **object)
{
    if (invert_python_object(*object))
        return 1;
    Py_DECREF(*object);
    return 0;
}

static int
finalize_objects(Parse *parse)
{
    if (iterate_stockpile(&parse->stockpiles.references, (StockpileIterateCallback)finalize_object))
        return 1;
    release_all_on_stockpile(&parse->stockpiles.references);
    return 0;
}


/* Parsing */

static PyObject *
parse(Data data, DataSize size, int is_unicode, PyObject *origin)
{
    Parse parse = {is_unicode, data, data + size, 1, 0, START};
    Element document = {NULL, GenericElement, NULL, NULL, origin};

    initialize_stockpile(&parse.stockpiles.elements, sizeof(Element), ELEMENTS_BATCH_SIZE);
    initialize_stockpile(&parse.stockpiles.substrings, sizeof(Substring), SUBSTRINGS_BATCH_SIZE);
    initialize_stockpile(&parse.stockpiles.references, sizeof(PyObject *), OBJECTS_BATCH_SIZE);

    /* the main concept of storing strings - is to store all strings in one format,
       string - for string source data and unicode - for unicode source data
       this allow us to compare python raw data without converting them each time
       below we define set of string functions to wrork with all string data */

    if (is_unicode)
    {
        parse.match_string = (MatchString)unicode_match_string;
        parse.is_equal_to_string = (IsEqualToString)unicode_is_equal_to_string;
        parse.is_equal_to_python_string = unicode_is_equal_to_python_string;
        parse.python_string_is_equal_to_string = unicode_python_string_is_equal_to_string;
        parse.create_python_string = unicode_create_python_string;
        parse.create_python_string_from_substrings = unicode_create_python_string_from_substrings;
        parse.create_empty_python_string = unicode_create_empty_python_string;
        parse.write_character = unicode_write_character;
    }
    else
    {
        parse.match_string = string_match_string;
        parse.is_equal_to_string = string_is_equal_to_string;
        parse.is_equal_to_python_string = string_is_equal_to_python_string;
        parse.python_string_is_equal_to_string = string_python_string_is_equal_to_string;
        parse.create_python_string = string_create_python_string;
        parse.create_python_string_from_substrings = string_create_python_string_from_substrings;
        parse.create_empty_python_string = string_create_empty_python_string;
        parse.write_character = string_write_character;
    }

    parse.element = &document;
    for(;;)
    {
        State next_state;
        Data next_data = parse.data;

        if (parse.data < parse.stop)
        {
            parse.character = is_unicode \
                ? UNICODE_NEXT(next_data, parse.stop) \
                : STRING_NEXT(next_data, parse.stop);

            switch (parse.character)
            {
            case '\n':
                parse.line++;
            case '\r':
                parse.column = 0;
                break;
            default:
                parse.column++;
            }

            /* categorize character to reduce possible combinations
               and except prohibited xml characters from good ones */

            if (parse.character < 0x80)
                parse.symbol = symbols[parse.character];
            else if (parse.character <= 0xD7FF
                    || (parse.character >= 0xE000 && parse.character <= 0xFFFD)
                    || (parse.character >= 0x10000 && parse.character <= 0x10FFFF))
                parse.symbol = CHARACTER;
            else
                parse.symbol = WRONG;
        }
        else
        {
            parse.symbol = END;
            parse.character = 0x0E0F0E0F;
        }

        /* each table cell keeps next state and optional callback and return state
           when we have callback we call them and get desired state from it
           in case of non-zero returns we select this value instead cell's one
           return state is used to return from auxiliary chains which are called
           from different states and must know where to return - no one of such chains
           can use return state inside */

        if (parse.symbol == WRONG)
        {
            parse.state = wrong_character(&parse);
        }
        else
        {
            parse.cell = &table[parse.state-1][parse.symbol];

            if (parse.cell->return_state)
            {
#ifdef DEBUG
                if (parse.cell->return_state == RESET_RETURN)
                {
                    if (!parse.return_state && parse.cell->return_state != RESET_RETURN)
                    {
                        PyErr_SetString(PyExc_RuntimeError, "Unable to clean empty return state");
                        goto cleanup;
                    }
                    parse.return_state = NEXT;
                }
                else
                {
                    if (parse.return_state)
                    {
                        PyErr_SetString(PyExc_RuntimeError, "Unclean return state");
                        goto cleanup;
                    }
#endif
                    parse.return_state = parse.cell->return_state;
#ifdef DEBUG
                }
#endif
            }

            if (parse.cell->callback)
            {
                next_state = parse.cell->callback(&parse);
                if (next_state == NEXT)
                    next_state = parse.cell->state;
            }
            else
            {
                next_state = parse.cell->state;
            }

            if (next_state != KEEP)
                parse.state = next_state;
        }

        parse.data = next_data;

        /* there we check if we done our job, handle errors and handle return state,
           in case of error we try to correct clean up resources, in case of normal
           termination we only need to finalize objects and clean up references */

        switch(parse.state)
        {
        case COMPLETE:
#ifdef DEBUG
            if (parse.element->parent)
            {
                PyErr_SetString(PyExc_RuntimeError, "Unclean element");
                goto failure;
            }
            if (parse.element->name)
            {
                PyErr_SetString(PyExc_RuntimeError, "Unclean element name");
                goto failure;
            }
            if (parse.element->attributes)
            {
                PyErr_SetString(PyExc_RuntimeError, "Unclean element attributes");
                goto failure;
            }
            if (parse.element->object != origin)
            {
                PyErr_SetString(PyExc_RuntimeError, "Inconsistent element object");
                goto failure;
            }
            if (parse.attribute.name)
            {
                PyErr_SetString(PyExc_RuntimeError, "Unclean attribute name");
                goto failure;
            }
            if (parse.substrings.list)
            {
                PyErr_SetString(PyExc_RuntimeError, "Unclean substrings");
                goto failure;
            }
#endif
            if (finalize_objects(&parse))
            {

                PyErr_SetString(UnableToParseError, "Unable to finalize objects");
                goto failure;
            }

            deinitialize_stockpile(&parse.stockpiles.elements);
            deinitialize_stockpile(&parse.stockpiles.substrings);
            deinitialize_stockpile(&parse.stockpiles.references);

            return parse.result;
        case FAILURE:
            create_or_update_error(parse.line, parse.column);
            goto cleanup;
        case RETURN:
            parse.state = parse.return_state;
#ifdef DEBUG
            parse.return_state = NEXT;
#endif
        default:
            break;
        }
    }

cleanup:

    cleanup_attribute(&parse);
    cleanup_elements(&parse);
    cleanup_substrings(&parse);
    cleanup_references(&parse);

failure:

    if (parse.result)
        release_python_object(parse.result);

    deinitialize_stockpile(&parse.stockpiles.elements);
    deinitialize_stockpile(&parse.stockpiles.substrings);
    deinitialize_stockpile(&parse.stockpiles.references);

    return NULL;
}


/* Functions */

static PyObject *
loads_loads(PyObject *self, PyObject *arguments)
{
    PyObject *object=NULL, *origin=NULL;

    if (!PyArg_ParseTuple(arguments, "OO", &object, &origin))
        return NULL;

    if (!memory_types_search && import_objects())
        return NULL;

    if (PyBytes_CheckExact(object))
    {
#ifdef DECODE_STRING
        PyObject *unicode = decode_utf8_python_string(object), *result;
        Py_ssize_t size;
        const char *data;
        if (!unicode)
            return NULL;
        data = PyUnicode_AsUTF8AndSize(unicode, &size);
        if (!data) {
            Py_DECREF(unicode);
            return NULL;
        }
        result = parse((Data)data, size, 1, origin);
        Py_DECREF(unicode);
        return result;
#else
        return parse((Data)PyBytes_AS_STRING(object), PyBytes_GET_SIZE(object), 0, origin);
#endif
    }
    else if (PyUnicode_CheckExact(object))
    {
        Py_ssize_t size;
        const char *data = PyUnicode_AsUTF8AndSize(object, &size);
        if (!data)
            return NULL;
        return parse((Data)data, size, 1, origin);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "Require string or unicode to parse");
        return NULL;
    }
}


/* Initialization */

static PyMethodDef module_methods[] =
{
    {"loads", (PyCFunction)loads_loads, METH_VARARGS, "loads"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "_loads",
    NULL,
    -1,
    module_methods
};

PyMODINIT_FUNC PyInit__loads(void)
{
    PyObject *module, *none, *error_dictionary;

    module = PyModule_Create(&module_def);
    if (!module)
        return NULL;

    /* release objects in case of reinitialization */

    Py_XDECREF(BaseException);
    Py_XDECREF(UnableToParseError);
    Py_XDECREF(WrongCharacterError);
    Py_XDECREF(NameDoesNotMatchError);
    Py_XDECREF(TypeNotFoundError);

    if (memory_types_search)
    {
        Py_DECREF(memory_types_search);
        memory_types_search = NULL;
    }

    /* construct module execptions */

    error_dictionary = PyDict_New();
    if (!error_dictionary)
        return NULL;

    error_dictionary = PyDict_New();
    if (!error_dictionary)
        return NULL;

    none = Py_BuildValue("");
    if (!none)
    {
        Py_DECREF(error_dictionary);
        return NULL;
    }
    if (PyDict_SetItemString(error_dictionary, "line", none))
    {
        Py_DECREF(none);
        Py_DECREF(error_dictionary);
        return NULL;
    }

    none = Py_BuildValue("");
    if (!none)
    {
        Py_DECREF(error_dictionary);
        return NULL;
    }
    if (PyDict_SetItemString(error_dictionary, "column", none))
    {
        Py_DECREF(none);
        Py_DECREF(error_dictionary);
        return NULL;
    }

    BaseException = PyErr_NewException("memory.vdomxml.loads.BaseException", NULL, error_dictionary);
    if (!BaseException)
    {
        Py_DECREF(error_dictionary);
        return NULL;
    }

    Py_DECREF(error_dictionary);

    if (PyModule_AddObject(module, "BaseException", BaseException))
        return NULL;

    UnableToParseError = PyErr_NewException("memory.vdomxml.loads.UnableToParseError", BaseException, NULL);
    if (!UnableToParseError)
        return NULL;
    if (PyModule_AddObject(module, "UnableToParseError", UnableToParseError))
        return NULL;

    WrongCharacterError = PyErr_NewException("memory.vdomxml.loads.WrongCharacterError", BaseException, NULL);
    if (!WrongCharacterError)
        return NULL;
    if (PyModule_AddObject(module, "WrongCharacterError", WrongCharacterError))
        return NULL;

    NameDoesNotMatchError = PyErr_NewException("memory.vdomxml.loads.NameDoesNotMatchError", BaseException, NULL);
    if (!NameDoesNotMatchError)
        return NULL;
    if (PyModule_AddObject(module, "NameDoesNotMatchError", NameDoesNotMatchError))
        return NULL;

    TypeNotFoundError = PyErr_NewException("memory.vdomxml.loads.TypeNotFoundError", BaseException, NULL);
    if (!TypeNotFoundError)
        return NULL;
    if (PyModule_AddObject(module, "TypeNotFoundError", TypeNotFoundError))
        return NULL;

    return module;
}
