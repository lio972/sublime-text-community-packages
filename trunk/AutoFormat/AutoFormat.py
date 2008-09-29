import sublime, sublimeplugin
import re
import os
from ctypes import *

malloc = cdll.msvcrt.malloc
malloc.restype = POINTER(c_double)
free = cdll.msvcrt.free

# // astyle ASTYLE_LIB declarations
# typedef void (STDCALL *fpError)(int, char*);       // pointer to callback error handler
# typedef char* (STDCALL *fpAlloc)(unsigned long);   // pointer to callback memory allocation
# extern "C" EXPORT char* STDCALL AStyleMain(const char*, const char*, fpError, fpAlloc);
# extern "C" EXPORT const char* STDCALL AStyleGetVersion (void);

# AStyleMain (addr)0x1000aac0 (rel addr)0x0000aac0 (ordinal)2

def ErrorHandler(size, str):
	print "[callback error handler] size:%d str:%s" % (size, str)

ErrorHandlerCallback = WINFUNCTYPE(None, c_int, c_char_p)
ERROR_HANDLER = ErrorHandlerCallback(ErrorHandler)

allocated = []
def MemoryAllocation(size):
   	arr_type = c_double * size
   	x = arr_type()
   	allocated.append(x)
   	ptr = addressof(x)
	#print "[callback memory allocation] size:%d ptr:%x" % (size, ptr)   
   	return ptr	
	
MemoryAllocationCallback = WINFUNCTYPE(c_char_p, c_ulong) 
MEMORY_ALLOCATION = MemoryAllocationCallback(MemoryAllocation)

class AutoFormatCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		path = sublime.packagesPath()
		path = os.path.join(path, "User")
		dll = os.path.join(path, "AStyle.dll")

		# if the function name has a @ followed by number it probably uses the stdcall calling convention. 
		libc = windll.LoadLibrary(dll)
		astyle_main = libc[2]
		astyle_main.restype = c_char_p
		astyle_main.argtypes = [c_char_p, c_char_p, ErrorHandlerCallback, MemoryAllocationCallback]
		
		region = sublime.Region(0L, view.size())
		select_all = view.substr(region)
		pretty_code = astyle_main(select_all, "", ERROR_HANDLER, MEMORY_ALLOCATION)
		view.replace(region, pretty_code)
		
	def isEnabled(self, view, args):
		lang = re.search(".*/([^/]*)\.tmLanguage$", view.options().getString("syntax")).group(1)
		lang = lang.lower()
		if lang == "c" or lang == "c++" or lang == "c#" or lang == "java":
			return True
		else:
			return False
