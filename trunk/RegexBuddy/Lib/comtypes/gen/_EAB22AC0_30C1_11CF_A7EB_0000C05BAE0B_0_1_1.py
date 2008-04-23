typelib_path = u'C:\\Windows\\system32\\ieframe.dll'
_lcid = 0 # change this if required
from ctypes import *
import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0
from comtypes import GUID
from ctypes import HRESULT
from comtypes.automation import VARIANT
from comtypes.automation import IDispatch
from comtypes import IUnknown
from ctypes.wintypes import VARIANT_BOOL
from comtypes import helpstring
from comtypes import COMMETHOD
from comtypes import dispid
from comtypes import CoClass
from comtypes import BSTR
from comtypes import DISPMETHOD, DISPPROPERTY, helpstring


class IShellWindows(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    u'Definition of interface IShellWindows'
    _iid_ = GUID('{85CB6900-4D95-11CF-960C-0080C7F4EE85}')
    _idlflags_ = ['dual', 'oleautomation']
IShellWindows._methods_ = [
    COMMETHOD([dispid(1610743808), helpstring(u'Get count of open Shell windows'), 'propget'], HRESULT, 'Count',
              ( ['retval', 'out'], POINTER(c_int), 'Count' )),
    COMMETHOD([dispid(0), helpstring(u'Return the shell window for the given index')], HRESULT, 'Item',
              ( ['in', 'optional'], VARIANT, 'index' ),
              ( ['retval', 'out'], POINTER(POINTER(IDispatch)), 'Folder' )),
    COMMETHOD([dispid(-4), helpstring(u'Enumerates the figures')], HRESULT, '_NewEnum',
              ( ['retval', 'out'], POINTER(POINTER(IUnknown)), 'ppunk' )),
    COMMETHOD([dispid(1610743811), helpstring(u'Register a window with the list'), 'hidden'], HRESULT, 'Register',
              ( ['in'], POINTER(IDispatch), 'pid' ),
              ( ['in'], c_int, 'HWND' ),
              ( ['in'], c_int, 'swClass' ),
              ( ['out'], POINTER(c_int), 'plCookie' )),
    COMMETHOD([dispid(1610743812), helpstring(u'Register a pending open with the list'), 'hidden'], HRESULT, 'RegisterPending',
              ( ['in'], c_int, 'lThreadId' ),
              ( ['in'], POINTER(VARIANT), 'pvarloc' ),
              ( ['in'], POINTER(VARIANT), 'pvarlocRoot' ),
              ( ['in'], c_int, 'swClass' ),
              ( ['out'], POINTER(c_int), 'plCookie' )),
    COMMETHOD([dispid(1610743813), helpstring(u'Remove a window from the list'), 'hidden'], HRESULT, 'Revoke',
              ( ['in'], c_int, 'lCookie' )),
    COMMETHOD([dispid(1610743814), helpstring(u'Notifies the new location'), 'hidden'], HRESULT, 'OnNavigate',
              ( ['in'], c_int, 'lCookie' ),
              ( ['in'], POINTER(VARIANT), 'pvarloc' )),
    COMMETHOD([dispid(1610743815), helpstring(u'Notifies the activation'), 'hidden'], HRESULT, 'OnActivated',
              ( ['in'], c_int, 'lCookie' ),
              ( ['in'], VARIANT_BOOL, 'fActive' )),
    COMMETHOD([dispid(1610743816), helpstring(u'Find the window based on the location'), 'hidden'], HRESULT, 'FindWindowSW',
              ( ['in'], POINTER(VARIANT), 'pvarloc' ),
              ( ['in'], POINTER(VARIANT), 'pvarlocRoot' ),
              ( ['in'], c_int, 'swClass' ),
              ( ['out'], POINTER(c_int), 'pHWND' ),
              ( ['in'], c_int, 'swfwOptions' ),
              ( ['retval', 'out'], POINTER(POINTER(IDispatch)), 'ppdispOut' )),
    COMMETHOD([dispid(1610743817), helpstring(u'Notifies on creation and frame name set'), 'hidden'], HRESULT, 'OnCreated',
              ( ['in'], c_int, 'lCookie' ),
              ( ['in'], POINTER(IUnknown), 'punk' )),
    COMMETHOD([dispid(1610743818), helpstring(u'Used by IExplore to register different processes'), 'hidden'], HRESULT, 'ProcessAttachDetach',
              ( ['in'], VARIANT_BOOL, 'fAttach' )),
]
################################################################
## code template for IShellWindows implementation
##class IShellWindows_Impl(object):
##    @property
##    def Count(self):
##        u'Get count of open Shell windows'
##        #return Count
##
##    def FindWindowSW(self, pvarloc, pvarlocRoot, swClass, swfwOptions):
##        u'Find the window based on the location'
##        #return pHWND, ppdispOut
##
##    def _NewEnum(self):
##        u'Enumerates the figures'
##        #return ppunk
##
##    def ProcessAttachDetach(self, fAttach):
##        u'Used by IExplore to register different processes'
##        #return 
##
##    def Register(self, pid, HWND, swClass):
##        u'Register a window with the list'
##        #return plCookie
##
##    def OnNavigate(self, lCookie, pvarloc):
##        u'Notifies the new location'
##        #return 
##
##    def Item(self, index):
##        u'Return the shell window for the given index'
##        #return Folder
##
##    def OnCreated(self, lCookie, punk):
##        u'Notifies on creation and frame name set'
##        #return 
##
##    def Revoke(self, lCookie):
##        u'Remove a window from the list'
##        #return 
##
##    def OnActivated(self, lCookie, fActive):
##        u'Notifies the activation'
##        #return 
##
##    def RegisterPending(self, lThreadId, pvarloc, pvarlocRoot, swClass):
##        u'Register a pending open with the list'
##        #return plCookie
##


# values for enumeration 'SecureLockIconConstants'
secureLockIconUnsecure = 0
secureLockIconMixed = 1
secureLockIconSecureUnknownBits = 2
secureLockIconSecure40Bit = 3
secureLockIconSecure56Bit = 4
secureLockIconSecureFortezza = 5
secureLockIconSecure128Bit = 6
SecureLockIconConstants = c_int # enum
class CScriptErrorList(CoClass):
    _reg_clsid_ = GUID('{EFD01300-160F-11D2-BB2E-00805FF7EFCA}')
    _idlflags_ = ['hidden', 'noncreatable']
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
class IScriptErrorList(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    u'Script Error List Interface'
    _iid_ = GUID('{F3470F24-15FD-11D2-BB2E-00805FF7EFCA}')
    _idlflags_ = ['dual', 'oleautomation', 'hidden']
CScriptErrorList._com_interfaces_ = [IScriptErrorList]

class ShellWindows(CoClass):
    u'ShellDispatch Load in Shell Context'
    _reg_clsid_ = GUID('{9BA05972-F6A8-11CF-A442-00A0C90A8F39}')
    _idlflags_ = []
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
class DShellWindowsEvents(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    'Event interface for IShellWindows'
    _iid_ = GUID('{FE4106E0-399A-11D0-A48C-00A0C90A8F39}')
    _idlflags_ = []
    _methods_ = []
ShellWindows._com_interfaces_ = [IShellWindows]
ShellWindows._outgoing_interfaces_ = [DShellWindowsEvents]

class WebBrowser_V1(CoClass):
    u'WebBrowser Control'
    _reg_clsid_ = GUID('{EAB22AC3-30C1-11CF-A7EB-0000C05BAE0B}')
    _idlflags_ = ['control']
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
class IWebBrowser(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    u'Web Browser interface'
    _iid_ = GUID('{EAB22AC1-30C1-11CF-A7EB-0000C05BAE0B}')
    _idlflags_ = ['dual', 'oleautomation', 'hidden']
class IWebBrowserApp(IWebBrowser):
    _case_insensitive_ = True
    u'Web Browser Application Interface.'
    _iid_ = GUID('{0002DF05-0000-0000-C000-000000000046}')
    _idlflags_ = ['dual', 'oleautomation', 'hidden']
class IWebBrowser2(IWebBrowserApp):
    _case_insensitive_ = True
    u'Web Browser Interface for IE4.'
    _iid_ = GUID('{D30C1661-CDAF-11D0-8A3E-00C04FC9E26E}')
    _idlflags_ = ['dual', 'oleautomation', 'hidden']
class DWebBrowserEvents2(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    'Web Browser Control events interface'
    _iid_ = GUID('{34A715A0-6587-11D0-924A-0020AFC7AC4D}')
    _idlflags_ = ['hidden']
    _methods_ = []
class DWebBrowserEvents(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    'Web Browser Control Events (old)'
    _iid_ = GUID('{EAB22AC2-30C1-11CF-A7EB-0000C05BAE0B}')
    _idlflags_ = ['hidden']
    _methods_ = []
WebBrowser_V1._com_interfaces_ = [IWebBrowser2, IWebBrowser]
WebBrowser_V1._outgoing_interfaces_ = [DWebBrowserEvents2, DWebBrowserEvents]


# values for enumeration 'OLECMDEXECOPT'
OLECMDEXECOPT_DODEFAULT = 0
OLECMDEXECOPT_PROMPTUSER = 1
OLECMDEXECOPT_DONTPROMPTUSER = 2
OLECMDEXECOPT_SHOWHELP = 3
OLECMDEXECOPT = c_int # enum
class ShellUIHelper(CoClass):
    _reg_clsid_ = GUID('{64AB4BB7-111E-11D1-8F79-00C04FC2FBE1}')
    _idlflags_ = []
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
class IShellUIHelper(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    u'Shell UI Helper Control Interface'
    _iid_ = GUID('{729FE2F8-1EA8-11D1-8F85-00C04FC2FBE1}')
    _idlflags_ = ['dual', 'oleautomation']
class IShellUIHelper2(IShellUIHelper):
    _case_insensitive_ = True
    u'Shell UI Helper Control Interface 2'
    _iid_ = GUID('{A7FE6EDA-1932-4281-B881-87B31B8BC52C}')
    _idlflags_ = ['dual', 'oleautomation']
ShellUIHelper._com_interfaces_ = [IShellUIHelper2]


# values for enumeration 'ShellWindowTypeConstants'
SWC_EXPLORER = 0
SWC_BROWSER = 1
SWC_3RDPARTY = 2
SWC_CALLBACK = 4
SWC_DESKTOP = 8
ShellWindowTypeConstants = c_int # enum
DWebBrowserEvents2._disp_methods_ = [
    DISPMETHOD([dispid(102), helpstring(u'Statusbar text changed.')], None, 'StatusTextChange',
               ( ['in'], BSTR, 'Text' )),
    DISPMETHOD([dispid(108), helpstring(u'Fired when download progress is updated.')], None, 'ProgressChange',
               ( ['in'], c_int, 'Progress' ),
               ( ['in'], c_int, 'ProgressMax' )),
    DISPMETHOD([dispid(105), helpstring(u'The enabled state of a command changed.')], None, 'CommandStateChange',
               ( ['in'], c_int, 'Command' ),
               ( ['in'], VARIANT_BOOL, 'Enable' )),
    DISPMETHOD([dispid(106), helpstring(u'Download of a page started.')], None, 'DownloadBegin'),
    DISPMETHOD([dispid(104), helpstring(u'Download of page complete.')], None, 'DownloadComplete'),
    DISPMETHOD([dispid(113), helpstring(u'Document title changed.')], None, 'TitleChange',
               ( ['in'], BSTR, 'Text' )),
    DISPMETHOD([dispid(112), helpstring(u'Fired when the PutProperty method has been called.')], None, 'PropertyChange',
               ( ['in'], BSTR, 'szProperty' )),
    DISPMETHOD([dispid(250), helpstring(u'Fired before navigate occurs in the given WebBrowser (window or frameset element). The processing of this navigation may be modified.')], None, 'BeforeNavigate2',
               ( ['in'], POINTER(IDispatch), 'pDisp' ),
               ( ['in'], POINTER(VARIANT), 'URL' ),
               ( ['in'], POINTER(VARIANT), 'Flags' ),
               ( ['in'], POINTER(VARIANT), 'TargetFrameName' ),
               ( ['in'], POINTER(VARIANT), 'PostData' ),
               ( ['in'], POINTER(VARIANT), 'Headers' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' )),
    DISPMETHOD([dispid(251), helpstring(u'A new, hidden, non-navigated WebBrowser window is needed.')], None, 'NewWindow2',
               ( ['in', 'out'], POINTER(POINTER(IDispatch)), 'ppDisp' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' )),
    DISPMETHOD([dispid(252), helpstring(u'Fired when the document being navigated to becomes visible and enters the navigation stack.')], None, 'NavigateComplete2',
               ( ['in'], POINTER(IDispatch), 'pDisp' ),
               ( ['in'], POINTER(VARIANT), 'URL' )),
    DISPMETHOD([dispid(259), helpstring(u'Fired when the document being navigated to reaches ReadyState_Complete.')], None, 'DocumentComplete',
               ( ['in'], POINTER(IDispatch), 'pDisp' ),
               ( ['in'], POINTER(VARIANT), 'URL' )),
    DISPMETHOD([dispid(253), helpstring(u'Fired when application is quiting.')], None, 'OnQuit'),
    DISPMETHOD([dispid(254), helpstring(u'Fired when the window should be shown/hidden')], None, 'OnVisible',
               ( ['in'], VARIANT_BOOL, 'Visible' )),
    DISPMETHOD([dispid(255), helpstring(u'Fired when the toolbar  should be shown/hidden')], None, 'OnToolBar',
               ( ['in'], VARIANT_BOOL, 'ToolBar' )),
    DISPMETHOD([dispid(256), helpstring(u'Fired when the menubar should be shown/hidden')], None, 'OnMenuBar',
               ( ['in'], VARIANT_BOOL, 'MenuBar' )),
    DISPMETHOD([dispid(257), helpstring(u'Fired when the statusbar should be shown/hidden')], None, 'OnStatusBar',
               ( ['in'], VARIANT_BOOL, 'StatusBar' )),
    DISPMETHOD([dispid(258), helpstring(u'Fired when fullscreen mode should be on/off')], None, 'OnFullScreen',
               ( ['in'], VARIANT_BOOL, 'FullScreen' )),
    DISPMETHOD([dispid(260), helpstring(u'Fired when theater mode should be on/off')], None, 'OnTheaterMode',
               ( ['in'], VARIANT_BOOL, 'TheaterMode' )),
    DISPMETHOD([dispid(262), helpstring(u'Fired when the host window should allow/disallow resizing')], None, 'WindowSetResizable',
               ( ['in'], VARIANT_BOOL, 'Resizable' )),
    DISPMETHOD([dispid(264), helpstring(u'Fired when the host window should change its Left coordinate')], None, 'WindowSetLeft',
               ( ['in'], c_int, 'Left' )),
    DISPMETHOD([dispid(265), helpstring(u'Fired when the host window should change its Top coordinate')], None, 'WindowSetTop',
               ( ['in'], c_int, 'Top' )),
    DISPMETHOD([dispid(266), helpstring(u'Fired when the host window should change its width')], None, 'WindowSetWidth',
               ( ['in'], c_int, 'Width' )),
    DISPMETHOD([dispid(267), helpstring(u'Fired when the host window should change its height')], None, 'WindowSetHeight',
               ( ['in'], c_int, 'Height' )),
    DISPMETHOD([dispid(263), helpstring(u'Fired when the WebBrowser is about to be closed by script')], None, 'WindowClosing',
               ( ['in'], VARIANT_BOOL, 'IsChildWindow' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' )),
    DISPMETHOD([dispid(268), helpstring(u'Fired to request client sizes be converted to host window sizes')], None, 'ClientToHostWindow',
               ( ['in', 'out'], POINTER(c_int), 'CX' ),
               ( ['in', 'out'], POINTER(c_int), 'CY' )),
    DISPMETHOD([dispid(269), helpstring(u'Fired to indicate the security level of the current web page contents')], None, 'SetSecureLockIcon',
               ( ['in'], c_int, 'SecureLockIcon' )),
    DISPMETHOD([dispid(270), helpstring(u'Fired to indicate the File Download dialog is opening')], None, 'FileDownload',
               ( ['in'], VARIANT_BOOL, 'ActiveDocument' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' )),
    DISPMETHOD([dispid(271), helpstring(u'Fired when a binding error occurs (window or frameset element).')], None, 'NavigateError',
               ( ['in'], POINTER(IDispatch), 'pDisp' ),
               ( ['in'], POINTER(VARIANT), 'URL' ),
               ( ['in'], POINTER(VARIANT), 'Frame' ),
               ( ['in'], POINTER(VARIANT), 'StatusCode' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' )),
    DISPMETHOD([dispid(225), helpstring(u'Fired when a print template is instantiated.')], None, 'PrintTemplateInstantiation',
               ( ['in'], POINTER(IDispatch), 'pDisp' )),
    DISPMETHOD([dispid(226), helpstring(u'Fired when a print template destroyed.')], None, 'PrintTemplateTeardown',
               ( ['in'], POINTER(IDispatch), 'pDisp' )),
    DISPMETHOD([dispid(227), helpstring(u'Fired when a page is spooled. When it is fired can be changed by a custom template.')], None, 'UpdatePageStatus',
               ( ['in'], POINTER(IDispatch), 'pDisp' ),
               ( ['in'], POINTER(VARIANT), 'nPage' ),
               ( ['in'], POINTER(VARIANT), 'fDone' )),
    DISPMETHOD([dispid(272), helpstring(u'Fired when the global privacy impacted state changes')], None, 'PrivacyImpactedStateChange',
               ( ['in'], VARIANT_BOOL, 'bImpacted' )),
    DISPMETHOD([dispid(273), helpstring(u'A new, hidden, non-navigated WebBrowser window is needed.')], None, 'NewWindow3',
               ( ['in', 'out'], POINTER(POINTER(IDispatch)), 'ppDisp' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' ),
               ( ['in'], c_ulong, 'dwFlags' ),
               ( ['in'], BSTR, 'bstrUrlContext' ),
               ( ['in'], BSTR, 'bstrUrl' )),
    DISPMETHOD([dispid(282), helpstring(u'Fired to indicate the progress and status of the Phishing Filter analysis of the current web page')], None, 'SetPhishingFilterStatus',
               ( ['in'], c_int, 'PhishingFilterStatus' )),
    DISPMETHOD([dispid(283), helpstring(u"Fired to indicate that the browser window's visibility or enabled state has changed.")], None, 'WindowStateChanged',
               ( ['in'], c_ulong, 'dwWindowStateFlags' ),
               ( ['in'], c_ulong, 'dwValidFlagsMask' )),
]
IShellUIHelper._methods_ = [
    COMMETHOD([dispid(1), 'hidden'], HRESULT, 'ResetFirstBootMode'),
    COMMETHOD([dispid(2), 'hidden'], HRESULT, 'ResetSafeMode'),
    COMMETHOD([dispid(3), 'hidden'], HRESULT, 'RefreshOfflineDesktop'),
    COMMETHOD([dispid(4)], HRESULT, 'AddFavorite',
              ( ['in'], BSTR, 'URL' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Title' )),
    COMMETHOD([dispid(5)], HRESULT, 'AddChannel',
              ( ['in'], BSTR, 'URL' )),
    COMMETHOD([dispid(6)], HRESULT, 'AddDesktopComponent',
              ( ['in'], BSTR, 'URL' ),
              ( ['in'], BSTR, 'Type' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Left' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Top' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Width' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Height' )),
    COMMETHOD([dispid(7)], HRESULT, 'IsSubscribed',
              ( ['in'], BSTR, 'URL' ),
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pBool' )),
    COMMETHOD([dispid(8)], HRESULT, 'NavigateAndFind',
              ( ['in'], BSTR, 'URL' ),
              ( ['in'], BSTR, 'strQuery' ),
              ( ['in'], POINTER(VARIANT), 'varTargetFrame' )),
    COMMETHOD([dispid(9)], HRESULT, 'ImportExportFavorites',
              ( ['in'], VARIANT_BOOL, 'fImport' ),
              ( ['in'], BSTR, 'strImpExpPath' )),
    COMMETHOD([dispid(10)], HRESULT, 'AutoCompleteSaveForm',
              ( ['in', 'optional'], POINTER(VARIANT), 'Form' )),
    COMMETHOD([dispid(11)], HRESULT, 'AutoScan',
              ( ['in'], BSTR, 'strSearch' ),
              ( ['in'], BSTR, 'strFailureUrl' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'pvarTargetFrame' )),
    COMMETHOD([dispid(12), 'hidden'], HRESULT, 'AutoCompleteAttach',
              ( ['in', 'optional'], POINTER(VARIANT), 'Reserved' )),
    COMMETHOD([dispid(13)], HRESULT, 'ShowBrowserUI',
              ( ['in'], BSTR, 'bstrName' ),
              ( ['in'], POINTER(VARIANT), 'pvarIn' ),
              ( ['retval', 'out'], POINTER(VARIANT), 'pvarOut' )),
]
################################################################
## code template for IShellUIHelper implementation
##class IShellUIHelper_Impl(object):
##    def ResetFirstBootMode(self):
##        '-no docstring-'
##        #return 
##
##    def RefreshOfflineDesktop(self):
##        '-no docstring-'
##        #return 
##
##    def AddChannel(self, URL):
##        '-no docstring-'
##        #return 
##
##    def ImportExportFavorites(self, fImport, strImpExpPath):
##        '-no docstring-'
##        #return 
##
##    def IsSubscribed(self, URL):
##        '-no docstring-'
##        #return pBool
##
##    def AutoScan(self, strSearch, strFailureUrl, pvarTargetFrame):
##        '-no docstring-'
##        #return 
##
##    def AddFavorite(self, URL, Title):
##        '-no docstring-'
##        #return 
##
##    def AutoCompleteAttach(self, Reserved):
##        '-no docstring-'
##        #return 
##
##    def NavigateAndFind(self, URL, strQuery, varTargetFrame):
##        '-no docstring-'
##        #return 
##
##    def ShowBrowserUI(self, bstrName, pvarIn):
##        '-no docstring-'
##        #return pvarOut
##
##    def ResetSafeMode(self):
##        '-no docstring-'
##        #return 
##
##    def AddDesktopComponent(self, URL, Type, Left, Top, Width, Height):
##        '-no docstring-'
##        #return 
##
##    def AutoCompleteSaveForm(self, Form):
##        '-no docstring-'
##        #return 
##


# values for enumeration 'ShellWindowFindWindowOptions'
SWFO_NEEDDISPATCH = 1
SWFO_INCLUDEPENDING = 2
SWFO_COOKIEPASSED = 4
ShellWindowFindWindowOptions = c_int # enum

# values for enumeration 'OLECMDF'
OLECMDF_SUPPORTED = 1
OLECMDF_ENABLED = 2
OLECMDF_LATCHED = 4
OLECMDF_NINCHED = 8
OLECMDF_INVISIBLE = 16
OLECMDF_DEFHIDEONCTXTMENU = 32
OLECMDF = c_int # enum
IScriptErrorList._methods_ = [
    COMMETHOD([dispid(10)], HRESULT, 'advanceError'),
    COMMETHOD([dispid(11)], HRESULT, 'retreatError'),
    COMMETHOD([dispid(12)], HRESULT, 'canAdvanceError',
              ( ['retval', 'out'], POINTER(c_int), 'pfCanAdvance' )),
    COMMETHOD([dispid(13)], HRESULT, 'canRetreatError',
              ( ['retval', 'out'], POINTER(c_int), 'pfCanRetreat' )),
    COMMETHOD([dispid(14)], HRESULT, 'getErrorLine',
              ( ['retval', 'out'], POINTER(c_int), 'plLine' )),
    COMMETHOD([dispid(15)], HRESULT, 'getErrorChar',
              ( ['retval', 'out'], POINTER(c_int), 'plChar' )),
    COMMETHOD([dispid(16)], HRESULT, 'getErrorCode',
              ( ['retval', 'out'], POINTER(c_int), 'plCode' )),
    COMMETHOD([dispid(17)], HRESULT, 'getErrorMsg',
              ( ['retval', 'out'], POINTER(BSTR), 'pstr' )),
    COMMETHOD([dispid(18)], HRESULT, 'getErrorUrl',
              ( ['retval', 'out'], POINTER(BSTR), 'pstr' )),
    COMMETHOD([dispid(23)], HRESULT, 'getAlwaysShowLockState',
              ( ['retval', 'out'], POINTER(c_int), 'pfAlwaysShowLocked' )),
    COMMETHOD([dispid(19)], HRESULT, 'getDetailsPaneOpen',
              ( ['retval', 'out'], POINTER(c_int), 'pfDetailsPaneOpen' )),
    COMMETHOD([dispid(20)], HRESULT, 'setDetailsPaneOpen',
              ( [], c_int, 'fDetailsPaneOpen' )),
    COMMETHOD([dispid(21)], HRESULT, 'getPerErrorDisplay',
              ( ['retval', 'out'], POINTER(c_int), 'pfPerErrorDisplay' )),
    COMMETHOD([dispid(22)], HRESULT, 'setPerErrorDisplay',
              ( [], c_int, 'fPerErrorDisplay' )),
]
################################################################
## code template for IScriptErrorList implementation
##class IScriptErrorList_Impl(object):
##    def advanceError(self):
##        '-no docstring-'
##        #return 
##
##    def canAdvanceError(self):
##        '-no docstring-'
##        #return pfCanAdvance
##
##    def getErrorCode(self):
##        '-no docstring-'
##        #return plCode
##
##    def getErrorUrl(self):
##        '-no docstring-'
##        #return pstr
##
##    def getPerErrorDisplay(self):
##        '-no docstring-'
##        #return pfPerErrorDisplay
##
##    def setDetailsPaneOpen(self, fDetailsPaneOpen):
##        '-no docstring-'
##        #return 
##
##    def getAlwaysShowLockState(self):
##        '-no docstring-'
##        #return pfAlwaysShowLocked
##
##    def getErrorLine(self):
##        '-no docstring-'
##        #return plLine
##
##    def getDetailsPaneOpen(self):
##        '-no docstring-'
##        #return pfDetailsPaneOpen
##
##    def getErrorChar(self):
##        '-no docstring-'
##        #return plChar
##
##    def setPerErrorDisplay(self, fPerErrorDisplay):
##        '-no docstring-'
##        #return 
##
##    def canRetreatError(self):
##        '-no docstring-'
##        #return pfCanRetreat
##
##    def retreatError(self):
##        '-no docstring-'
##        #return 
##
##    def getErrorMsg(self):
##        '-no docstring-'
##        #return pstr
##

class Library(object):
    u'Microsoft Internet Controls'
    name = u'SHDocVw'
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)

class DShellNameSpaceEvents(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    _iid_ = GUID('{55136806-B2DE-11D1-B9F2-00A0C98BC547}')
    _idlflags_ = []
    _methods_ = []
DShellNameSpaceEvents._disp_methods_ = [
    DISPMETHOD([dispid(1)], None, 'FavoritesSelectionChange',
               ( ['in'], c_int, 'cItems' ),
               ( ['in'], c_int, 'hItem' ),
               ( ['in'], BSTR, 'strName' ),
               ( ['in'], BSTR, 'strUrl' ),
               ( ['in'], c_int, 'cVisits' ),
               ( ['in'], BSTR, 'strDate' ),
               ( ['in'], c_int, 'fAvailableOffline' )),
    DISPMETHOD([dispid(2)], None, 'SelectionChange'),
    DISPMETHOD([dispid(3)], None, 'DoubleClick'),
    DISPMETHOD([dispid(4)], None, 'Initialized'),
]
class IShellFavoritesNameSpace(comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IDispatch):
    _case_insensitive_ = True
    u'IShellFavoritesNameSpace Interface'
    _iid_ = GUID('{55136804-B2DE-11D1-B9F2-00A0C98BC547}')
    _idlflags_ = ['dual', 'oleautomation', 'hidden']
class IShellNameSpace(IShellFavoritesNameSpace):
    _case_insensitive_ = True
    u'IShellNameSpace Interface'
    _iid_ = GUID('{E572D3C9-37BE-4AE2-825D-D521763E3108}')
    _idlflags_ = ['dual', 'oleautomation', 'hidden']
IShellFavoritesNameSpace._methods_ = [
    COMMETHOD([dispid(1), helpstring(u'method MoveSelectionUp')], HRESULT, 'MoveSelectionUp'),
    COMMETHOD([dispid(2), helpstring(u'method MoveSelectionDown')], HRESULT, 'MoveSelectionDown'),
    COMMETHOD([dispid(3), helpstring(u'method ResetSort')], HRESULT, 'ResetSort'),
    COMMETHOD([dispid(4), helpstring(u'method NewFolder')], HRESULT, 'NewFolder'),
    COMMETHOD([dispid(5), helpstring(u'method Synchronize')], HRESULT, 'Synchronize'),
    COMMETHOD([dispid(6), helpstring(u'method Import')], HRESULT, 'Import'),
    COMMETHOD([dispid(7), helpstring(u'method Export')], HRESULT, 'Export'),
    COMMETHOD([dispid(8), helpstring(u'method InvokeContextMenuCommand')], HRESULT, 'InvokeContextMenuCommand',
              ( ['in'], BSTR, 'strCommand' )),
    COMMETHOD([dispid(9), helpstring(u'method MoveSelectionTo')], HRESULT, 'MoveSelectionTo'),
    COMMETHOD([dispid(10), helpstring(u'Query to see if subscriptions are enabled'), 'propget'], HRESULT, 'SubscriptionsEnabled',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pBool' )),
    COMMETHOD([dispid(11), helpstring(u'method CreateSubscriptionForSelection')], HRESULT, 'CreateSubscriptionForSelection',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pBool' )),
    COMMETHOD([dispid(12), helpstring(u'method DeleteSubscriptionForSelection')], HRESULT, 'DeleteSubscriptionForSelection',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pBool' )),
    COMMETHOD([dispid(13), helpstring(u'old, use put_Root() instead')], HRESULT, 'SetRoot',
              ( ['in'], BSTR, 'bstrFullPath' )),
]
################################################################
## code template for IShellFavoritesNameSpace implementation
##class IShellFavoritesNameSpace_Impl(object):
##    def InvokeContextMenuCommand(self, strCommand):
##        u'method InvokeContextMenuCommand'
##        #return 
##
##    def DeleteSubscriptionForSelection(self):
##        u'method DeleteSubscriptionForSelection'
##        #return pBool
##
##    def MoveSelectionTo(self):
##        u'method MoveSelectionTo'
##        #return 
##
##    @property
##    def SubscriptionsEnabled(self):
##        u'Query to see if subscriptions are enabled'
##        #return pBool
##
##    def Synchronize(self):
##        u'method Synchronize'
##        #return 
##
##    def NewFolder(self):
##        u'method NewFolder'
##        #return 
##
##    def ResetSort(self):
##        u'method ResetSort'
##        #return 
##
##    def MoveSelectionUp(self):
##        u'method MoveSelectionUp'
##        #return 
##
##    def Import(self):
##        u'method Import'
##        #return 
##
##    def CreateSubscriptionForSelection(self):
##        u'method CreateSubscriptionForSelection'
##        #return pBool
##
##    def Export(self):
##        u'method Export'
##        #return 
##
##    def MoveSelectionDown(self):
##        u'method MoveSelectionDown'
##        #return 
##
##    def SetRoot(self, bstrFullPath):
##        u'old, use put_Root() instead'
##        #return 
##

IShellNameSpace._methods_ = [
    COMMETHOD([dispid(14), helpstring(u'options '), 'propget'], HRESULT, 'EnumOptions',
              ( ['retval', 'out'], POINTER(c_int), 'pgrfEnumFlags' )),
    COMMETHOD([dispid(14), helpstring(u'options '), 'propput'], HRESULT, 'EnumOptions',
              ( ['in'], c_int, 'pgrfEnumFlags' )),
    COMMETHOD([dispid(15), helpstring(u'get the selected item'), 'propget'], HRESULT, 'SelectedItem',
              ( ['retval', 'out'], POINTER(POINTER(IDispatch)), 'pItem' )),
    COMMETHOD([dispid(15), helpstring(u'get the selected item'), 'propput'], HRESULT, 'SelectedItem',
              ( ['in'], POINTER(IDispatch), 'pItem' )),
    COMMETHOD([dispid(16), helpstring(u'get the root item'), 'propget'], HRESULT, 'Root',
              ( ['retval', 'out'], POINTER(VARIANT), 'pvar' )),
    COMMETHOD([dispid(16), helpstring(u'get the root item'), 'propput'], HRESULT, 'Root',
              ( ['in'], VARIANT, 'pvar' )),
    COMMETHOD([dispid(17), 'propget'], HRESULT, 'Depth',
              ( ['retval', 'out'], POINTER(c_int), 'piDepth' )),
    COMMETHOD([dispid(17), 'propput'], HRESULT, 'Depth',
              ( ['in'], c_int, 'piDepth' )),
    COMMETHOD([dispid(18), 'propget'], HRESULT, 'Mode',
              ( ['retval', 'out'], POINTER(c_uint), 'puMode' )),
    COMMETHOD([dispid(18), 'propput'], HRESULT, 'Mode',
              ( ['in'], c_uint, 'puMode' )),
    COMMETHOD([dispid(19), 'propget'], HRESULT, 'Flags',
              ( ['retval', 'out'], POINTER(c_ulong), 'pdwFlags' )),
    COMMETHOD([dispid(19), 'propput'], HRESULT, 'Flags',
              ( ['in'], c_ulong, 'pdwFlags' )),
    COMMETHOD([dispid(20), 'propput'], HRESULT, 'TVFlags',
              ( ['in'], c_ulong, 'dwFlags' )),
    COMMETHOD([dispid(20), 'propget'], HRESULT, 'TVFlags',
              ( ['retval', 'out'], POINTER(c_ulong), 'dwFlags' )),
    COMMETHOD([dispid(21), 'propget'], HRESULT, 'Columns',
              ( ['retval', 'out'], POINTER(BSTR), 'bstrColumns' )),
    COMMETHOD([dispid(21), 'propput'], HRESULT, 'Columns',
              ( ['in'], BSTR, 'bstrColumns' )),
    COMMETHOD([dispid(22), helpstring(u'number of view types'), 'propget'], HRESULT, 'CountViewTypes',
              ( ['retval', 'out'], POINTER(c_int), 'piTypes' )),
    COMMETHOD([dispid(23), helpstring(u'set view type')], HRESULT, 'SetViewType',
              ( ['in'], c_int, 'iType' )),
    COMMETHOD([dispid(24), helpstring(u'collection of selected items')], HRESULT, 'SelectedItems',
              ( ['retval', 'out'], POINTER(POINTER(IDispatch)), 'ppid' )),
    COMMETHOD([dispid(25), helpstring(u'expands item specified depth')], HRESULT, 'Expand',
              ( ['in'], VARIANT, 'var' ),
              ( [], c_int, 'iDepth' )),
    COMMETHOD([dispid(26), helpstring(u'unselects all items')], HRESULT, 'UnselectAll'),
]
################################################################
## code template for IShellNameSpace implementation
##class IShellNameSpace_Impl(object):
##    @property
##    def CountViewTypes(self):
##        u'number of view types'
##        #return piTypes
##
##    def _get(self):
##        u'get the selected item'
##        #return pItem
##    def _set(self, pItem):
##        u'get the selected item'
##    SelectedItem = property(_get, _set, doc = _set.__doc__)
##
##    def SelectedItems(self):
##        u'collection of selected items'
##        #return ppid
##
##    def SetViewType(self, iType):
##        u'set view type'
##        #return 
##
##    def _get(self):
##        '-no docstring-'
##        #return piDepth
##    def _set(self, piDepth):
##        '-no docstring-'
##    Depth = property(_get, _set, doc = _set.__doc__)
##
##    def Expand(self, var, iDepth):
##        u'expands item specified depth'
##        #return 
##
##    def _get(self):
##        '-no docstring-'
##        #return pdwFlags
##    def _set(self, pdwFlags):
##        '-no docstring-'
##    Flags = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        '-no docstring-'
##        #return puMode
##    def _set(self, puMode):
##        '-no docstring-'
##    Mode = property(_get, _set, doc = _set.__doc__)
##
##    def UnselectAll(self):
##        u'unselects all items'
##        #return 
##
##    def _get(self):
##        '-no docstring-'
##        #return bstrColumns
##    def _set(self, bstrColumns):
##        '-no docstring-'
##    Columns = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'options '
##        #return pgrfEnumFlags
##    def _set(self, pgrfEnumFlags):
##        u'options '
##    EnumOptions = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'get the root item'
##        #return pvar
##    def _set(self, pvar):
##        u'get the root item'
##    Root = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        '-no docstring-'
##        #return dwFlags
##    def _set(self, dwFlags):
##        '-no docstring-'
##    TVFlags = property(_get, _set, doc = _set.__doc__)
##

IWebBrowser._methods_ = [
    COMMETHOD([dispid(100), helpstring(u'Navigates to the previous item in the history list.')], HRESULT, 'GoBack'),
    COMMETHOD([dispid(101), helpstring(u'Navigates to the next item in the history list.')], HRESULT, 'GoForward'),
    COMMETHOD([dispid(102), helpstring(u'Go home/start page.')], HRESULT, 'GoHome'),
    COMMETHOD([dispid(103), helpstring(u'Go Search Page.')], HRESULT, 'GoSearch'),
    COMMETHOD([dispid(104), helpstring(u'Navigates to a URL or file.')], HRESULT, 'Navigate',
              ( ['in'], BSTR, 'URL' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Flags' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'TargetFrameName' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'PostData' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Headers' )),
    COMMETHOD([dispid(-550), helpstring(u'Refresh the currently viewed page.')], HRESULT, 'Refresh'),
    COMMETHOD([dispid(105), helpstring(u'Refresh the currently viewed page.')], HRESULT, 'Refresh2',
              ( ['in', 'optional'], POINTER(VARIANT), 'Level' )),
    COMMETHOD([dispid(106), helpstring(u'Stops opening a file.')], HRESULT, 'Stop'),
    COMMETHOD([dispid(200), helpstring(u'Returns the application automation object if accessible, this automation object otherwise..'), 'propget'], HRESULT, 'Application',
              ( ['retval', 'out'], POINTER(POINTER(IDispatch)), 'ppDisp' )),
    COMMETHOD([dispid(201), helpstring(u'Returns the automation object of the container/parent if one exists or this automation object.'), 'propget'], HRESULT, 'Parent',
              ( ['retval', 'out'], POINTER(POINTER(IDispatch)), 'ppDisp' )),
    COMMETHOD([dispid(202), helpstring(u'Returns the container/parent automation object, if any.'), 'propget'], HRESULT, 'Container',
              ( ['retval', 'out'], POINTER(POINTER(IDispatch)), 'ppDisp' )),
    COMMETHOD([dispid(203), helpstring(u'Returns the active Document automation object, if any.'), 'propget'], HRESULT, 'Document',
              ( ['retval', 'out'], POINTER(POINTER(IDispatch)), 'ppDisp' )),
    COMMETHOD([dispid(204), helpstring(u'Returns True if this is the top level object.'), 'propget'], HRESULT, 'TopLevelContainer',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pBool' )),
    COMMETHOD([dispid(205), helpstring(u'Returns the type of the contained document object.'), 'propget'], HRESULT, 'Type',
              ( ['retval', 'out'], POINTER(BSTR), 'Type' )),
    COMMETHOD([dispid(206), helpstring(u'The horizontal position (pixels) of the frame window relative to the screen/container.'), 'propget'], HRESULT, 'Left',
              ( ['retval', 'out'], POINTER(c_int), 'pl' )),
    COMMETHOD([dispid(206), helpstring(u'The horizontal position (pixels) of the frame window relative to the screen/container.'), 'propput'], HRESULT, 'Left',
              ( ['in'], c_int, 'pl' )),
    COMMETHOD([dispid(207), helpstring(u'The vertical position (pixels) of the frame window relative to the screen/container.'), 'propget'], HRESULT, 'Top',
              ( ['retval', 'out'], POINTER(c_int), 'pl' )),
    COMMETHOD([dispid(207), helpstring(u'The vertical position (pixels) of the frame window relative to the screen/container.'), 'propput'], HRESULT, 'Top',
              ( ['in'], c_int, 'pl' )),
    COMMETHOD([dispid(208), helpstring(u'The horizontal dimension (pixels) of the frame window/object.'), 'propget'], HRESULT, 'Width',
              ( ['retval', 'out'], POINTER(c_int), 'pl' )),
    COMMETHOD([dispid(208), helpstring(u'The horizontal dimension (pixels) of the frame window/object.'), 'propput'], HRESULT, 'Width',
              ( ['in'], c_int, 'pl' )),
    COMMETHOD([dispid(209), helpstring(u'The vertical dimension (pixels) of the frame window/object.'), 'propget'], HRESULT, 'Height',
              ( ['retval', 'out'], POINTER(c_int), 'pl' )),
    COMMETHOD([dispid(209), helpstring(u'The vertical dimension (pixels) of the frame window/object.'), 'propput'], HRESULT, 'Height',
              ( ['in'], c_int, 'pl' )),
    COMMETHOD([dispid(210), helpstring(u'Gets the short (UI-friendly) name of the URL/file currently viewed.'), 'propget'], HRESULT, 'LocationName',
              ( ['retval', 'out'], POINTER(BSTR), 'LocationName' )),
    COMMETHOD([dispid(211), helpstring(u'Gets the full URL/path currently viewed.'), 'propget'], HRESULT, 'LocationURL',
              ( ['retval', 'out'], POINTER(BSTR), 'LocationURL' )),
    COMMETHOD([dispid(212), helpstring(u'Query to see if something is still in progress.'), 'propget'], HRESULT, 'Busy',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pBool' )),
]
################################################################
## code template for IWebBrowser implementation
##class IWebBrowser_Impl(object):
##    def Refresh2(self, Level):
##        u'Refresh the currently viewed page.'
##        #return 
##
##    @property
##    def TopLevelContainer(self):
##        u'Returns True if this is the top level object.'
##        #return pBool
##
##    @property
##    def Container(self):
##        u'Returns the container/parent automation object, if any.'
##        #return ppDisp
##
##    @property
##    def Parent(self):
##        u'Returns the automation object of the container/parent if one exists or this automation object.'
##        #return ppDisp
##
##    def _get(self):
##        u'The horizontal dimension (pixels) of the frame window/object.'
##        #return pl
##    def _set(self, pl):
##        u'The horizontal dimension (pixels) of the frame window/object.'
##    Width = property(_get, _set, doc = _set.__doc__)
##
##    def GoForward(self):
##        u'Navigates to the next item in the history list.'
##        #return 
##
##    def GoBack(self):
##        u'Navigates to the previous item in the history list.'
##        #return 
##
##    def _get(self):
##        u'The vertical position (pixels) of the frame window relative to the screen/container.'
##        #return pl
##    def _set(self, pl):
##        u'The vertical position (pixels) of the frame window relative to the screen/container.'
##    Top = property(_get, _set, doc = _set.__doc__)
##
##    @property
##    def LocationURL(self):
##        u'Gets the full URL/path currently viewed.'
##        #return LocationURL
##
##    def Stop(self):
##        u'Stops opening a file.'
##        #return 
##
##    def GoHome(self):
##        u'Go home/start page.'
##        #return 
##
##    def Refresh(self):
##        u'Refresh the currently viewed page.'
##        #return 
##
##    def _get(self):
##        u'The vertical dimension (pixels) of the frame window/object.'
##        #return pl
##    def _set(self, pl):
##        u'The vertical dimension (pixels) of the frame window/object.'
##    Height = property(_get, _set, doc = _set.__doc__)
##
##    @property
##    def LocationName(self):
##        u'Gets the short (UI-friendly) name of the URL/file currently viewed.'
##        #return LocationName
##
##    @property
##    def Application(self):
##        u'Returns the application automation object if accessible, this automation object otherwise..'
##        #return ppDisp
##
##    def GoSearch(self):
##        u'Go Search Page.'
##        #return 
##
##    @property
##    def Busy(self):
##        u'Query to see if something is still in progress.'
##        #return pBool
##
##    def Navigate(self, URL, Flags, TargetFrameName, PostData, Headers):
##        u'Navigates to a URL or file.'
##        #return 
##
##    @property
##    def Document(self):
##        u'Returns the active Document automation object, if any.'
##        #return ppDisp
##
##    @property
##    def Type(self):
##        u'Returns the type of the contained document object.'
##        #return Type
##
##    def _get(self):
##        u'The horizontal position (pixels) of the frame window relative to the screen/container.'
##        #return pl
##    def _set(self, pl):
##        u'The horizontal position (pixels) of the frame window relative to the screen/container.'
##    Left = property(_get, _set, doc = _set.__doc__)
##

IWebBrowserApp._methods_ = [
    COMMETHOD([dispid(300), helpstring(u'Exits application and closes the open document.')], HRESULT, 'Quit'),
    COMMETHOD([dispid(301), helpstring(u'Converts client sizes into window sizes.')], HRESULT, 'ClientToWindow',
              ( ['in', 'out'], POINTER(c_int), 'pcx' ),
              ( ['in', 'out'], POINTER(c_int), 'pcy' )),
    COMMETHOD([dispid(302), helpstring(u'Associates vtValue with the name szProperty in the context of the object.')], HRESULT, 'PutProperty',
              ( ['in'], BSTR, 'Property' ),
              ( ['in'], VARIANT, 'vtValue' )),
    COMMETHOD([dispid(303), helpstring(u'Retrieve the Associated value for the property vtValue in the context of the object.')], HRESULT, 'GetProperty',
              ( ['in'], BSTR, 'Property' ),
              ( ['retval', 'out'], POINTER(VARIANT), 'pvtValue' )),
    COMMETHOD([dispid(0), helpstring(u'Returns name of the application.'), 'propget'], HRESULT, 'Name',
              ( ['retval', 'out'], POINTER(BSTR), 'Name' )),
    COMMETHOD([dispid(-515), helpstring(u'Returns the HWND of the current IE window.'), 'propget'], HRESULT, 'HWND',
              ( ['retval', 'out'], POINTER(c_int), 'pHWND' )),
    COMMETHOD([dispid(400), helpstring(u'Returns file specification of the application, including path.'), 'propget'], HRESULT, 'FullName',
              ( ['retval', 'out'], POINTER(BSTR), 'FullName' )),
    COMMETHOD([dispid(401), helpstring(u'Returns the path to the application.'), 'propget'], HRESULT, 'Path',
              ( ['retval', 'out'], POINTER(BSTR), 'Path' )),
    COMMETHOD([dispid(402), helpstring(u'Determines whether the application is visible or hidden.'), 'propget'], HRESULT, 'Visible',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pBool' )),
    COMMETHOD([dispid(402), helpstring(u'Determines whether the application is visible or hidden.'), 'propput'], HRESULT, 'Visible',
              ( ['in'], VARIANT_BOOL, 'pBool' )),
    COMMETHOD([dispid(403), helpstring(u'Turn on or off the statusbar.'), 'propget'], HRESULT, 'StatusBar',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pBool' )),
    COMMETHOD([dispid(403), helpstring(u'Turn on or off the statusbar.'), 'propput'], HRESULT, 'StatusBar',
              ( ['in'], VARIANT_BOOL, 'pBool' )),
    COMMETHOD([dispid(404), helpstring(u'Text of Status window.'), 'propget'], HRESULT, 'StatusText',
              ( ['retval', 'out'], POINTER(BSTR), 'StatusText' )),
    COMMETHOD([dispid(404), helpstring(u'Text of Status window.'), 'propput'], HRESULT, 'StatusText',
              ( ['in'], BSTR, 'StatusText' )),
    COMMETHOD([dispid(405), helpstring(u'Controls which toolbar is shown.'), 'propget'], HRESULT, 'ToolBar',
              ( ['retval', 'out'], POINTER(c_int), 'Value' )),
    COMMETHOD([dispid(405), helpstring(u'Controls which toolbar is shown.'), 'propput'], HRESULT, 'ToolBar',
              ( ['in'], c_int, 'Value' )),
    COMMETHOD([dispid(406), helpstring(u'Controls whether menubar is shown.'), 'propget'], HRESULT, 'MenuBar',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'Value' )),
    COMMETHOD([dispid(406), helpstring(u'Controls whether menubar is shown.'), 'propput'], HRESULT, 'MenuBar',
              ( ['in'], VARIANT_BOOL, 'Value' )),
    COMMETHOD([dispid(407), helpstring(u'Maximizes window and turns off statusbar, toolbar, menubar, and titlebar.'), 'propget'], HRESULT, 'FullScreen',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pbFullScreen' )),
    COMMETHOD([dispid(407), helpstring(u'Maximizes window and turns off statusbar, toolbar, menubar, and titlebar.'), 'propput'], HRESULT, 'FullScreen',
              ( ['in'], VARIANT_BOOL, 'pbFullScreen' )),
]
################################################################
## code template for IWebBrowserApp implementation
##class IWebBrowserApp_Impl(object):
##    def Quit(self):
##        u'Exits application and closes the open document.'
##        #return 
##
##    def GetProperty(self, Property):
##        u'Retrieve the Associated value for the property vtValue in the context of the object.'
##        #return pvtValue
##
##    @property
##    def Name(self):
##        u'Returns name of the application.'
##        #return Name
##
##    def _get(self):
##        u'Maximizes window and turns off statusbar, toolbar, menubar, and titlebar.'
##        #return pbFullScreen
##    def _set(self, pbFullScreen):
##        u'Maximizes window and turns off statusbar, toolbar, menubar, and titlebar.'
##    FullScreen = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'Turn on or off the statusbar.'
##        #return pBool
##    def _set(self, pBool):
##        u'Turn on or off the statusbar.'
##    StatusBar = property(_get, _set, doc = _set.__doc__)
##
##    @property
##    def HWND(self):
##        u'Returns the HWND of the current IE window.'
##        #return pHWND
##
##    def ClientToWindow(self):
##        u'Converts client sizes into window sizes.'
##        #return pcx, pcy
##
##    def _get(self):
##        u'Determines whether the application is visible or hidden.'
##        #return pBool
##    def _set(self, pBool):
##        u'Determines whether the application is visible or hidden.'
##    Visible = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'Text of Status window.'
##        #return StatusText
##    def _set(self, StatusText):
##        u'Text of Status window.'
##    StatusText = property(_get, _set, doc = _set.__doc__)
##
##    @property
##    def Path(self):
##        u'Returns the path to the application.'
##        #return Path
##
##    @property
##    def FullName(self):
##        u'Returns file specification of the application, including path.'
##        #return FullName
##
##    def _get(self):
##        u'Controls whether menubar is shown.'
##        #return Value
##    def _set(self, Value):
##        u'Controls whether menubar is shown.'
##    MenuBar = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'Controls which toolbar is shown.'
##        #return Value
##    def _set(self, Value):
##        u'Controls which toolbar is shown.'
##    ToolBar = property(_get, _set, doc = _set.__doc__)
##
##    def PutProperty(self, Property, vtValue):
##        u'Associates vtValue with the name szProperty in the context of the object.'
##        #return 
##


# values for enumeration 'tagREADYSTATE'
READYSTATE_UNINITIALIZED = 0
READYSTATE_LOADING = 1
READYSTATE_LOADED = 2
READYSTATE_INTERACTIVE = 3
READYSTATE_COMPLETE = 4
tagREADYSTATE = c_int # enum

# values for enumeration 'OLECMDID'
OLECMDID_OPEN = 1
OLECMDID_NEW = 2
OLECMDID_SAVE = 3
OLECMDID_SAVEAS = 4
OLECMDID_SAVECOPYAS = 5
OLECMDID_PRINT = 6
OLECMDID_PRINTPREVIEW = 7
OLECMDID_PAGESETUP = 8
OLECMDID_SPELL = 9
OLECMDID_PROPERTIES = 10
OLECMDID_CUT = 11
OLECMDID_COPY = 12
OLECMDID_PASTE = 13
OLECMDID_PASTESPECIAL = 14
OLECMDID_UNDO = 15
OLECMDID_REDO = 16
OLECMDID_SELECTALL = 17
OLECMDID_CLEARSELECTION = 18
OLECMDID_ZOOM = 19
OLECMDID_GETZOOMRANGE = 20
OLECMDID_UPDATECOMMANDS = 21
OLECMDID_REFRESH = 22
OLECMDID_STOP = 23
OLECMDID_HIDETOOLBARS = 24
OLECMDID_SETPROGRESSMAX = 25
OLECMDID_SETPROGRESSPOS = 26
OLECMDID_SETPROGRESSTEXT = 27
OLECMDID_SETTITLE = 28
OLECMDID_SETDOWNLOADSTATE = 29
OLECMDID_STOPDOWNLOAD = 30
OLECMDID_ONTOOLBARACTIVATED = 31
OLECMDID_FIND = 32
OLECMDID_DELETE = 33
OLECMDID_HTTPEQUIV = 34
OLECMDID_HTTPEQUIV_DONE = 35
OLECMDID_ENABLE_INTERACTION = 36
OLECMDID_ONUNLOAD = 37
OLECMDID_PROPERTYBAG2 = 38
OLECMDID_PREREFRESH = 39
OLECMDID_SHOWSCRIPTERROR = 40
OLECMDID_SHOWMESSAGE = 41
OLECMDID_SHOWFIND = 42
OLECMDID_SHOWPAGESETUP = 43
OLECMDID_SHOWPRINT = 44
OLECMDID_CLOSE = 45
OLECMDID_ALLOWUILESSSAVEAS = 46
OLECMDID_DONTDOWNLOADCSS = 47
OLECMDID_UPDATEPAGESTATUS = 48
OLECMDID_PRINT2 = 49
OLECMDID_PRINTPREVIEW2 = 50
OLECMDID_SETPRINTTEMPLATE = 51
OLECMDID_GETPRINTTEMPLATE = 52
OLECMDID_PAGEACTIONBLOCKED = 55
OLECMDID_PAGEACTIONUIQUERY = 56
OLECMDID_FOCUSVIEWCONTROLS = 57
OLECMDID_FOCUSVIEWCONTROLSQUERY = 58
OLECMDID_SHOWPAGEACTIONMENU = 59
OLECMDID_ADDTRAVELENTRY = 60
OLECMDID_UPDATETRAVELENTRY = 61
OLECMDID_UPDATEBACKFORWARDSTATE = 62
OLECMDID_OPTICAL_ZOOM = 63
OLECMDID_OPTICAL_GETZOOMRANGE = 64
OLECMDID_WINDOWSTATECHANGED = 65
OLECMDID = c_int # enum
IWebBrowser2._methods_ = [
    COMMETHOD([dispid(500), helpstring(u'Navigates to a URL or file or pidl.')], HRESULT, 'Navigate2',
              ( ['in'], POINTER(VARIANT), 'URL' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Flags' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'TargetFrameName' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'PostData' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'Headers' )),
    COMMETHOD([dispid(501), helpstring(u'IOleCommandTarget::QueryStatus')], HRESULT, 'QueryStatusWB',
              ( ['in'], OLECMDID, 'cmdID' ),
              ( ['retval', 'out'], POINTER(OLECMDF), 'pcmdf' )),
    COMMETHOD([dispid(502), helpstring(u'IOleCommandTarget::Exec')], HRESULT, 'ExecWB',
              ( ['in'], OLECMDID, 'cmdID' ),
              ( ['in'], OLECMDEXECOPT, 'cmdexecopt' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'pvaIn' ),
              ( ['in', 'out', 'optional'], POINTER(VARIANT), 'pvaOut' )),
    COMMETHOD([dispid(503), helpstring(u'Set BrowserBar to Clsid')], HRESULT, 'ShowBrowserBar',
              ( ['in'], POINTER(VARIANT), 'pvaClsid' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'pvarShow' ),
              ( ['in', 'optional'], POINTER(VARIANT), 'pvarSize' )),
    COMMETHOD([dispid(-525), 'bindable', 'propget'], HRESULT, 'ReadyState',
              ( ['retval', 'out'], POINTER(tagREADYSTATE), 'plReadyState' )),
    COMMETHOD([dispid(550), helpstring(u'Controls if the frame is offline (read from cache)'), 'propget'], HRESULT, 'Offline',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pbOffline' )),
    COMMETHOD([dispid(550), helpstring(u'Controls if the frame is offline (read from cache)'), 'propput'], HRESULT, 'Offline',
              ( ['in'], VARIANT_BOOL, 'pbOffline' )),
    COMMETHOD([dispid(551), helpstring(u'Controls if any dialog boxes can be shown'), 'propget'], HRESULT, 'Silent',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pbSilent' )),
    COMMETHOD([dispid(551), helpstring(u'Controls if any dialog boxes can be shown'), 'propput'], HRESULT, 'Silent',
              ( ['in'], VARIANT_BOOL, 'pbSilent' )),
    COMMETHOD([dispid(552), helpstring(u'Registers OC as a top-level browser (for target name resolution)'), 'propget'], HRESULT, 'RegisterAsBrowser',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pbRegister' )),
    COMMETHOD([dispid(552), helpstring(u'Registers OC as a top-level browser (for target name resolution)'), 'propput'], HRESULT, 'RegisterAsBrowser',
              ( ['in'], VARIANT_BOOL, 'pbRegister' )),
    COMMETHOD([dispid(553), helpstring(u'Registers OC as a drop target for navigation'), 'propget'], HRESULT, 'RegisterAsDropTarget',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pbRegister' )),
    COMMETHOD([dispid(553), helpstring(u'Registers OC as a drop target for navigation'), 'propput'], HRESULT, 'RegisterAsDropTarget',
              ( ['in'], VARIANT_BOOL, 'pbRegister' )),
    COMMETHOD([dispid(554), helpstring(u'Controls if the browser is in theater mode'), 'propget'], HRESULT, 'TheaterMode',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pbRegister' )),
    COMMETHOD([dispid(554), helpstring(u'Controls if the browser is in theater mode'), 'propput'], HRESULT, 'TheaterMode',
              ( ['in'], VARIANT_BOOL, 'pbRegister' )),
    COMMETHOD([dispid(555), helpstring(u'Controls whether address bar is shown'), 'propget'], HRESULT, 'AddressBar',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'Value' )),
    COMMETHOD([dispid(555), helpstring(u'Controls whether address bar is shown'), 'propput'], HRESULT, 'AddressBar',
              ( ['in'], VARIANT_BOOL, 'Value' )),
    COMMETHOD([dispid(556), helpstring(u'Controls whether the window is resizable'), 'propget'], HRESULT, 'Resizable',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'Value' )),
    COMMETHOD([dispid(556), helpstring(u'Controls whether the window is resizable'), 'propput'], HRESULT, 'Resizable',
              ( ['in'], VARIANT_BOOL, 'Value' )),
]
################################################################
## code template for IWebBrowser2 implementation
##class IWebBrowser2_Impl(object):
##    @property
##    def ReadyState(self):
##        '-no docstring-'
##        #return plReadyState
##
##    def QueryStatusWB(self, cmdID):
##        u'IOleCommandTarget::QueryStatus'
##        #return pcmdf
##
##    def _get(self):
##        u'Controls if any dialog boxes can be shown'
##        #return pbSilent
##    def _set(self, pbSilent):
##        u'Controls if any dialog boxes can be shown'
##    Silent = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'Controls whether the window is resizable'
##        #return Value
##    def _set(self, Value):
##        u'Controls whether the window is resizable'
##    Resizable = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'Registers OC as a top-level browser (for target name resolution)'
##        #return pbRegister
##    def _set(self, pbRegister):
##        u'Registers OC as a top-level browser (for target name resolution)'
##    RegisterAsBrowser = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'Controls if the browser is in theater mode'
##        #return pbRegister
##    def _set(self, pbRegister):
##        u'Controls if the browser is in theater mode'
##    TheaterMode = property(_get, _set, doc = _set.__doc__)
##
##    def ShowBrowserBar(self, pvaClsid, pvarShow, pvarSize):
##        u'Set BrowserBar to Clsid'
##        #return 
##
##    def _get(self):
##        u'Registers OC as a drop target for navigation'
##        #return pbRegister
##    def _set(self, pbRegister):
##        u'Registers OC as a drop target for navigation'
##    RegisterAsDropTarget = property(_get, _set, doc = _set.__doc__)
##
##    def Navigate2(self, URL, Flags, TargetFrameName, PostData, Headers):
##        u'Navigates to a URL or file or pidl.'
##        #return 
##
##    def _get(self):
##        u'Controls if the frame is offline (read from cache)'
##        #return pbOffline
##    def _set(self, pbOffline):
##        u'Controls if the frame is offline (read from cache)'
##    Offline = property(_get, _set, doc = _set.__doc__)
##
##    def _get(self):
##        u'Controls whether address bar is shown'
##        #return Value
##    def _set(self, Value):
##        u'Controls whether address bar is shown'
##    AddressBar = property(_get, _set, doc = _set.__doc__)
##
##    def ExecWB(self, cmdID, cmdexecopt, pvaIn):
##        u'IOleCommandTarget::Exec'
##        #return pvaOut
##

DShellWindowsEvents._disp_methods_ = [
    DISPMETHOD([dispid(200), helpstring(u'A new window was registered.')], None, 'WindowRegistered',
               ( ['in'], c_int, 'lCookie' )),
    DISPMETHOD([dispid(201), helpstring(u'A new window was revoked.')], None, 'WindowRevoked',
               ( ['in'], c_int, 'lCookie' )),
]
class ShellShellNameSpace(CoClass):
    u'Shell ShellNameSpace Class'
    _reg_clsid_ = GUID('{2F2F1F96-2BC1-4B1C-BE28-EA3774F4676A}')
    _idlflags_ = []
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
ShellShellNameSpace._com_interfaces_ = [IShellNameSpace]
ShellShellNameSpace._outgoing_interfaces_ = [DShellNameSpaceEvents]

class InternetExplorer(CoClass):
    u'Internet Explorer Application.'
    _reg_clsid_ = GUID('{0002DF01-0000-0000-C000-000000000046}')
    _idlflags_ = []
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
InternetExplorer._com_interfaces_ = [IWebBrowser2, IWebBrowserApp]
InternetExplorer._outgoing_interfaces_ = [DWebBrowserEvents2, DWebBrowserEvents]


# values for enumeration 'CommandStateChangeConstants'
CSC_UPDATECOMMANDS = -1
CSC_NAVIGATEFORWARD = 1
CSC_NAVIGATEBACK = 2
CommandStateChangeConstants = c_int # enum
class WebBrowser(CoClass):
    u'WebBrowser Control'
    _reg_clsid_ = GUID('{8856F961-340A-11D0-A96B-00C04FD705A2}')
    _idlflags_ = ['control']
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
WebBrowser._com_interfaces_ = [IWebBrowser2, IWebBrowser]
WebBrowser._outgoing_interfaces_ = [DWebBrowserEvents2, DWebBrowserEvents]

IShellUIHelper2._methods_ = [
    COMMETHOD([dispid(14)], HRESULT, 'AddSearchProvider',
              ( ['in'], BSTR, 'URL' )),
    COMMETHOD([dispid(15)], HRESULT, 'RunOnceShown'),
    COMMETHOD([dispid(16)], HRESULT, 'SkipRunOnce'),
    COMMETHOD([dispid(17)], HRESULT, 'CustomizeSettings',
              ( ['in'], VARIANT_BOOL, 'fSQM' ),
              ( ['in'], VARIANT_BOOL, 'fPhishing' ),
              ( ['in'], BSTR, 'bstrLocale' )),
    COMMETHOD([dispid(18)], HRESULT, 'SqmEnabled',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pfEnabled' )),
    COMMETHOD([dispid(19)], HRESULT, 'PhishingEnabled',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pfEnabled' )),
    COMMETHOD([dispid(20)], HRESULT, 'BrandImageUri',
              ( ['retval', 'out'], POINTER(BSTR), 'pbstrUri' )),
    COMMETHOD([dispid(21)], HRESULT, 'SkipTabsWelcome'),
    COMMETHOD([dispid(22)], HRESULT, 'DiagnoseConnection'),
    COMMETHOD([dispid(23)], HRESULT, 'CustomizeClearType',
              ( ['in'], VARIANT_BOOL, 'fSet' )),
    COMMETHOD([dispid(24)], HRESULT, 'IsSearchProviderInstalled',
              ( ['in'], BSTR, 'URL' ),
              ( ['retval', 'out'], POINTER(c_ulong), 'pdwResult' )),
    COMMETHOD([dispid(25)], HRESULT, 'IsSearchMigrated',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pfMigrated' )),
    COMMETHOD([dispid(26)], HRESULT, 'DefaultSearchProvider',
              ( ['retval', 'out'], POINTER(BSTR), 'pbstrName' )),
    COMMETHOD([dispid(27)], HRESULT, 'RunOnceRequiredSettingsComplete',
              ( ['in'], VARIANT_BOOL, 'fComplete' )),
    COMMETHOD([dispid(28)], HRESULT, 'RunOnceHasShown',
              ( ['retval', 'out'], POINTER(VARIANT_BOOL), 'pfShown' )),
    COMMETHOD([dispid(29)], HRESULT, 'SearchGuideUrl',
              ( ['retval', 'out'], POINTER(BSTR), 'pbstrUrl' )),
]
################################################################
## code template for IShellUIHelper2 implementation
##class IShellUIHelper2_Impl(object):
##    def SkipRunOnce(self):
##        '-no docstring-'
##        #return 
##
##    def SkipTabsWelcome(self):
##        '-no docstring-'
##        #return 
##
##    def RunOnceRequiredSettingsComplete(self, fComplete):
##        '-no docstring-'
##        #return 
##
##    def PhishingEnabled(self):
##        '-no docstring-'
##        #return pfEnabled
##
##    def CustomizeSettings(self, fSQM, fPhishing, bstrLocale):
##        '-no docstring-'
##        #return 
##
##    def DefaultSearchProvider(self):
##        '-no docstring-'
##        #return pbstrName
##
##    def CustomizeClearType(self, fSet):
##        '-no docstring-'
##        #return 
##
##    def RunOnceShown(self):
##        '-no docstring-'
##        #return 
##
##    def BrandImageUri(self):
##        '-no docstring-'
##        #return pbstrUri
##
##    def DiagnoseConnection(self):
##        '-no docstring-'
##        #return 
##
##    def IsSearchProviderInstalled(self, URL):
##        '-no docstring-'
##        #return pdwResult
##
##    def SqmEnabled(self):
##        '-no docstring-'
##        #return pfEnabled
##
##    def SearchGuideUrl(self):
##        '-no docstring-'
##        #return pbstrUrl
##
##    def RunOnceHasShown(self):
##        '-no docstring-'
##        #return pfShown
##
##    def IsSearchMigrated(self):
##        '-no docstring-'
##        #return pfMigrated
##
##    def AddSearchProvider(self, URL):
##        '-no docstring-'
##        #return 
##

class ShellBrowserWindow(CoClass):
    u'Shell Browser Window.'
    _reg_clsid_ = GUID('{C08AFD90-F2A1-11D1-8455-00A0C91F3880}')
    _idlflags_ = ['hidden', 'noncreatable']
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
ShellBrowserWindow._com_interfaces_ = [IWebBrowser2, IWebBrowserApp]
ShellBrowserWindow._outgoing_interfaces_ = [DWebBrowserEvents2, DWebBrowserEvents]

DWebBrowserEvents._disp_methods_ = [
    DISPMETHOD([dispid(100), helpstring(u'Fired when a new hyperlink is being navigated to.')], None, 'BeforeNavigate',
               ( ['in'], BSTR, 'URL' ),
               ( [], c_int, 'Flags' ),
               ( [], BSTR, 'TargetFrameName' ),
               ( [], POINTER(VARIANT), 'PostData' ),
               ( [], BSTR, 'Headers' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' )),
    DISPMETHOD([dispid(101), helpstring(u'Fired when the document being navigated to becomes visible and enters the navigation stack.')], None, 'NavigateComplete',
               ( ['in'], BSTR, 'URL' )),
    DISPMETHOD([dispid(102), helpstring(u'Statusbar text changed.')], None, 'StatusTextChange',
               ( ['in'], BSTR, 'Text' )),
    DISPMETHOD([dispid(108), helpstring(u'Fired when download progress is updated.')], None, 'ProgressChange',
               ( ['in'], c_int, 'Progress' ),
               ( ['in'], c_int, 'ProgressMax' )),
    DISPMETHOD([dispid(104), helpstring(u'Download of page complete.')], None, 'DownloadComplete'),
    DISPMETHOD([dispid(105), helpstring(u'The enabled state of a command changed')], None, 'CommandStateChange',
               ( ['in'], c_int, 'Command' ),
               ( ['in'], VARIANT_BOOL, 'Enable' )),
    DISPMETHOD([dispid(106), helpstring(u'Download of a page started.')], None, 'DownloadBegin'),
    DISPMETHOD([dispid(107), helpstring(u'Fired when a new window should be created.')], None, 'NewWindow',
               ( ['in'], BSTR, 'URL' ),
               ( ['in'], c_int, 'Flags' ),
               ( ['in'], BSTR, 'TargetFrameName' ),
               ( ['in'], POINTER(VARIANT), 'PostData' ),
               ( ['in'], BSTR, 'Headers' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Processed' )),
    DISPMETHOD([dispid(113), helpstring(u'Document title changed.')], None, 'TitleChange',
               ( ['in'], BSTR, 'Text' )),
    DISPMETHOD([dispid(200), helpstring(u'Fired when a new hyperlink is being navigated to in a frame.')], None, 'FrameBeforeNavigate',
               ( ['in'], BSTR, 'URL' ),
               ( [], c_int, 'Flags' ),
               ( [], BSTR, 'TargetFrameName' ),
               ( [], POINTER(VARIANT), 'PostData' ),
               ( [], BSTR, 'Headers' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' )),
    DISPMETHOD([dispid(201), helpstring(u'Fired when a new hyperlink is being navigated to in a frame.')], None, 'FrameNavigateComplete',
               ( ['in'], BSTR, 'URL' )),
    DISPMETHOD([dispid(204), helpstring(u'Fired when a new window should be created.')], None, 'FrameNewWindow',
               ( ['in'], BSTR, 'URL' ),
               ( ['in'], c_int, 'Flags' ),
               ( ['in'], BSTR, 'TargetFrameName' ),
               ( ['in'], POINTER(VARIANT), 'PostData' ),
               ( ['in'], BSTR, 'Headers' ),
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Processed' )),
    DISPMETHOD([dispid(103), helpstring(u'Fired when application is quiting.')], None, 'Quit',
               ( ['in', 'out'], POINTER(VARIANT_BOOL), 'Cancel' )),
    DISPMETHOD([dispid(109), helpstring(u'Fired when window has been moved.')], None, 'WindowMove'),
    DISPMETHOD([dispid(110), helpstring(u'Fired when window has been sized.')], None, 'WindowResize'),
    DISPMETHOD([dispid(111), helpstring(u'Fired when window has been activated.')], None, 'WindowActivate'),
    DISPMETHOD([dispid(112), helpstring(u'Fired when the PutProperty method has been called.')], None, 'PropertyChange',
               ( ['in'], BSTR, 'Property' )),
]
class ShellNameSpace(CoClass):
    _reg_clsid_ = GUID('{55136805-B2DE-11D1-B9F2-00A0C98BC547}')
    _idlflags_ = []
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1)
ShellNameSpace._com_interfaces_ = [IShellNameSpace]
ShellNameSpace._outgoing_interfaces_ = [DShellNameSpaceEvents]

__all__ = ['OLECMDID_HTTPEQUIV', 'OLECMDID_SHOWSCRIPTERROR',
           'OLECMDID_OPTICAL_ZOOM', 'SWFO_COOKIEPASSED',
           'SWFO_INCLUDEPENDING', 'OLECMDID_OPEN', 'SWC_CALLBACK',
           'CSC_NAVIGATEFORWARD', 'OLECMDF_DEFHIDEONCTXTMENU',
           'SWC_BROWSER', 'OLECMDF', 'CSC_NAVIGATEBACK',
           'OLECMDID_REDO', 'OLECMDID_SETPRINTTEMPLATE',
           'IWebBrowser2', 'IShellNameSpace', 'SWC_EXPLORER',
           'OLECMDID_ONTOOLBARACTIVATED', 'OLECMDF_SUPPORTED',
           'CommandStateChangeConstants', 'OLECMDID',
           'OLECMDID_SHOWMESSAGE', 'IShellUIHelper',
           'OLECMDF_LATCHED', 'OLECMDID_UPDATEBACKFORWARDSTATE',
           'OLECMDID_GETZOOMRANGE', 'IScriptErrorList',
           'READYSTATE_LOADED', 'OLECMDEXECOPT_DODEFAULT',
           'ShellShellNameSpace', 'READYSTATE_INTERACTIVE',
           'secureLockIconSecureUnknownBits', 'IWebBrowser',
           'OLECMDF_INVISIBLE', 'OLECMDID_REFRESH',
           'OLECMDID_SHOWPAGESETUP', 'OLECMDID_STOPDOWNLOAD',
           'OLECMDID_SPELL', 'OLECMDID_PROPERTYBAG2',
           'OLECMDID_PROPERTIES', 'OLECMDID_PRINTPREVIEW2',
           'OLECMDID_UPDATECOMMANDS', 'ShellUIHelper',
           'OLECMDID_PRINT', 'OLECMDID_SETPROGRESSTEXT',
           'OLECMDID_DELETE', 'IShellWindows',
           'OLECMDID_SHOWPAGEACTIONMENU',
           'OLECMDID_FOCUSVIEWCONTROLSQUERY', 'DShellNameSpaceEvents',
           'tagREADYSTATE', 'OLECMDID_PRINTPREVIEW',
           'ShellWindowTypeConstants', 'ShellWindows',
           'OLECMDID_PRINT2', 'CSC_UPDATECOMMANDS', 'OLECMDID_SAVE',
           'OLECMDEXECOPT', 'OLECMDID_ONUNLOAD',
           'OLECMDID_PASTESPECIAL', 'OLECMDID_UNDO',
           'IShellUIHelper2', 'SWFO_NEEDDISPATCH',
           'secureLockIconSecure40Bit', 'OLECMDID_UPDATETRAVELENTRY',
           'OLECMDID_UPDATEPAGESTATUS', 'SWC_DESKTOP',
           'OLECMDID_HIDETOOLBARS', 'OLECMDID_PAGEACTIONBLOCKED',
           'ShellNameSpace', 'SWC_3RDPARTY', 'IWebBrowserApp',
           'OLECMDID_ZOOM', 'OLECMDID_SAVECOPYAS',
           'OLECMDID_ALLOWUILESSSAVEAS',
           'OLECMDID_WINDOWSTATECHANGED', 'DWebBrowserEvents2',
           'OLECMDID_CUT', 'OLECMDID_PASTE',
           'OLECMDID_OPTICAL_GETZOOMRANGE', 'OLECMDID_FIND',
           'OLECMDID_CLEARSELECTION', 'OLECMDID_SETTITLE',
           'OLECMDID_SHOWPRINT', 'secureLockIconSecure128Bit',
           'OLECMDID_SHOWFIND', 'READYSTATE_UNINITIALIZED',
           'OLECMDID_PAGESETUP', 'OLECMDID_FOCUSVIEWCONTROLS',
           'READYSTATE_COMPLETE', 'OLECMDF_ENABLED',
           'SecureLockIconConstants', 'InternetExplorer',
           'ShellWindowFindWindowOptions', 'OLECMDID_CLOSE',
           'OLECMDF_NINCHED', 'OLECMDID_SETPROGRESSPOS',
           'IShellFavoritesNameSpace', 'OLECMDID_GETPRINTTEMPLATE',
           'OLECMDEXECOPT_DONTPROMPTUSER', 'DWebBrowserEvents',
           'OLECMDEXECOPT_PROMPTUSER', 'WebBrowser',
           'secureLockIconMixed', 'OLECMDID_SETPROGRESSMAX',
           'READYSTATE_LOADING', 'OLECMDID_SAVEAS',
           'OLECMDID_SELECTALL', 'secureLockIconSecure56Bit',
           'ShellBrowserWindow', 'OLECMDID_NEW',
           'DShellWindowsEvents', 'WebBrowser_V1',
           'secureLockIconUnsecure', 'OLECMDID_STOP',
           'OLECMDID_SETDOWNLOADSTATE', 'CScriptErrorList',
           'OLECMDID_HTTPEQUIV_DONE', 'OLECMDEXECOPT_SHOWHELP',
           'OLECMDID_COPY', 'OLECMDID_DONTDOWNLOADCSS',
           'OLECMDID_PREREFRESH', 'OLECMDID_ADDTRAVELENTRY',
           'OLECMDID_ENABLE_INTERACTION',
           'OLECMDID_PAGEACTIONUIQUERY',
           'secureLockIconSecureFortezza']
