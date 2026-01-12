
#define IS_HIGH_SURROGATE(value) (0xD800 <= value && value <= 0xDBFF)
#define IS_LOW_SURROGATE(value) (0xDC00 <= value && value <= 0xDFFF)

#define JOIN_SURROGATES(high, low) \
    (0x10000 + ((((Character)(high) & 0x03FF) << 10) | ((Character)(low) & 0x03FF)))


#define STRING_NEXT(data, stop) (Character)(*(data)++)

/* UTF-8 decoder for Python 3 - decode next UTF-8 character */
static inline Character unicode_next_utf8(Data *data_ptr, Data stop)
{
    unsigned char *p = (unsigned char *)*data_ptr;
    if (p >= (unsigned char *)stop)
        return 0;

    if (*p < 0x80) {
        (*data_ptr)++;
        return (Character)*p;
    } else if (*p < 0xE0) {
        if (p + 1 >= (unsigned char *)stop) return 0;
        Character c = ((Character)(p[0] & 0x1F) << 6) | (p[1] & 0x3F);
        *data_ptr += 2;
        return c;
    } else if (*p < 0xF0) {
        if (p + 2 >= (unsigned char *)stop) return 0;
        Character c = ((Character)(p[0] & 0x0F) << 12) | ((Character)(p[1] & 0x3F) << 6) | (p[2] & 0x3F);
        *data_ptr += 3;
        return c;
    } else {
        if (p + 3 >= (unsigned char *)stop) return 0;
        Character c = ((Character)(p[0] & 0x07) << 18) | ((Character)(p[1] & 0x3F) << 12) | ((Character)(p[2] & 0x3F) << 6) | (p[3] & 0x3F);
        *data_ptr += 4;
        return c;
    }
}

#define UNICODE_NEXT(data, stop) unicode_next_utf8(&(data), stop)


static int
string_match_string(Data data, Data stop, char *value)
{
    for (;;)
    {
        if (*value == '\0')
            return data == stop;
        if (data == stop || tolower(*data++) != *value++)
            return 0;
    };
};

static int
unicode_match_string(UnicodeData data, UnicodeData stop, char *value)
{
    for (;;)
    {
        if (*value == '\0')
            return data == stop;
        if (data == stop || tolower((char)(*data++)) != *value++)
            return 0;
    };
};


static int
string_is_equal_to_string(Data data, Data stop, char *value)
{
    for (;;)
    {
        if (*value == '\0')
            return data == stop;
        if (data == stop || *data++ != *value++)
            return 0;
    };
};

static int
unicode_is_equal_to_string(UnicodeData data, UnicodeData stop, char *value)
{
    for (;;)
    {
        if (*value == '\0')
            return data == stop;
        if (data == stop || (char)(*data++) != *value++)
            return 0;
    };
};


static int
string_is_equal_to_python_string(Data data, Data stop, PyObject *object)
{
    const char *object_data;
    Py_ssize_t object_size;
    if (PyBytes_CheckExact(object)) {
        object_data = PyBytes_AS_STRING(object);
        object_size = PyBytes_GET_SIZE(object);
    } else if (PyUnicode_CheckExact(object)) {
        object_data = PyUnicode_AsUTF8AndSize(object, &object_size);
        if (!object_data)
            return 0;
    } else {
        return 0;
    }
    return ((stop - data) == object_size) && !memcmp(data, object_data, object_size);
};

static int
unicode_is_equal_to_python_string(Data data, Data stop, PyObject *object)
{
    const char *object_data;
    Py_ssize_t object_size;
    if (PyBytes_CheckExact(object)) {
        object_data = PyBytes_AS_STRING(object);
        object_size = PyBytes_GET_SIZE(object);
    } else if (PyUnicode_CheckExact(object)) {
        object_data = PyUnicode_AsUTF8AndSize(object, &object_size);
        if (!object_data)
            return 0;
    } else {
        return 0;
    }
    return ((stop - data) == object_size) && !memcmp(data, object_data, object_size);
};


