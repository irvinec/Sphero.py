#include <Python.h>
//#include <winrt/Windows.Devices.Bluetooth.h>
#include <winrt/base.h>

// Link to umbrella lib.
#pragma comment(lib, "windowsapp")

using namespace winrt;


// winble.WinBleAdapter definition

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
} WinBleAdapter_Object;

int WinBleAdapter_init(PyObject* self, PyObject* args, PyObject* kwds)
{
    init_apartment();
    return 0;
}

PyObject* WinBleAdapter_start(PyObject* self)
{
    Py_RETURN_NOTIMPLEMENTED;
    //Py_RETURN_NONE;
}

PyObject* WinBleAdapter_scan(PyObject* self)
{
    // BUG: TypeError: string indices must be integers
    // when calling device['name']
    // Need a list of dictionaries...
    PyObject* bogusDevice = PyDict_New();
    PyDict_SetItemString(bogusDevice, "name", PyUnicode_FromString("SK-Bogus"));
    PyDict_SetItemString(bogusDevice, "address", PyUnicode_FromString("FF:FF:FF:FF:FF:FF"));
    PyObject* devices = PyList_New(1);
    Py_INCREF(bogusDevice);
    PyList_Append(devices, bogusDevice);
    Py_INCREF(devices);
    //return devices;
    Py_RETURN_NOTIMPLEMENTED;
}

PyMethodDef WinBleAdapter_methods[] = {
    { "start", (PyCFunction) WinBleAdapter_start, METH_NOARGS, "Starts the adapter." },
    { "scan", (PyCFunction) WinBleAdapter_scan, METH_NOARGS, "Starts the adapter." },
    {NULL, NULL, 0, NULL}
};

static PyTypeObject WinBleAdapter_Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "winble.WinBleAdapter", // tp_name
    sizeof(WinBleAdapter_Object),   // tp_basicsize
    0,  // tp_itemsize
    NULL,   // tp_dealloc
    NULL,   // tp_print
    NULL,   // tp_getattr
    NULL,   // tp_setattr
    NULL,   // tp_as_async
    NULL,   // tp_repr
    NULL,   // tp_as_number
    NULL,   // tp_as_sequence
    NULL,   // tp_as_mapping
    NULL,   // tp_hash
    NULL,   // tp_call
    NULL,   // tp_str
    PyObject_GenericGetAttr,   // tp_getattro
    PyObject_GenericSetAttr,   // tp_setattro
    NULL,   // tp_as_buffer
    Py_TPFLAGS_DEFAULT, // tp_flags
    "BLE adapter that uses winrt BLE api.", // tp_doc
    NULL,   // tp_traverse
    NULL,   // tp_clear
    NULL,   // tp_richcompare
    NULL,   // tp_weaklistoffset
    NULL,   // tp_iter
    NULL,   // tp_iternext
    WinBleAdapter_methods,  // tp_methods
    NULL,   // tp_members
    NULL,   // tp_getset
    NULL,   // tp_base
    NULL,   // tp_dict
    NULL,   // tp_descr_get
    NULL,   // tp_descr_set
    NULL,   // tp_dictoffset
    WinBleAdapter_init, // tp_init
    NULL,   // tp_alloc
    PyType_GenericNew,  // tp_new
    NULL,   // tp_free /* Low-level free-memory routine */
    NULL,   // tp_is_gc /* For PyObject_IS_GC */
    NULL,   // tp_bases
    NULL,   // tp_mro /* method resolution order */
    NULL,   // tp_cache
    NULL,   // tp_subclasses
    NULL,   // tp_weaklist
    NULL,   // tp_del
    0,  // tp_version_tag
    NULL, // tp_finalize
};

// Define the winble module
static PyModuleDef winble_Module = {
    PyModuleDef_HEAD_INIT,
    "winble", // m_name
    "winble module.", // m_doc
    -1, // m_size
    NULL, // m_methods
    NULL, // m_slots
    NULL, // m_traverse
    NULL, // m_clear
    NULL, // m_free
};

PyMODINIT_FUNC
PyInit_winble(void)
{
    PyObject* module;
    if (PyType_Ready(&WinBleAdapter_Type) < 0)
        return NULL;

    module = PyModule_Create(&winble_Module);
    if (module == NULL)
        return NULL;

    Py_INCREF(&WinBleAdapter_Type);
    PyModule_AddObject(module, "WinBleAdapter", (PyObject*) &WinBleAdapter_Type);
    return module;
}
