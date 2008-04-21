import unittest
from ctypes import *
from comtypes import IUnknown
from comtypes.test.find_memleak import find_memleak

from _ctypes import CopyComPointer

oledll = OleDLL("oleaut32")

def getrc(obj):
    "Return the COM reference count of a COM pointer."
    obj.AddRef()
    return obj.Release()

SYS_WIN32 = 1
def create():
    "A helper function to create a COM interface pointer."
    p = POINTER(IUnknown)()
    oledll.CreateTypeLib2(SYS_WIN32, u"foo", byref(p))
    return p

class COMTestCase(unittest.TestCase):
    # These tests demonstrates the (wrong) behaviour and explains some
    # workarounds in the code:
    
    def test_leaks(self):
        # Create a lot of COM pointers, test if they are released
        # correctly.
        bytes = find_memleak(create)
        self.failIf(bytes, "Leaks %d bytes" % bytes)

        # Inverse test: Create COM pointers, do NOT release them,
        # and make sure we have a memory leak.
        def doit():
            create().AddRef()
        bytes = find_memleak(doit)
        self.failIf(bytes <= 0)

    def test_CopyComPointer(self):
        # 1. Storing a COM pointer in an array should of course
        # increase the refcount - it does not automatically.
        #
        # 2. Similarly retrieving a COM pointer from an array should
        # increase the refcount - it does not automatically.
        #
        # 3. Finally destroying the array should call decrease the
        # refcount of the contained items - it does not automatically.
        #
        # The workaround used in comtype for issue 1) is to use the
        # CopyComPointer function to store a COM object in an array or
        # a pointer - CopyComPointer calls AddRef() before storing.
        # One problem remains: CopyComPointer does not call Release()
        # on the destination, so there is a refcount lost if a COM
        # pointer is overwritten.  See code in comtypes.automation
        # where IUnknown, IDispatch, or IRecordInfo pointers are
        # stored in VARIANT.
        #
        # To fix issue 2) one must call AddRef() manually if a COM
        # pointer is retrieved from an array or a pointer.  Again, see
        # the VARIANT code in comtypes.automation.
        
        # This test demonstrates this behaviour.

        array = (POINTER(IUnknown) * 32)()

        ptr = create()
        self.assertEqual(getrc(ptr), 1)

        # AddRef() called by CopyComPtr:
        CopyComPointer(ptr, array)
        self.assertEqual(getrc(ptr), 2)

        # AddRef() called by CopyComPtr, but original contents
        # overwritten:
        CopyComPointer(ptr, array)
        self.assertEqual(getrc(ptr), 3)

        # Overwrite contents (loosing a refcount):
        array[0] = None
        self.assertEqual(getrc(ptr), 3)

        # AddRef() called by CopyComPtr:
        CopyComPointer(ptr, array)
        self.assertEqual(getrc(ptr), 4)

        ptr.Release(); ptr.Release(); ptr.Release()

    def test_ccp(self):
        array = (POINTER(IUnknown) * 32)()

        ptr = create()
        self.assertEqual(getrc(ptr), 1)

        ccp(ptr, array)
        self.assertEqual(getrc(ptr), 2)

        ccp(ptr, array)
        self.assertEqual(getrc(ptr), 2)

        ccp(None, array)
        self.assertEqual(getrc(ptr), 1)

        ccp(None, array)
        self.assertEqual(getrc(ptr), 1)

        for i in range(32):
            ccp(ptr, array, i)
        self.assertEqual(getrc(ptr), 1+32)

        for i in range(32):
            ccp(ptr, array, i)
        self.assertEqual(getrc(ptr), 1+32)

        for i in range(32):
            ccp(None, array, i)
        self.assertEqual(getrc(ptr), 1)

        for i in range(32):
            ccp(ptr, array, i)
        self.assertEqual(getrc(ptr), 1+32)

##        # To delete the array we have to release all refcounts before
##        # Three different ways to free the array items.
##        for i in range(32):
##            ccp(None, array, i)

##        for i in range(32):
##            array[i]

        # Is there something wrong in the way ctypes iterates over an
        # array???
        # Why doesn't this free the last one?
##        for x in array:
##            pass
##        del x

        array[:]

        self.assertEqual(getrc(ptr), 1)

##    def test_pointer(self):
##        ppunk = pointer(POINTER(IUnknown)())
##        self.failUnlessEqual(bool(ppunk[0]), False)

##        ptr = create()
##        self.assertEqual(getrc(ptr), 1)

##        ccp(ptr, ppunk)
##        self.assertEqual(getrc(ptr), 3)

##        ccp(ptr, ppunk)
##        self.assertEqual(getrc(ptr), 4)
        
##        ccp(ptr, ppunk)
##        self.assertEqual(getrc(ptr), 5)
        

################################################################

def ccp(src, dest, index=0):
    "A better CopyComPointer function"
    # release destination, if needed. This code retrieves the
    # current index without AddRef(), and when the object goes
    # out of scope Release() is called.
    dest[index]
    # store it:
    dest[index] = src
    # addref p, if needed:
    if src:
        src.AddRef()

################################################################

if __name__ == "__main__":
    unittest.main()

