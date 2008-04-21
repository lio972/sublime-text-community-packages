import unittest, os
from ctypes import *
from comtypes import BSTR
from comtypes.test import requires
from comtypes.client import CreateObject

##requires("memleaks")

requires("IONTOF.ChemInfoOptions")

from comtypes.test.find_memleak import find_memleak

class Test(unittest.TestCase):
    def test_1(self):
        cio = CreateObject("IONTOF.ChemInfoOptions")
        cio.ElementFilter = "CHCl"

        self.failUnlessEqual(cio.ElementFilter, "CHCl")

        pb = pointer(BSTR())
        cio._IChemInfoOptions__com__get_ElementFilter(pb)

        self.failUnlessEqual(pb[0], "CHCl")
        # Create and destroy a new long BSTR
        BSTR("x" * 256)
        self.failUnlessEqual(pb[0], "CHCl")

        # Create and destroy a new short BSTR
        BSTR("x")
        self.failUnlessEqual(pb[0], "CHCl")

    def test_2(self):
        cio = CreateObject("IONTOF.ChemInfoOptions")
        cio.ElementFilter = "CHCl"

        self.failUnlessEqual(cio.ElementFilter, "CHCl")

        b = BSTR()
        cio._IChemInfoOptions__com__get_ElementFilter(byref(b))

        self.failUnlessEqual(b.value, "CHCl")

        # Create and destroy a new long BSTR
        BSTR("y" * 256)
        self.failUnlessEqual(b.value, "CHCl")

        # Create and destroy a new short BSTR
        BSTR("y")
        self.failUnlessEqual(b.value, "CHCl")

if __name__ == "__main__":
    unittest.main()
