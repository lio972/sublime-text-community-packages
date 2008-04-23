import unittest
from comtypes import COMError
from comtypes.client import CreateObject, GetModule
from comtypes.server.register import register, unregister
from comtypes.test.testserver import Server

GetModule(r".\TestServer.tlb")
from comtypes.gen import TestServerLib


# Register the COM object as soon as this module is imported.
register(Server)

# Unregister the COM object on Python shutdown.
import atexit
atexit.register(unregister, Server)

################################################################

class ServerTest(unittest.TestCase):

    def test_name(self):
        obj = CreateObject("TestServerLib.TestServer")

        self.failUnlessEqual(obj.name, "<undefined>")
        obj.name = "Silly"
        self.failUnlessEqual(obj.name, "Silly")
        obj.SetName("foo")
        self.failUnlessEqual(obj.name, "foo")

        # case insensitive methods
        obj.sETnAME("bar")
        self.failUnlessEqual(obj.name, "bar")

        self.assertRaises(AttributeError, lambda: obj.NonExistingName)

        # properties only case insensitive if implemented as Python property
        obj.NAME = "spam"
        self.failUnlessEqual(obj.name, "spam")
        self.failUnlessEqual(obj.NAME, "spam")
        self.failUnlessEqual(obj.nAMe, "spam")

    def test_eval(self):
        obj = CreateObject(TestServerLib.TestServer)
        self.failUnlessEqual(obj.eval("32"), 32)
        self.failUnlessEqual(obj.eval("[]"), ())
        self.failUnlessEqual(obj.eval("()"), ())
        self.failUnlessEqual(obj.eval("(1, False, 'blah')"), (1, False, "blah"))


    def test_exec(self):
        obj = CreateObject(TestServerLib.TestServer)
        self.assertRaises(COMError, lambda: obj.Exec("raise WindowsError"))
        self.assertRaises(COMError, lambda: obj.Exec("raise WindowsError(3)"))
        self.assertRaises(COMError, lambda: obj.Exec("raise WindowsError(3, 'foo')"))
        self.assertRaises(COMError,
                          lambda: obj.Exec("from comtypes import COMError; raise COMError(3, 'foo', ())"))
##        self.assertRaises(COMError,
##                          obj.Exec("from comtypes import COMError; raise COMError(None, None, None)"))

if __name__ == "__main__":
    unittest.main()
