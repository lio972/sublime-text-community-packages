# To disable OLE caching of BStrings, set the 'OANODEBUG' environment
# variable to '1' before running the app
##import logging
##logging.basicConfig(level=logging.ERROR)

from ctypes import *
from comtypes import IUnknown, GUID, STDMETHOD, COMObject

from ctypes.wintypes import BOOL

class IMallocSpy(IUnknown):
    _iid_ = GUID("{0000001D-0000-0000-C000-000000000046}")
    _methods_ = [
        STDMETHOD(c_ulong, "PreAlloc", [c_ulong]),
        STDMETHOD(c_voidp, "PostAlloc", [c_voidp]),
        STDMETHOD(c_voidp, "PreFree", [c_voidp, BOOL]),
        STDMETHOD(None, "PostFree", [BOOL]),
        STDMETHOD(c_ulong, "PreRealloc", [c_voidp, c_ulong, POINTER(c_voidp), BOOL]),
        STDMETHOD(c_voidp, "PostRealloc", [c_voidp, BOOL]),
        STDMETHOD(c_voidp, "PreGetSize", [c_voidp, BOOL]),
        STDMETHOD(c_ulong, "PostGetSize", [c_ulong, BOOL]),
        STDMETHOD(c_voidp, "PreDidAlloc", [c_voidp, BOOL]),
        STDMETHOD(c_int, "PostDidAlloc", [c_voidp, BOOL, c_int]),
        STDMETHOD(None, "PreHeapMinimize", []),
        STDMETHOD(None, "PostHeapMinimize", [])]

class MallocSpy(COMObject):
    _com_interfaces_ = [IMallocSpy]

    def __init__(self):
        self.blocks = {}
        self.freed = {}
        super(MallocSpy, self).__init__()

##    def AddRef(self, this):
##        return 2

##    def Release(self, this):
##        return 1

    # keep track of allocated blocks and size
    def PreAlloc(self, this, cbRequest):
##        print "ALLOC", cbRequest
        self.cbRequest = cbRequest
        return cbRequest

    def PostAlloc(self, this, pActual):
        self.blocks[pActual] = self.cbRequest
        del self.cbRequest
##        print "PostAlloc %X" % pActual
        return pActual

    def PreFree(self, this, pRequest, fSpyed):
##        print "PreFree %s %X" % (fSpyed, pRequest), pRequest in self.blocks
        if pRequest in self.blocks:
            self.freed[pRequest] = None
            del self.blocks[pRequest]
        else:
            size = c_int.from_address(pRequest)
            print "\tDBF?", (size, hex(pRequest), wstring_at(pRequest+4))
            print "\t\t", pRequest in self.freed, fSpyed
##            import pdb
##            pdb.set_trace()
##            x = (c_char * 32)()
##            memmove(x, pRequest, 32)
##            from binascii import hexlify
##            print hexlify(buffer(x))
##            print x[:]
        return pRequest

    def PostFree(self, this, fSpyed):
        pass

    def PreGetSize(self, this, pRequest, fSpyed):
        return pRequest

    def PostGetSize(self, this, cbActual, fSpyed):
        return cbActual

    def PreRealloc(self, this, pRequest, cbRequest, ppNewRequest, fSpyed):
        return cbRequest

    def PostRealloc(self, this, pActual, fSpyed):
        return pActual

    def PreDidAlloc(self, this, pRequest, fSpyed):
        return pRequest

    def PostDidAlloc(self, this, pRequest, fSpyed, fActual):
        return fActual

    def PreHeapMinimize(self, this):
        pass

    def PostHeapMinimize(self, this):
        pass

    ################

    def active_blocks(self):
        return self.blocks

    def register(self):
        return oledll.ole32.CoRegisterMallocSpy(self._com_pointers_.values()[0])

    def revoke(self, warn=1):
        self.release_all(warn=warn)
        return windll.ole32.CoRevokeMallocSpy()

    def release_all(self, warn=1):
        active = self.active_blocks()
        if active and warn:
##            print "ACTIVE", self.blocks
            print "%d Allocated Memory Blocks:" % len(active)
##            for block, size in active.items():
##                print "\t%d bytes at %08X" % (size, block)

if __name__ == "__main__":
    ##from comtypes import BSTR
    ##BSTR("alibaba")
    _m = MallocSpy()
    print _m.register()
    oledll.ole32.CoInitialize(None)
    for i in range(32):
        a = oledll.oleaut32.SysAllocString(u"alskjd alskjd")
        oledll.oleaut32.SysFreeString(a)
        oledll.oleaut32.SysFreeString(a)
        del a
    print "REVOKE", _m.revoke(False)
    del _m
    import gc
    gc.collect()
    oledll.ole32.CoUninitialize()
