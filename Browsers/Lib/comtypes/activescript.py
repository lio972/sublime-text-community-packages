# Generated from a typelib build from activscp.idl, then cleaned up
# and extended manually.

from ctypes import *
from comtypes import BSTR
from comtypes import COMMETHOD
from comtypes import DWORD
from comtypes import GUID
from comtypes import IUnknown
from comtypes import STDMETHOD
from comtypes import _GUID
from comtypes import dispid
from comtypes import helpstring
from comtypes import wireHWND
from comtypes.automation import IDispatch
from comtypes.automation import VARIANT
from comtypes.automation import tagEXCEPINFO
from comtypes.typeinfo import ITypeInfo

BOOL = c_int
WSTRING = c_wchar_p

class IActiveScriptSiteWindow(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{D10F6761-83E9-11CF-8F20-00805F2CD064}')
    _idlflags_ = []
IActiveScriptSiteWindow._methods_ = [
    COMMETHOD([], HRESULT, 'GetWindow',
              ( ['out'], POINTER(wireHWND), 'phwnd' )),
    COMMETHOD([], HRESULT, 'EnableModeless',
              ( ['in'], c_int, 'fEnable' )),
]
class IActiveScriptSiteInterruptPoll(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{539698A0-CDCA-11CF-A5EB-00AA0047A063}')
    _idlflags_ = []
IActiveScriptSiteInterruptPoll._methods_ = [
    COMMETHOD([], HRESULT, 'QueryContinue'),
]
class IBindEventHandler(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{63CDBCB0-C1B1-11D0-9336-00A0C90DCAA9}')
    _idlflags_ = []
IBindEventHandler._methods_ = [
    COMMETHOD([], HRESULT, 'BindHandler',
              ( ['in'], WSTRING, 'pstrEvent' ),
              ( ['in'], POINTER(IDispatch), 'pdisp' )),
]
class IActiveScript(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{BB1A2AE1-A4F9-11CF-8F20-00805F2CD064}')
    _idlflags_ = []
class IActiveScriptSite(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DB01A1E3-A42B-11CF-8F20-00805F2CD064}')
    _idlflags_ = []

# values for enumeration 'tagSCRIPTSTATE'
SCRIPTSTATE_UNINITIALIZED = 0
SCRIPTSTATE_INITIALIZED = 5
SCRIPTSTATE_STARTED = 1
SCRIPTSTATE_CONNECTED = 2
SCRIPTSTATE_DISCONNECTED = 3
SCRIPTSTATE_CLOSED = 4
tagSCRIPTSTATE = c_int # enum

# values for enumeration 'tagSCRIPTTHREADSTATE'
SCRIPTTHREADSTATE_NOTINSCRIPT = 0
SCRIPTTHREADSTATE_RUNNING = 1
tagSCRIPTTHREADSTATE = c_int # enum
IActiveScript._methods_ = [
    COMMETHOD([], HRESULT, 'SetScriptSite',
              ( ['in'], POINTER(IActiveScriptSite), 'pass' )),
    COMMETHOD([], HRESULT, 'GetScriptSite',
              ( ['in'], POINTER(_GUID), 'riid' ),
              ( ['out'], POINTER(c_void_p), 'ppvObject' )),
    COMMETHOD([], HRESULT, 'SetScriptState',
              ( ['in'], tagSCRIPTSTATE, 'ss' )),
    COMMETHOD([], HRESULT, 'GetScriptState',
              ( ['out'], POINTER(tagSCRIPTSTATE), 'pssState' )),
    COMMETHOD([], HRESULT, 'Close'),
    COMMETHOD([], HRESULT, 'AddNamedItem',
              ( ['in'], WSTRING, 'pstrName' ),
              ( ['in'], c_ulong, 'dwFlags' )),
    COMMETHOD([], HRESULT, 'AddTypeLib',
              ( ['in'], POINTER(_GUID), 'rguidTypeLib' ),
              ( ['in'], c_ulong, 'dwMajor' ),
              ( ['in'], c_ulong, 'dwMinor' ),
              ( ['in'], c_ulong, 'dwFlags' )),
    COMMETHOD([], HRESULT, 'GetScriptDispatch',
              ( ['in'], WSTRING, 'pstrItemName' ),
              ( ['out'], POINTER(POINTER(IDispatch)), 'ppdisp' )),
    COMMETHOD([], HRESULT, 'GetCurrentScriptThreadID',
              ( ['out'], POINTER(c_ulong), 'pstidThread' )),
    COMMETHOD([], HRESULT, 'GetScriptThreadID',
              ( ['in'], c_ulong, 'dwWin32ThreadId' ),
              ( ['out'], POINTER(c_ulong), 'pstidThread' )),
    COMMETHOD([], HRESULT, 'GetScriptThreadState',
              ( ['in'], c_ulong, 'stidThread' ),
              ( ['out'], POINTER(tagSCRIPTTHREADSTATE), 'pstsState' )),
    COMMETHOD([], HRESULT, 'InterruptScriptThread',
              ( ['in'], c_ulong, 'stidThread' ),
              ( ['in'], POINTER(tagEXCEPINFO), 'pexcepinfo' ),
              ( ['in'], c_ulong, 'dwFlags' )),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IActiveScript)), 'ppscript' )),
]
class IActiveScriptParseProcedureOld(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{1CFF0050-6FDD-11D0-9328-00A0C90DCAA9}')
    _idlflags_ = []
IActiveScriptParseProcedureOld._methods_ = [
    COMMETHOD([], HRESULT, 'ParseProcedureText',
              ( ['in'], WSTRING, 'pstrCode' ),
              ( ['in'], WSTRING, 'pstrFormalParams' ),
              ( ['in'], WSTRING, 'pstrItemName' ),
              ( ['in'], POINTER(IUnknown), 'punkContext' ),
              ( ['in'], WSTRING, 'pstrDelimiter' ),
              ( ['in'], c_ulong, 'dwSourceContextCookie' ),
              ( ['in'], c_ulong, 'ulStartingLineNumber' ),
              ( ['in'], c_ulong, 'dwFlags' ),
              ( ['out'], POINTER(POINTER(IDispatch)), 'ppdisp' )),
]
class IActiveScriptError(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{EAE1BA61-A4ED-11CF-8F20-00805F2CD064}')
    _idlflags_ = []
IActiveScriptError._methods_ = [
    COMMETHOD([], HRESULT, 'GetExceptionInfo',
              ( ['out'], POINTER(tagEXCEPINFO), 'pexcepinfo' )),
    COMMETHOD([], HRESULT, 'GetSourcePosition',
              ( ['out'], POINTER(c_ulong), 'pdwSourceContext' ),
              ( ['out'], POINTER(c_ulong), 'pulLineNumber' ),
              ( ['out'], POINTER(c_int), 'plCharacterPosition' )),
    COMMETHOD([], HRESULT, 'GetSourceLineText',
              ( ['out'], POINTER(BSTR), 'pbstrSourceLine' )),
]
class IActiveScriptParseProcedure(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{AA5B6A80-B834-11D0-932F-00A0C90DCAA9}')
    _idlflags_ = []
IActiveScriptParseProcedure._methods_ = [
    COMMETHOD([], HRESULT, 'ParseProcedureText',
              ( ['in'], WSTRING, 'pstrCode' ),
              ( ['in'], WSTRING, 'pstrFormalParams' ),
              ( ['in'], WSTRING, 'pstrProcedureName' ),
              ( ['in'], WSTRING, 'pstrItemName' ),
              ( ['in'], POINTER(IUnknown), 'punkContext' ),
              ( ['in'], WSTRING, 'pstrDelimiter' ),
              ( ['in'], c_ulong, 'dwSourceContextCookie' ),
              ( ['in'], c_ulong, 'ulStartingLineNumber' ),
              ( ['in'], c_ulong, 'dwFlags' ),
              ( ['out'], POINTER(POINTER(IDispatch)), 'ppdisp' )),
]
class IActiveScriptStats(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{B8DA6310-E19B-11D0-933C-00A0C90DCAA9}')
    _idlflags_ = []
IActiveScriptStats._methods_ = [
    COMMETHOD([], HRESULT, 'GetStat',
              ( ['in'], c_ulong, 'stid' ),
              ( ['out'], POINTER(c_ulong), 'pluHi' ),
              ( ['out'], POINTER(c_ulong), 'pluLo' )),
    COMMETHOD([], HRESULT, 'GetStatEx',
              ( ['in'], POINTER(_GUID), 'guid' ),
              ( ['out'], POINTER(c_ulong), 'pluHi' ),
              ( ['out'], POINTER(c_ulong), 'pluLo' )),
    COMMETHOD([], HRESULT, 'ResetStats'),
]
class IActiveScriptParse(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{BB1A2AE2-A4F9-11CF-8F20-00805F2CD064}')
    _idlflags_ = []
IActiveScriptParse._methods_ = [
    COMMETHOD([], HRESULT, 'InitNew'),
    COMMETHOD([], HRESULT, 'AddScriptlet',
              ( ['in'], WSTRING, 'pstrDefaultName' ),
              ( ['in'], WSTRING, 'pstrCode' ),
              ( ['in'], WSTRING, 'pstrItemName' ),
              ( ['in'], WSTRING, 'pstrSubItemName' ),
              ( ['in'], WSTRING, 'pstrEventName' ),
              ( ['in'], WSTRING, 'pstrDelimiter' ),
              ( ['in'], c_ulong, 'dwSourceContextCookie' ),
              ( ['in'], c_ulong, 'ulStartingLineNumber' ),
              ( ['in'], c_ulong, 'dwFlags' ),
              ( ['out'], POINTER(BSTR), 'pBstrName' ),
              ( ['out'], POINTER(tagEXCEPINFO), 'pexcepinfo' )),
    COMMETHOD([], HRESULT, 'ParseScriptText',
              ( ['in'], WSTRING, 'pstrCode' ),
              ( ['in'], WSTRING, 'pstrItemName' ),
              ( ['in'], POINTER(IUnknown), 'punkContext' ),
              ( ['in'], WSTRING, 'pstrDelimiter' ),
              ( ['in'], c_ulong, 'dwSourceContextCookie' ),
              ( ['in'], c_ulong, 'ulStartingLineNumber' ),
              ( ['in'], c_ulong, 'dwFlags' ),
              ( ['out'], POINTER(VARIANT), 'pvarResult' ),
              ( ['out'], POINTER(tagEXCEPINFO), 'pexcepinfo' )),
]
IActiveScriptSite._methods_ = [
    COMMETHOD([], HRESULT, 'GetLCID',
              ( ['out'], POINTER(c_ulong), 'plcid' )),
    COMMETHOD([], HRESULT, 'GetItemInfo',
              ( ['in'], WSTRING, 'pstrName' ),
              ( ['in'], c_ulong, 'dwReturnMask' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppiunkItem' ),
              ( ['out'], POINTER(POINTER(ITypeInfo)), 'ppti' )),
    COMMETHOD([], HRESULT, 'GetDocVersionString',
              ( ['out'], POINTER(BSTR), 'pbstrVersion' )),
    COMMETHOD([], HRESULT, 'OnScriptTerminate',
              ( ['in'], POINTER(VARIANT), 'pvarResult' ),
              ( ['in'], POINTER(tagEXCEPINFO), 'pexcepinfo' )),
    COMMETHOD([], HRESULT, 'OnStateChange',
              ( ['in'], tagSCRIPTSTATE, 'ssScriptState' )),
    COMMETHOD([], HRESULT, 'OnScriptError',
              ( ['in'], POINTER(IActiveScriptError), 'pscripterror' )),
    COMMETHOD([], HRESULT, 'OnEnterScript'),
    COMMETHOD([], HRESULT, 'OnLeaveScript'),
]

################################################################

# fakes, because they are not really used
IDebugDocumentContext = IDebugApplication = IDebugApplicationNode = IScriptErrorDebug = IUnknown
class IActiveScriptSiteDebug(IUnknown):
    _iid_ = GUID("{51973C11-CB0C-11d0-B5C9-00A0244A0E7A}")

    _methods_ = [
        STDMETHOD(HRESULT, "GetDocumentContextFromPosition",
                  [c_ulong, c_ulong, c_ulong, POINTER(POINTER(IDebugDocumentContext))]),
        STDMETHOD(HRESULT, "GetApplication",
                  [POINTER(POINTER(IDebugApplication))]),
        STDMETHOD(HRESULT, "GetRootApplicationNode",
                  [POINTER(POINTER(IDebugApplicationNode))]),
        STDMETHOD(HRESULT, "OnScriptErrorDebug",
                  [POINTER(IScriptErrorDebug), POINTER(BOOL), POINTER(BOOL)]),
        ]

SCRIPTITEM_ISVISIBLE            = 0x00000002
SCRIPTITEM_ISSOURCE             = 0x00000004
SCRIPTITEM_GLOBALMEMBERS        = 0x00000008
SCRIPTITEM_ISPERSISTENT         = 0x00000040
SCRIPTITEM_CODEONLY             = 0x00000200
SCRIPTITEM_NOCODE               = 0x00000400

SCRIPTTYPELIB_ISCONTROL         = 0x00000010
SCRIPTTYPELIB_ISPERSISTENT      = 0x00000040

SCRIPTTEXT_DELAYEXECUTION       = 0x00000001
SCRIPTTEXT_ISVISIBLE            = 0x00000002
SCRIPTTEXT_ISEXPRESSION         = 0x00000020
SCRIPTTEXT_ISPERSISTENT         = 0x00000040
SCRIPTTEXT_HOSTMANAGESSOURCE    = 0x00000080

SCRIPTTHREADID_CURRENT  = -1
SCRIPTTHREADID_BASE     = -2
SCRIPTTHREADID_ALL      = -3

SCRIPTINTERRUPT_DEBUG           = 0x00000001
SCRIPTINTERRUPT_RAISEEXCEPTION  = 0x00000002

SCRIPTINFO_IUNKNOWN             = 0x00000001
SCRIPTINFO_ITYPEINFO            = 0x00000002

# --eof--
