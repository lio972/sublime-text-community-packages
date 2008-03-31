import sublime, sublimeplugin, packagedownloader

# import stuff to allow messageboxes
from ctypes import c_int, WINFUNCTYPE, windll
from ctypes.wintypes import HWND, LPCSTR, UINT
prototype = WINFUNCTYPE(c_int, HWND, LPCSTR, LPCSTR, UINT)
paramflags = (1, "hwnd", 0), (1, "text", "Hi"), (1, "caption", None), (1, "flags", 0)
MessageBox = prototype(("MessageBoxA", windll.user32), paramflags)

class DownloadPackagesOnSublimeTextWikiCommand(sublimeplugin.ApplicationCommand):
  
  name = "Package Downloader"
  
  def run(self, args):
    packageList = packagedownloader.downloadPackages()
    if len(packageList) == 0:
      MessageBox(text="No Packages Downloaded", caption=self.name)
    else:
      MessageBox(text="Downloaded these packages;\n\n  " + str.join("\n  ", packageList) + "\n\nPackages will be installed next time you start Sublime Text.", caption=self.name)
