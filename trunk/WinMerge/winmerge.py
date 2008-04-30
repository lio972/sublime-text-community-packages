import sublime, sublimeplugin
from subprocess import Popen

WINMERGE = '"C:\Program Files\WinMerge\WinMergeU.exe"'
OPTIONS = "/e /x /s /ub"

# /r  tells WinMerge to compare folders recursively . Normally WinMerge does 
#     not compare subfolder contents but does the "flat" compare showing the
#     files in compared folders and subfolders as separate items. Using /r 
#     tells WinMerge to compare all files in all subfolders. When subfolders 
#     are included, only unique subfolders are visible as separate items in 
#     compare results. Note that including subfolders can increase compare 
#     time remarkably. 

# /e  allows WinMerge to be closed with a single Esc keypress. This is useful
#     when using WinMerge as an external compare application. WinMerge can act 
#     like an dialog which is easy and fast to close. 


# /f  allows selecting filter used. Filter can be filemask like "*.h *.cpp" 
#     or name of filefilter like "XML/HTML Devel". Quotation marks must be used 
#     if filter mask or name contains spaces. 

# /x  closes WinMerge if opened files are identical (after information dialog is 
#     shown). This parameter is useful when WinMerge is used as an external 
#     compare application. It helps to faster process and/or ignore files which don't
#     have any differences. Note that this option does not apply when files become 
#     identical when merging/editing them. 

# /s  enables single-instance behavior. If there is already WinMerge running
#     new compare is opened to that same instance. Depending on other settings (
#     if multiple windows are allowed) new compare is opened to existing or new window. 

# /ul tells WinMerge to not add left path to MRU. External applications should 
#     not add paths to Open-dialog's MRU lists. 

# /ur tells WinMerge to not add right path to MRU. External applications should 
#     not add paths to Open-dialog's MRU lists. 

# /ub tells WinMerge to not add both paths to MRU. External applications should 
#     not add paths to Open-dialog's MRU lists. 

# /wl initially opens left side as read-only. Use this when you don't 
#     want to change left-side items in compare. 

# /wr initially opens right side as read-only. Use this when you don't 
#     want to change right-side items in compare. 

# /minimize starts WinMerge as minimized. This option can be used to start WinMerge
#     minimized for lengthy compares. 

# /maximize starts WinMerge as maximized. 

# /dl adds a description for left side shown instead of folder / filename. 
#     This allows showing version number or label for compared items. Like 
#     "Version 1.0" or "Work Copy". 

# /dr adds a description for right side shown instead of folder / filename. 
#     This allows showing version number or label for compared items. Like 
#     "Version 1.0" or "Work Copy". 

# leftpath is the folder or filename to open on the left side. 

# rightpath is the folder or filename to open on the right side. 

# outputpath is an optional output folder where you want merged files to be saved. 


class WinMergeCommand(sublimeplugin.TextCommand):
    file1 = None
    file2 = None
    
    def run(self, view, args):
        if not self.file1:
            self.file1 = view.fileName()
            if self.file1: sublime.statusMessage("Merge File 1 chosen")
            else: self.notifySave()
    
    def notifySave(self):
        self.file1 = None
        sublime.messageBox('File must be saved to merge')
        
    def merge(self):
        cmd = '%s %s "%s" "%s"' % (WINMERGE, OPTIONS, self.file1, self.file2)
        Popen(cmd)
        self.file1 = None
            
    def onActivated(self, view):
        if not self.file1: return
        else:
            self.file2 = view.fileName()
            if self.file2: self.merge()
            else: self.notifySave()