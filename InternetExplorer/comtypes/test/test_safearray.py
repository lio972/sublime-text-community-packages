import unittest
from decimal import Decimal
import datetime
from ctypes import *
from ctypes.wintypes import BOOL
from comtypes.test.find_memleak import find_memleak
from comtypes import BSTR, IUnknown

from comtypes.automation import VARIANT, IDispatch, VT_ARRAY, VT_VARIANT, \
     VT_I4, VT_R4, VT_R8, VT_BSTR, VARIANT_BOOL, VT_DATE, VT_CY
from comtypes.automation import _midlSAFEARRAY

from comtypes._safearray import SafeArrayGetVartype

class VariantTestCase(unittest.TestCase):
    def test_VARIANT_array(self):
        v = VARIANT()
        v.value = ((1, 2, 3), ("foo", "bar", None))
        self.failUnlessEqual(v.vt, VT_ARRAY | VT_VARIANT)
        self.failUnlessEqual(v.value, ((1, 2, 3), ("foo", "bar", None)))

        def func():
            v = VARIANT((1, 2, 3), ("foo", "bar", None))

        bytes = find_memleak(func)
        self.failIf(bytes, "Leaks %d bytes" % bytes)


    def test_object(self):
        self.assertRaises(TypeError, lambda: VARIANT(object()))

    def test_double_array(self):
        import array
        a = array.array("d", (3.14, 2.78))
        v = VARIANT(a)
        self.failUnlessEqual(v.vt, VT_ARRAY | VT_R8)
        self.failUnlessEqual(tuple(a.tolist()), v.value)

        def func():
            v = VARIANT(array.array("d", (3.14, 2.78)))

        bytes = find_memleak(func)
        self.failIf(bytes, "Leaks %d bytes" % bytes)


    def test_float_array(self):
        import array
        a = array.array("f", (3.14, 2.78))
        v = VARIANT(a)
        self.failUnlessEqual(v.vt, VT_ARRAY | VT_R4)
        self.failUnlessEqual(tuple(a.tolist()), v.value)

    def test_2dim_array(self):
        data = ((1, 2, 3, 4),
                (5, 6, 7, 8),
                (9, 10, 11, 12))
        v = VARIANT(data)
        self.failUnlessEqual(v.value, data)

    def test_datetime(self):
        now = datetime.datetime.now()

        v = VARIANT()
        v.value = now
        self.failUnlessEqual(v.value, now)
        self.failUnlessEqual(v.vt, VT_DATE)

    def test_decimal(self):
        pi = Decimal("3.13")

        v = VARIANT()
        v.value = pi
        self.failUnlessEqual(v.vt, VT_CY)
        self.failUnlessEqual(v.value, pi)

    def test_UDT(self):
        from comtypes.gen.TestComServerLib import MYCOLOR
        v = VARIANT(MYCOLOR(red=1.0, green=2.0, blue=3.0))
        value = v.value
        self.failUnlessEqual((1.0, 2.0, 3.0),
                             (value.red, value.green, value.blue))

        def func():
            v = VARIANT(MYCOLOR(red=1.0, green=2.0, blue=3.0))
            return v.value

        bytes = find_memleak(func)
        self.failIf(bytes, "Leaks %d bytes" % bytes)


class SafeArrayTestCase(unittest.TestCase):

    def test_equality(self):
        a = _midlSAFEARRAY(c_long)
        b = _midlSAFEARRAY(c_long)
        self.failUnless(a is b)

        c = _midlSAFEARRAY(BSTR)
        d = _midlSAFEARRAY(BSTR)
        self.failUnless(c is d)

        self.failIfEqual(a, c)

        # XXX remove:
        self.failUnlessEqual((a._itemtype_, a._vartype_),
                             (c_long, VT_I4))
        self.failUnlessEqual((c._itemtype_, c._vartype_),
                             (BSTR, VT_BSTR))

    def test_VT_BSTR(self):
        t = _midlSAFEARRAY(BSTR)

        sa = t.from_param(["a" ,"b", "c"])
        self.failUnlessEqual(sa[0], ("a", "b", "c"))
        self.failUnlessEqual(SafeArrayGetVartype(sa), VT_BSTR)

    def test_VT_BSTR_leaks(self):
        sb = _midlSAFEARRAY(BSTR)
        def doit():
            sb.from_param(["foo", "bar"])

        bytes = find_memleak(doit)
        self.failIf(bytes, "Leaks %d bytes" % bytes)

    def test_VT_I4_leaks(self):
        sa = _midlSAFEARRAY(c_long)
        def doit():
            sa.from_param([1, 2, 3, 4, 5, 6])

        bytes = find_memleak(doit)
        self.failIf(bytes, "Leaks %d bytes" % bytes)

    def test_VT_I4(self):
        t = _midlSAFEARRAY(c_long)

        sa = t.from_param([11, 22, 33])

        self.failUnlessEqual(sa[0], (11, 22, 33))

        self.failUnlessEqual(SafeArrayGetVartype(sa), VT_I4)

        # TypeError: len() of unsized object
        self.assertRaises(TypeError, lambda: t.from_param(object()))

    def test_VT_VARIANT(self):
        t = _midlSAFEARRAY(VARIANT)

        now = datetime.datetime.now()
        sa = t.from_param([11, "22", None, True, now, Decimal("3.14")])
        self.failUnlessEqual(sa[0], (11, "22", None, True, now, Decimal("3.14")))

        self.failUnlessEqual(SafeArrayGetVartype(sa), VT_VARIANT)

    def test_VT_BOOL(self):
        t = _midlSAFEARRAY(VARIANT_BOOL)

        sa = t.from_param([True, False, True, False])
        self.failUnlessEqual(sa[0], (True, False, True, False))

    # not yet implemented 