static int
string_python_string_is_equal_to_string(PyObject *object, char *value)
{
    const char *data;
    Py_ssize_t size;
    if (PyBytes_CheckExact(object)) {
        data = PyBytes_AS_STRING(object);
        size = PyBytes_GET_SIZE(object);
    } else if (PyUnicode_CheckExact(object)) {
        data = PyUnicode_AsUTF8AndSize(object, &size);
        if (!data)
            return 0;
    } else {
        return 0;
    }
    return string_is_equal_to_string((Data)data, (Data)(data + size), value);
};

static int
unicode_python_string_is_equal_to_string(PyObject *object, char *value)
{
    const char *data;
    Py_ssize_t size;
    if (PyBytes_CheckExact(object)) {
        data = PyBytes_AS_STRING(object);
        size = PyBytes_GET_SIZE(object);
    } else if (PyUnicode_CheckExact(object)) {
        data = PyUnicode_AsUTF8AndSize(object, &size);
        if (!data)
            return 0;
    } else {
        return 0;
    }
    return unicode_is_equal_to_string((UnicodeData)data, (UnicodeData)(data + size), value);
};


static PyObject *
string_create_python_string(Data data, Data stop)
{
    return PyBytes_FromStringAndSize((char *)data, stop - data);
}

static PyObject *
unicode_create_python_string(Data data, Data stop)
{
    /* In Python 3, data is UTF-8 encoded bytes */
    return PyUnicode_FromStringAndSize((char *)data, stop - data);
}


static PyObject *
string_create_python_string_from_substrings(Substrings *substrings)
{
    PyObject *object;
    Substring *substring;
    Data data;

    object = PyBytes_FromStringAndSize(NULL, substrings->size);
    if (!object)
        return NULL;

    data = (Data)PyBytes_AS_STRING(object);
    for (substring = substrings->list; substring; substring = substring->next)
    {
        Py_MEMCPY(data, substring->data, substring->size);
        data += substring->size;
    }

    return object;
}

static PyObject *
unicode_create_python_string_from_substrings(Substrings *substrings)
{
    PyObject *object;
    Substring *substring;
    char *buffer;
    char *data;

    /* Allocate buffer for UTF-8 string */
    buffer = (char *)PyMem_Malloc(substrings->size);
    if (!buffer)
        return PyErr_NoMemory();

    data = buffer;
    for (substring = substrings->list; substring; substring = substring->next)
    {
        Py_MEMCPY(data, substring->data, substring->size);
        data += substring->size;
    }

    /* Create Unicode object from UTF-8 string */
    object = PyUnicode_FromStringAndSize(buffer, substrings->size);
    PyMem_Free(buffer);

    return object;
}


static PyObject *
string_create_empty_python_string(void)
{
    return PyBytes_FromStringAndSize("", 0);
}

static PyObject *
unicode_create_empty_python_string(void)
{
    return PyUnicode_FromString("");
}


static DataSize
string_write_character(Data data, Character character)
{
    if (character > 0x7F)
    {
        PyErr_Format(WrongCharacterError, "Wrong character '?' (0x%x)", character);
        return 0;
    }

    *((char *)data) = (char)character;
    return 1;
}

static DataSize
unicode_write_character(Data data, Character character)
{
    /* In Python 3, encode character to UTF-8 */
    if (character <= 0x7F) {
        *((char *)data) = (char)character;
        return 1;
    } else if (character <= 0x7FF) {
        *((char *)data) = (char)(0xC0 | (character >> 6));
        *((char *)(data + 1)) = (char)(0x80 | (character & 0x3F));
        return 2;
    } else if (character <= 0xFFFF) {
        *((char *)data) = (char)(0xE0 | (character >> 12));
        *((char *)(data + 1)) = (char)(0x80 | ((character >> 6) & 0x3F));
        *((char *)(data + 2)) = (char)(0x80 | (character & 0x3F));
        return 3;
    } else if (character <= 0x10FFFF) {
        *((char *)data) = (char)(0xF0 | (character >> 18));
        *((char *)(data + 1)) = (char)(0x80 | ((character >> 12) & 0x3F));
        *((char *)(data + 2)) = (char)(0x80 | ((character >> 6) & 0x3F));
        *((char *)(data + 3)) = (char)(0x80 | (character & 0x3F));
        return 4;
    } else {
        PyErr_Format(WrongCharacterError, "Wrong character '?' (0x%x)", character);
        return 0;
    }
}
