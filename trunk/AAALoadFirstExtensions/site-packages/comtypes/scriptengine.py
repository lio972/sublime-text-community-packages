# scripting engine.
import sys

from comtypes.hresult import *
from comtypes import COMObject, IUnknown, GUID, HRESULT, COMError, COINIT_MULTITHREADED
from comtypes.client import GetModule, CreateObject
from comtypes import activescript

################################################################
import logging
logger = logging.getLogger("engine")

# To receive script runtime errors on the script site, it is
# sufficient to implement the IActiveScriptSiteDebug interface,
# although it is NOT needed to implement ANY methods of this
# interface.

class Error(object):
    "This is simply a container for error information"
    def __init__(self, **kw):
        for name, value in kw.iteritems():
            setattr(self, name, value)

    def __str__(self):
        # can be presented to the user
        return "%s: %s, at line %s" % (self.Description, self.Text, self.Line)

    def __repr__(self):
        return "<Error(%r, %r, %r) at %x>" % (self.Description, self.Text, self.Line, id(self))

class Engine(COMObject):
    _com_interfaces_ = [activescript.IActiveScriptSite,
                        activescript.IActiveScriptSiteDebug,
                        activescript.IActiveScriptSiteInterruptPoll,
    ]

    ################################
    # IActiveScriptSiteInterruptPoll
    def IActiveScriptSiteInterruptPoll_QueryContinue(self, this):
        logger.debug("QueryContinue")
        return S_OK

    ################################
    # IActiveScriptSite
    def IActiveScriptSite_OnScriptError(self, this, scripterror):
        # Observation: The GetSourceLineText() method of the
        # scripterror instance that we receive fails for runtime
        # errors, so we don't use it.
        cookie, lineno, charpos = scripterror.GetSourcePosition()
        ei = scripterror.GetExceptionInfo()
        logger.error("OnScriptError %s", ei)
        self.Error = Error(Description = ei.bstrDescription,
                           Source = self.__code[cookie],
                           Text = ei.bstrSource,
                           Line = lineno+1)
        return S_OK

    def IActiveScriptSite_OnStateChange(self, this, state):
        self.__state = state
        logger.debug("OnStateChange %s", state)
        return S_OK

    def IActiveScriptSite_OnEnterScript(self, this):
        logger.debug("OnEnterScript")
        return S_OK
        
    def IActiveScriptSite_OnLeaveScript(self, this):
        logger.debug("OnLeaveScript")
        return S_OK

    def IActiveScriptSite_OnScriptTerminate(self, this, pvarResult, pexcepinfo):
        logger.debug("OnScriptTerminate")
        return S_OK

    def IActiveScriptSite_GetItemInfo(self, this, name, returnmask, ppiunk, ppti):
        logger.debug("GetItemInfo(%s %s)", name, returnmask)
        try:
            ob = self.__items[name]
        except KeyError:
            return E_INVALIDARG
        if hasattr(ob, "IUnknown_QueryInterface"):
            # seems we've got a COMObject instance
            from ctypes import pointer
            return ob.IUnknown_QueryInterface(None, pointer(IUnknown._iid_), ppiunk)
        if hasattr(ob, "AddRef"):
            # seems we got a COM pointer
            from ctypes import memmove, addressof, sizeof, c_void_p
            memmove(ppiunk, addressof(ob), sizeof(c_void_p))
            ob.AddRef()
            return S_OK
        return E_FAIL
        

    def __init__(self, language):
        super(Engine, self).__init__()
        engine = self.__engine = CreateObject(language, interface=activescript.IActiveScript)
        parser = self.__parser = engine.QueryInterface(activescript.IActiveScriptParse)
        engine.SetScriptSite(self)
        parser.InitNew()

        self.__code = []
        self.__items = {}

    ################################################################
    # public api

    def AddObject(self, name, object):
        self.__items[name] = object
        self.__engine.AddNamedItem(name, activescript.SCRIPTITEM_ISVISIBLE)

    def AddCode(self, code, sourcepath):
        cookie = len(self.__code)
        # so we can lookup with self.__code[cookie]
        self.__code.append(sourcepath)
        try:
            self.__parser.ParseScriptText(code,
                                          None, # itemname
                                          None, # context
                                          None, # Delimiter
                                          cookie, # SourceContextCookie
                                          0, # ulStartingLineNumber
                                          0) # dwFlags
        except COMError, (hr, text, details):
            err = getattr(self, "Error", text)
            if err is not None:
                raise COMError(hr,
                               str(err) + " in %s" % sourcepath, details)
            raise
##            if err:
##        except COMError, (hresult, text, details):
##            if hresult == DISP_E_EXCEPTION:
##                details = (excepinfo.bstrDescription, excepinfo.bstrSource,
##                           excepinfo.bstrHelpFile, excepinfo.dwHelpContext,
##                           excepinfo.scode)
##                raise COMError(hresult, text, details)
##                raise COMError, err
##            else:
##                raise
        
    def Run(self, procname, *args):
        disp = self.__engine.GetScriptDispatch(None)._comobj
        dispid = disp.GetIDsOfNames(procname)[0]
        return disp.Invoke(dispid, *args)

    def _GetNamedItem(self, name):
        return self.__engine.GetScriptDispatch(name)

    def Abort(self, info):
        # Hm, this should check the script state.
        from comtypes.automation import EXCEPINFO
        ei = EXCEPINFO()
        ei.bstrDescription = info
        ei.scode = DISP_E_EXCEPTION
        self.__engine.InterruptScriptThread(activescript.SCRIPTTHREADID_ALL,
                                            ei,
                                            activescript.SCRIPTINTERRUPT_RAISEEXCEPTION)

    def Reset(self):
        self.__engine.SetScriptState(activescript.SCRIPTSTATE_CLOSED)

##    Timeout = property()
##    Error = property()

################################################################

script = u"""
function main(a, b, c) {
    return a + b + c;
};
"""

def main():
    engine = Engine("jscript")

    try:
        engine.AddCode(script, "<sring>")
        print engine.Run(u"main", 1, "2", "3")
    except:
        print engine.Error

if __name__ == "__main__":
    main()
