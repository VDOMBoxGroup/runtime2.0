

typedef char *Data;
typedef char *UnicodeData;  /* In Python 3, Unicode strings are UTF-8 encoded */
typedef Py_ssize_t DataSize;
typedef Py_ssize_t Length;
typedef unsigned long Hash;
typedef Py_UCS4 Character;


typedef struct BatchStruct
{
    struct BatchStruct *prev, *next;
    unsigned int counter;
}
Batch;

typedef struct
{
    Batch *list, *last;
    unsigned int counter;
    unsigned int item_size;
    unsigned int items_per_batch;
    unsigned int batch_size;
}
Stockpile;

typedef int (* StockpileIterateCallback)(void *);


typedef enum
{
    GenericElement,
    AttributeElement,
    NameAttributeElement
}
ElementType;

typedef enum
{
    GenericAttribute,
    NameAttribute
}
AttributeType;


typedef struct SubstringStruct
{
    Data data;
    DataSize size;
    // Maximum UTF-8 character size is 4 bytes.
    char buffer[4];
    struct SubstringStruct *next;
}
Substring;

typedef struct
{
    Substring *list;
    Substring *last;
    int size;
}
Substrings;

typedef struct ElementStruct
{
    struct ElementStruct *parent;
    ElementType type;
    PyObject *name;
    PyObject *attributes;
    PyObject *object;
}
Element;


typedef int (*MatchString)(Data, Data, char *);
typedef int (*IsEqualToString)(Data, Data, char *);
typedef int (*IsEqualToPythonString)(Data, Data, PyObject *);
typedef int (*PythonStringIsEqualToString)(PyObject *, char *);
typedef PyObject *(*CreatePythonString)(Data, Data);
typedef PyObject *(*CreateEmptyPythonString)(void);
typedef PyObject *(*CreatePythonStringFromSubstrings)(Substrings *);
typedef DataSize (*WriteCharacter)(Data, Character);


struct CellStruct;

typedef struct
{
    int is_unicode;

    Data data;
    Data stop;

    int line;
    int column;

    State state, return_state;
    Character character;
    Symbol symbol;
    struct CellStruct *cell;

    Element *element;
    PyObject *result;

    MatchString match_string;
    IsEqualToString is_equal_to_string;
    IsEqualToPythonString is_equal_to_python_string;
    PythonStringIsEqualToString python_string_is_equal_to_string;
    CreatePythonString create_python_string;
    CreatePythonStringFromSubstrings create_python_string_from_substrings;
    CreateEmptyPythonString create_empty_python_string;
    WriteCharacter write_character;

    struct
    {
        Stockpile elements;
        Stockpile substrings;
        Stockpile references;
    }
    stockpiles;

    Data mark;
    Substrings substrings;

    unsigned int length;
    char buffer[BUFFER_LENGTH];

    struct
    {
        AttributeType type;
        PyObject *name;
    }
    attribute;
    struct
    {
        Hash hash;
        Length length;
        Character character;
    }
    entity;
}
Parse;

typedef State (*Callback)(Parse *);

typedef struct CellStruct
{
    State state;
    Callback callback;
    State return_state;
}
Cell;