##    def test_VT_UNKNOWN(self):
##        a = _midlSAFEARRAY(POINTER(IUnknown))
##        t = _midlSAFEARRAY(POINTER(IUnknown))
##        self.failUnless(a is t)

##        from comtypes.typeinfo import CreateTypeLib
##        punk = CreateTypeLib("spam").QueryInterface(IUnknown) # will never be saved to disk
##        refcnt_before = punk.AddRef(), punk.Release()
##        t.from_param([punk, punk, punk])
##        import gc; gc.collect(); gc.collect()
##        refcnt_after = punk.AddRef(), punk.Release()
##        # This test leaks COM refcounts of the punk object.  Don't know why.
##        ##self.failUnlessEqual(refcnt_before, refcnt_after)

    def test_UDT(self):
        from comtypes.gen.TestComServerLib import MYCOLOR

        t = _midlSAFEARRAY(MYCOLOR)
        self.failUnless(t is _midlSAFEARRAY(MYCOLOR))

        sa = t.from_param([MYCOLOR(0, 0, 0), MYCOLOR(1, 2, 3)])

        self.failUnlessEqual([(x.red, x.green, x.blue) for x in sa[0]],
                             [(0.0, 0.0, 0.0), (1.0, 2.0, 3.0)])

        def doit():
            t.from_param([MYCOLOR(0, 0, 0), MYCOLOR(1, 2, 3)])
        bytes = find_memleak(doit)
        self.failIf(bytes, "Leaks %d bytes" % bytes)

try:
    import pythoncom
except ImportError:
    # pywin32 not installed...
    pass
else:
    # pywin32 is available.  The pythoncom dll contains two handy
    # exported functions that allow to create a VARIANT from a Python
    # object, also a function that unpacks a VARIANT into a Python
    # object.
    #
    # This allows us to create und unpack SAFEARRAY instances
    # contained in VARIANTs, and check for consistency with the
    # comtypes code.
    
    _dll = PyDLL(pythoncom.__file__)

    # c:/sf/pywin32/com/win32com/src/oleargs.cpp 213
    # PyObject *PyCom_PyObjectFromVariant(const VARIANT *var)
    unpack = _dll.PyCom_PyObjectFromVariant
    unpack.restype = py_object
    unpack.argtypes = POINTER(VARIANT),

    # c:/sf/pywin32/com/win32com/src/oleargs.cpp 54
    # BOOL PyCom_VariantFromPyObject(PyObject *obj, VARIANT *var)
    _pack = _dll.PyCom_VariantFromPyObject
    _pack.argtypes = py_object, POINTER(VARIANT)
    _pack.restype = BOOL
    def pack(obj):
        var = VARIANT()
        result = _pack(obj, byref(var))
        return var

    class PyWinTest(unittest.TestCase):
        def test_1dim(self):
            data = (1, 2, 3)
            variant = pack(data)
            self.failUnlessEqual(variant.value, data)
            self.failUnlessEqual(unpack(variant), data)

        def test_2dim(self):
            data = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
            variant = pack(data)
            self.failUnlessEqual(variant.value, data)
            self.failUnlessEqual(unpack(variant), data)

        def test_3dim(self):
            data = ( ( (1, 2), (3, 4), (5, 6) ),
                     ( (7, 8), (9, 10), (11, 12) ) )
            variant = pack(data)
            self.failUnlessEqual(variant.value, data)
            self.failUnlessEqual(unpack(variant), data)

        def test_4dim(self):
            data = ( ( ( ( 1,  2), ( 3,  4) ),
                       ( ( 5,  6), ( 7,  8) ) ),
                     ( ( ( 9, 10), (11, 12) ),
                       ( (13, 14), (15, 16) ) ) )
            variant = pack(data)
            self.failUnlessEqual(variant.value, data)
            self.failUnlessEqual(unpack(variant), data)

if __name__ == "__main__":
    unittest.main()
