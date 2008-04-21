import sys
import logging
logging.basicConfig(level=logging.WARNING)

if not hasattr(sys, "frozen"):
    from comtypes.client import GetModule
    # ../gen/TestServerLib.py
    # ../gen/_77026E1C_AC5D_4693_9EF9_CA9722476F6A_0_1_0.py
    GetModule(r".\TestServer.tlb")

from comtypes import CLSCTX_SERVER
from comtypes.gen import TestServerLib
from comtypes.server.register import UseCommandLine

class Server(TestServerLib.TestServer):
    _reg_progid_ = "TestServerLib.TestServer.1"
    _reg_novers_progid_ = "TestServerLib.TestServer"
    _reg_clsctx_ = CLSCTX_SERVER

    def ITestServer_eval(self, text):
        return eval(text)

    def ITestServer_exec(self, text):
        exec(text)

    _name = "<undefined>"
    def _set(self, name):
        self._name = name
    def _get(self):
        return self._name
    name = property(_get, _set)

    def SetName(self, value):
        self.name = value

if __name__ == "__main__":
    UseCommandLine(Server)
