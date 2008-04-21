# Work in progress.  Need to refactor (IStorage, IStream, maybe more)
from ctypes import *

WSTRING = c_wchar_p

from comtypes import COMMETHOD
from comtypes import GUID
from comtypes import IUnknown
from comtypes import _GUID
from comtypes import tagBIND_OPTS

from comtypes.persist import IPersist

from ctypes.wintypes import _FILETIME
from ctypes.wintypes import _LARGE_INTEGER
from ctypes.wintypes import _ULARGE_INTEGER


class IEnumString(IUnknown):
    _iid_ = GUID('{00000101-0000-0000-C000-000000000046}')
    _idlflags_ = []
    def __iter__(self):
        return self

    def next(self):
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise StopIteration

    def __getitem__(self, index):
        self.Reset()
        self.Skip(index)
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise IndexError, index

IEnumString._methods_ = [
    COMMETHOD([], HRESULT, 'Next',
              ( ['in'], c_ulong, 'celt' ),
              ( ['out'], POINTER(WSTRING), 'rgelt' ),
              ( ['out'], POINTER(c_ulong), 'pceltFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'celt' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IEnumString)), 'ppenum' )),
]
class tagSTATSTG(Structure):
    pass
tagSTATSTG._fields_ = [
    ('pwcsName', WSTRING),
    ('type', c_ulong),
    ('cbSize', _ULARGE_INTEGER),
    ('mtime', _FILETIME),
    ('ctime', _FILETIME),
    ('atime', _FILETIME),
    ('grfMode', c_ulong),
    ('grfLocksSupported', c_ulong),
    ('clsid', _GUID),
    ('grfStateBits', c_ulong),
    ('reserved', c_ulong),
]
class IPersistStream(IPersist):
    _iid_ = GUID('{00000109-0000-0000-C000-000000000046}')
    _idlflags_ = []
class IPersistStreamInit(IPersist):
    _iid_ = GUID('{7FD52380-4E07-101B-AE2D-08002B2EC713}')
    _idlflags_ = []
class ISequentialStream(IUnknown):
    _iid_ = GUID('{0C733A30-2A1C-11CE-ADE5-00AA0044773D}')
    _idlflags_ = []
class IStream(ISequentialStream):
    _iid_ = GUID('{0000000C-0000-0000-C000-000000000046}')
    _idlflags_ = []
IPersistStream._methods_ = [
    COMMETHOD([], HRESULT, 'IsDirty'),
    COMMETHOD([], HRESULT, 'Load',
              ( ['in'], POINTER(IStream), 'pstm' )),
    COMMETHOD([], HRESULT, 'Save',
              ( ['in'], POINTER(IStream), 'pstm' ),
              ( ['in'], c_int, 'fClearDirty' )),
    COMMETHOD([], HRESULT, 'GetSizeMax',
              ( ['out'], POINTER(_ULARGE_INTEGER), 'pcbSize' )),
]
IPersistStreamInit._methods_ = [
    COMMETHOD([], HRESULT, 'IsDirty'),
    COMMETHOD([], HRESULT, 'Load',
              ( ['in'], POINTER(IStream), 'pstm' )),
    COMMETHOD([], HRESULT, 'Save',
              ( ['in'], POINTER(IStream), 'pstm' ),
              ( ['in'], c_int, 'fClearDirty' )),
    COMMETHOD([], HRESULT, 'GetSizeMax',
              ( ['out'], POINTER(_ULARGE_INTEGER), 'pcbSize' )),
    COMMETHOD([], HRESULT, 'InitNew'),
]
class __MIDL_IAdviseSink_0001(Union):
    pass
class IStorage(IUnknown):
    _iid_ = GUID('{0000000B-0000-0000-C000-000000000046}')
    _idlflags_ = []
__MIDL_IAdviseSink_0001._fields_ = [
    ('hBitmap', c_void_p),
    ('hMetaFilePict', c_void_p),
    ('hEnhMetaFile', c_void_p),
    ('hGlobal', c_void_p),
    ('lpszFileName', WSTRING),
    ('pstm', POINTER(IStream)),
    ('pstg', POINTER(IStorage)),
]
class IEnumMoniker(IUnknown):
    _iid_ = GUID('{00000102-0000-0000-C000-000000000046}')
    _idlflags_ = []
    def __iter__(self):
        return self

    def next(self):
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise StopIteration

    def __getitem__(self, index):
        self.Reset()
        self.Skip(index)
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise IndexError, index

class IMoniker(IPersistStream):
    _iid_ = GUID('{0000000F-0000-0000-C000-000000000046}')
    _idlflags_ = []
IEnumMoniker._methods_ = [
    COMMETHOD([], HRESULT, 'Next',
              ( ['in'], c_ulong, 'celt' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'rgelt' ),
              ( ['out'], POINTER(c_ulong), 'pceltFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'celt' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IEnumMoniker)), 'ppenum' )),
]
class IDataObject(IUnknown):
    _iid_ = GUID('{0000010E-0000-0000-C000-000000000046}')
    _idlflags_ = []
class tagFORMATETC(Structure):
    def __repr__(self):
        return "<FORMATETC cfFormat=%d, dwAspect=%d, lindex=%d, tymed=%d>" % \
               (self.cfFormat, self.dwAspect, self.lindex, self.tymed)
##        ('cfFormat', c_ushort),
##        ('ptd', POINTER(tagDVTARGETDEVICE)),
##        ('dwAspect', c_ulong),
##        ('lindex', c_int),
##        ('tymed', c_ulong),
FORMATETC = tagFORMATETC

class tagSTGMEDIUM(Structure):
    def __repr__(self):
        return "<STGMEDIUM tymed=%d>" % self.tymed
##    ('tymed', c_ulong),
##    ('__MIDL_0001', __MIDL_IAdviseSink_0001),
##    ('pUnkForRelease', POINTER(IUnknown)),
STGMEDIUM = tagSTGMEDIUM

class IEnumFORMATETC(IUnknown):
    _iid_ = GUID('{00000103-0000-0000-C000-000000000046}')
    _idlflags_ = []
    def __iter__(self):
        return self

    def next(self):
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise StopIteration

    def __getitem__(self, index):
        self.Reset()
        self.Skip(index)
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise IndexError, index

class IAdviseSink(IUnknown):
    _iid_ = GUID('{0000010F-0000-0000-C000-000000000046}')
    _idlflags_ = []
class IEnumSTATDATA(IUnknown):
    _iid_ = GUID('{00000105-0000-0000-C000-000000000046}')
    _idlflags_ = []
    def __iter__(self):
        return self

    def next(self):
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise StopIteration

    def __getitem__(self, index):
        self.Reset()
        self.Skip(index)
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise IndexError, index

IDataObject._methods_ = [
    COMMETHOD([], HRESULT, 'GetData',
              ( ['in'], POINTER(tagFORMATETC), 'pformatetcIn' ),
              ( ['out'], POINTER(tagSTGMEDIUM), 'pmedium' )),
    COMMETHOD([], HRESULT, 'GetDataHere',
              ( ['in'], POINTER(tagFORMATETC), 'pformatetc' ),
              ( ['in', 'out'], POINTER(tagSTGMEDIUM), 'pmedium' )),
    COMMETHOD([], HRESULT, 'QueryGetData',
              ( ['in'], POINTER(tagFORMATETC), 'pformatetc' )),
    COMMETHOD([], HRESULT, 'GetCanonicalFormatEtc',
              ( ['in'], POINTER(tagFORMATETC), 'pformatectIn' ),
              ( ['out'], POINTER(tagFORMATETC), 'pformatetcOut' )),
    COMMETHOD([], HRESULT, 'SetData',
              ( ['in'], POINTER(tagFORMATETC), 'pformatetc' ),
              ( ['in'], POINTER(tagSTGMEDIUM), 'pmedium' ),
              ( ['in'], c_int, 'fRelease' )),
    COMMETHOD([], HRESULT, 'EnumFormatEtc',
              ( ['in'], c_ulong, 'dwDirection' ),
              ( ['out'], POINTER(POINTER(IEnumFORMATETC)), 'ppenumFormatEtc' )),
    COMMETHOD([], HRESULT, 'DAdvise',
              ( ['in'], POINTER(tagFORMATETC), 'pformatetc' ),
              ( ['in'], c_ulong, 'advf' ),
              ( ['in'], POINTER(IAdviseSink), 'pAdvSink' ),
              ( ['out'], POINTER(c_ulong), 'pdwConnection' )),
    COMMETHOD([], HRESULT, 'DUnadvise',
              ( ['in'], c_ulong, 'dwConnection' )),
    COMMETHOD([], HRESULT, 'EnumDAdvise',
              ( ['out'], POINTER(POINTER(IEnumSTATDATA)), 'ppenumAdvise' )),
]
IAdviseSink._methods_ = [
    COMMETHOD([], None, 'OnDataChange',
              ( ['in'], POINTER(tagFORMATETC), 'pformatetc' ),
              ( ['in'], POINTER(tagSTGMEDIUM), 'pStgmed' )),
    COMMETHOD([], None, 'OnViewChange',
              ( ['in'], c_ulong, 'dwAspect' ),
              ( ['in'], c_int, 'lindex' )),
    COMMETHOD([], None, 'OnRename',
              ( ['in'], POINTER(IMoniker), 'pmk' )),
    COMMETHOD([], None, 'OnSave'),
    COMMETHOD([], None, 'OnClose'),
]
class IRunningObjectTable(IUnknown):
    _iid_ = GUID('{00000010-0000-0000-C000-000000000046}')
    _idlflags_ = []
IRunningObjectTable._methods_ = [
    COMMETHOD([], HRESULT, 'Register',
              ( ['in'], c_ulong, 'grfFlags' ),
              ( ['in'], POINTER(IUnknown), 'punkObject' ),
              ( ['in'], POINTER(IMoniker), 'pmkObjectName' ),
              ( ['out'], POINTER(c_ulong), 'pdwRegister' )),
    COMMETHOD([], HRESULT, 'Revoke',
              ( ['in'], c_ulong, 'dwRegister' )),
    COMMETHOD([], HRESULT, 'IsRunning',
              ( ['in'], POINTER(IMoniker), 'pmkObjectName' )),
    COMMETHOD([], HRESULT, 'GetObject',
              ( ['in'], POINTER(IMoniker), 'pmkObjectName' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppunkObject' )),
    COMMETHOD([], HRESULT, 'NoteChangeTime',
              ( ['in'], c_ulong, 'dwRegister' ),
              ( ['in'], POINTER(_FILETIME), 'pfiletime' )),
    COMMETHOD([], HRESULT, 'GetTimeOfLastChange',
              ( ['in'], POINTER(IMoniker), 'pmkObjectName' ),
              ( ['out'], POINTER(_FILETIME), 'pfiletime' )),
    COMMETHOD([], HRESULT, 'EnumRunning',
              ( ['out'], POINTER(POINTER(IEnumMoniker)), 'ppenumMoniker' )),
]
class tagDVTARGETDEVICE(Structure):
    pass
tagFORMATETC._fields_ = [
    ('cfFormat', c_ushort),
    ('ptd', POINTER(tagDVTARGETDEVICE)),
    ('dwAspect', c_ulong),
    ('lindex', c_int),
    ('tymed', c_ulong),
]
tagDVTARGETDEVICE._fields_ = [
    ('tdSize', c_ulong),
    ('tdDriverNameOffset', c_ushort),
    ('tdDeviceNameOffset', c_ushort),
    ('tdPortNameOffset', c_ushort),
    ('tdExtDevmodeOffset', c_ushort),
    ('tdData', POINTER(c_ubyte)),
]
class IEnumSTATSTG(IUnknown):
    _iid_ = GUID('{0000000D-0000-0000-C000-000000000046}')
    _idlflags_ = []
    def __iter__(self):
        return self

    def next(self):
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise StopIteration

    def __getitem__(self, index):
        self.Reset()
        self.Skip(index)
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise IndexError, index

IStorage._methods_ = [
    COMMETHOD([], HRESULT, 'CreateStream',
              ( ['in'], WSTRING, 'pwcsName' ),
              ( ['in'], c_ulong, 'grfMode' ),
              ( ['in'], c_ulong, 'reserved1' ),
              ( ['in'], c_ulong, 'reserved2' ),
              ( ['out'], POINTER(POINTER(IStream)), 'ppstm' )),
    COMMETHOD([], HRESULT, 'OpenStream',
              ( ['in'], WSTRING, 'pwcsName' ),
              ( ['in'], c_void_p, 'reserved1' ),
              ( ['in'], c_ulong, 'grfMode' ),
              ( ['in'], c_ulong, 'reserved2' ),
              ( ['out'], POINTER(POINTER(IStream)), 'ppstm' )),
    COMMETHOD([], HRESULT, 'CreateStorage',
              ( ['in'], WSTRING, 'pwcsName' ),
              ( ['in'], c_ulong, 'grfMode' ),
              ( ['in'], c_ulong, 'reserved1' ),
              ( ['in'], c_ulong, 'reserved2' ),
              ( ['out'], POINTER(POINTER(IStorage)), 'ppstg' )),
    COMMETHOD([], HRESULT, 'OpenStorage',
              ( ['in'], WSTRING, 'pwcsName' ),
              ( ['in'], POINTER(IStorage), 'pstgPriority' ),
              ( ['in'], c_ulong, 'grfMode' ),
              ( ['in'], POINTER(POINTER(c_short)), 'snbExclude' ),
              ( ['in'], c_ulong, 'reserved' ),
              ( ['out'], POINTER(POINTER(IStorage)), 'ppstg' )),
    COMMETHOD([], HRESULT, 'CopyTo',
              ( ['in'], c_ulong, 'ciidExclude' ),
              ( ['in'], POINTER(_GUID), 'rgiidExclude' ),
              ( ['in'], POINTER(POINTER(c_short)), 'snbExclude' ),
              ( ['in'], POINTER(IStorage), 'pstgDest' )),
    COMMETHOD([], HRESULT, 'MoveElementTo',
              ( ['in'], WSTRING, 'pwcsName' ),
              ( ['in'], POINTER(IStorage), 'pstgDest' ),
              ( ['in'], WSTRING, 'pwcsNewName' ),
              ( ['in'], c_ulong, 'grfFlags' )),
    COMMETHOD([], HRESULT, 'Commit',
              ( ['in'], c_ulong, 'grfCommitFlags' )),
    COMMETHOD([], HRESULT, 'Revert'),
    COMMETHOD([], HRESULT, 'EnumElements',
              ( ['in'], c_ulong, 'reserved1' ),
              ( ['in'], c_void_p, 'reserved2' ),
              ( ['in'], c_ulong, 'reserved3' ),
              ( ['out'], POINTER(POINTER(IEnumSTATSTG)), 'ppenum' )),
    COMMETHOD([], HRESULT, 'DestroyElement',
              ( ['in'], WSTRING, 'pwcsName' )),
    COMMETHOD([], HRESULT, 'RenameElement',
              ( ['in'], WSTRING, 'pwcsOldName' ),
              ( ['in'], WSTRING, 'pwcsNewName' )),
    COMMETHOD([], HRESULT, 'SetElementTimes',
              ( ['in'], WSTRING, 'pwcsName' ),
              ( ['in'], POINTER(_FILETIME), 'pctime' ),
              ( ['in'], POINTER(_FILETIME), 'patime' ),
              ( ['in'], POINTER(_FILETIME), 'pmtime' )),
    COMMETHOD([], HRESULT, 'SetClass',
              ( ['in'], POINTER(_GUID), 'clsid' )),
    COMMETHOD([], HRESULT, 'SetStateBits',
              ( ['in'], c_ulong, 'grfStateBits' ),
              ( ['in'], c_ulong, 'grfMask' )),
    COMMETHOD([], HRESULT, 'Stat',
              ( ['out'], POINTER(tagSTATSTG), 'pstatstg' ),
              ( ['in'], c_ulong, 'grfStatFlag' )),
]
IEnumSTATSTG._methods_ = [
    COMMETHOD([], HRESULT, 'Next',
              ( ['in'], c_ulong, 'celt' ),
              ( ['out'], POINTER(tagSTATSTG), 'rgelt' ),
              ( ['out'], POINTER(c_ulong), 'pceltFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'celt' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IEnumSTATSTG)), 'ppenum' )),
]
class tagSTATDATA(Structure):
    pass
IEnumSTATDATA._methods_ = [
    COMMETHOD([], HRESULT, 'Next',
              ( ['in'], c_ulong, 'celt' ),
              ( ['out'], POINTER(tagSTATDATA), 'rgelt' ),
              ( ['out'], POINTER(c_ulong), 'pceltFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'celt' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IEnumSTATDATA)), 'ppenum' )),
]
class IBindCtx(IUnknown):
    _iid_ = GUID('{0000000E-0000-0000-C000-000000000046}')
    _idlflags_ = []
IMoniker._methods_ = [
    COMMETHOD([], HRESULT, 'BindToObject',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['in'], POINTER(_GUID), 'riidResult' ),
              ( ['out'], POINTER(c_void_p), 'ppvResult' )),
    COMMETHOD([], HRESULT, 'BindToStorage',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['in'], POINTER(_GUID), 'riid' ),
              ( ['out'], POINTER(c_void_p), 'ppvObj' )),
    COMMETHOD([], HRESULT, 'Reduce',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], c_ulong, 'dwReduceHowFar' ),
              ( ['in', 'out'], POINTER(POINTER(IMoniker)), 'ppmkToLeft' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkReduced' )),
    COMMETHOD([], HRESULT, 'ComposeWith',
              ( ['in'], POINTER(IMoniker), 'pmkRight' ),
              ( ['in'], c_int, 'fOnlyIfNotGeneric' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkComposite' )),
    COMMETHOD([], HRESULT, 'Enum',
              ( ['in'], c_int, 'fForward' ),
              ( ['out'], POINTER(POINTER(IEnumMoniker)), 'ppenumMoniker' )),
    COMMETHOD([], HRESULT, 'IsEqual',
              ( ['in'], POINTER(IMoniker), 'pmkOtherMoniker' )),
    COMMETHOD([], HRESULT, 'Hash',
              ( ['out'], POINTER(c_ulong), 'pdwHash' )),
    COMMETHOD([], HRESULT, 'IsRunning',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['in'], POINTER(IMoniker), 'pmkNewlyRunning' )),
    COMMETHOD([], HRESULT, 'GetTimeOfLastChange',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['out'], POINTER(_FILETIME), 'pfiletime' )),
    COMMETHOD([], HRESULT, 'Inverse',
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmk' )),
    COMMETHOD([], HRESULT, 'CommonPrefixWith',
              ( ['in'], POINTER(IMoniker), 'pmkOther' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkPrefix' )),
    COMMETHOD([], HRESULT, 'RelativePathTo',
              ( ['in'], POINTER(IMoniker), 'pmkOther' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkRelPath' )),
    COMMETHOD([], HRESULT, 'GetDisplayName',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['out'], POINTER(WSTRING), 'ppszDisplayName' )),
    COMMETHOD([], HRESULT, 'ParseDisplayName',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['in'], WSTRING, 'pszDisplayName' ),
              ( ['out'], POINTER(c_ulong), 'pchEaten' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkOut' )),
    COMMETHOD([], HRESULT, 'IsSystemMoniker',
              ( ['out'], POINTER(c_ulong), 'pdwMksys' )),
]
ISequentialStream._methods_ = [
    COMMETHOD([], HRESULT, 'Read',
              ( ['out'], c_void_p, 'pv' ),
              ( ['in'], c_ulong, 'cb' ),
              ( ['out'], POINTER(c_ulong), 'pcbRead' )),
    COMMETHOD([], HRESULT, 'Write',
              ( ['in'], c_void_p, 'pv' ),
              ( ['in'], c_ulong, 'cb' ),
              ( ['out'], POINTER(c_ulong), 'pcbWritten' )),
]
IStream._methods_ = [
    COMMETHOD([], HRESULT, 'Seek',
              ( ['in'], _LARGE_INTEGER, 'dlibMove' ),
              ( ['in'], c_ulong, 'dwOrigin' ),
              ( ['out'], POINTER(_ULARGE_INTEGER), 'plibNewPosition' )),
    COMMETHOD([], HRESULT, 'SetSize',
              ( ['in'], _ULARGE_INTEGER, 'libNewSize' )),
    COMMETHOD([], HRESULT, 'CopyTo',
              ( ['in'], POINTER(IStream), 'pstm' ),
              ( ['in'], _ULARGE_INTEGER, 'cb' ),
              ( ['out'], POINTER(_ULARGE_INTEGER), 'pcbRead' ),
              ( ['out'], POINTER(_ULARGE_INTEGER), 'pcbWritten' )),
    COMMETHOD([], HRESULT, 'Commit',
              ( ['in'], c_ulong, 'grfCommitFlags' )),
    COMMETHOD([], HRESULT, 'Revert'),
    COMMETHOD([], HRESULT, 'LockRegion',
              ( ['in'], _ULARGE_INTEGER, 'libOffset' ),
              ( ['in'], _ULARGE_INTEGER, 'cb' ),
              ( ['in'], c_ulong, 'dwLockType' )),
    COMMETHOD([], HRESULT, 'UnlockRegion',
              ( ['in'], _ULARGE_INTEGER, 'libOffset' ),
              ( ['in'], _ULARGE_INTEGER, 'cb' ),
              ( ['in'], c_ulong, 'dwLockType' )),
    COMMETHOD([], HRESULT, 'Stat',
              ( ['out'], POINTER(tagSTATSTG), 'pstatstg' ),
              ( ['in'], c_ulong, 'grfStatFlag' )),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IStream)), 'ppstm' )),
]
tagSTATDATA._fields_ = [
    ('formatetc', tagFORMATETC),
    ('advf', c_ulong),
    ('pAdvSink', POINTER(IAdviseSink)),
    ('dwConnection', c_ulong),
]
tagSTGMEDIUM._anonymous_ = ['_']
tagSTGMEDIUM._fields_ = [
    ('tymed', c_ulong),
    ('_', __MIDL_IAdviseSink_0001),
    ('pUnkForRelease', POINTER(IUnknown)),
]
IEnumFORMATETC._methods_ = [
    COMMETHOD([], HRESULT, 'Next',
              ( ['in'], c_ulong, 'celt' ),
              ( ['out'], POINTER(tagFORMATETC), 'rgelt' ),
              ( ['out'], POINTER(c_ulong), 'pceltFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'celt' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IEnumFORMATETC)), 'ppenum' )),
]
IBindCtx._methods_ = [
    COMMETHOD([], HRESULT, 'RegisterObjectBound',
              ( ['in'], POINTER(IUnknown), 'punk' )),
    COMMETHOD([], HRESULT, 'RevokeObjectBound',
              ( ['in'], POINTER(IUnknown), 'punk' )),
    COMMETHOD([], HRESULT, 'ReleaseBoundObjects'),
    COMMETHOD([], HRESULT, 'SetBindOptions',
              ( ['in'], POINTER(tagBIND_OPTS), 'pbindopts' )),
    COMMETHOD([], HRESULT, 'GetBindOptions',
              ( ['in', 'out'], POINTER(tagBIND_OPTS), 'pbindopts' )),
    COMMETHOD([], HRESULT, 'GetRunningObjectTable',
              ( ['out'], POINTER(POINTER(IRunningObjectTable)), 'pprot' )),
    COMMETHOD([], HRESULT, 'RegisterObjectParam',
              ( ['in'], WSTRING, 'pszKey' ),
              ( ['in'], POINTER(IUnknown), 'punk' )),
    COMMETHOD([], HRESULT, 'GetObjectParam',
              ( ['in'], WSTRING, 'pszKey' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppunk' )),
    COMMETHOD([], HRESULT, 'EnumObjectParam',
              ( ['out'], POINTER(POINTER(IEnumString)), 'ppenum' )),
    COMMETHOD([], HRESULT, 'RevokeObjectParam',
              ( ['in'], WSTRING, 'pszKey' )),
]
__all__ = ['IStorage', 'tagSTATDATA', 'IEnumString', 'IBindCtx',
           'IStream', 'IEnumSTATDATA', 'IRunningObjectTable',
           'IAdviseSink', 'IMoniker', 'IPersistStream',
           'tagFORMATETC', 'IDataObject', 'IEnumSTATSTG',
           'tagDVTARGETDEVICE', 'tagSTGMEDIUM', 'tagSTATSTG',
           'IEnumMoniker', '__MIDL_IAdviseSink_0001',
           'ISequentialStream', 'IEnumFORMATETC']
