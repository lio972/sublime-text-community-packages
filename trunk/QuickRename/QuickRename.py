import os
import shutil
import sublime
import sublimeplugin

class QuickRename(sublimeplugin.TextCommand):

    def run(self, view, args):
        view.window().showInputPanel("New filename", "", lambda s: self.rename(view, s), None, None)

    def rename(self, view, new_file):
        old_file = view.fileName()
        if old_file is None:
            print("ABORT: The file hasn't been saved to disk yet. Performing regular save instead of rename.")
            view.window().runCommand("save")
            return
        old_file = old_file.rsplit(os.sep, 1)[1]
        if not self.validateFileName(view, old_file, new_file):
            return
        if view.isDirty():
            view.window().runCommand("save")
        window = view.window()
        self.fileOperations(window, old_file, new_file)
        self.setSelection(view, window.activeView())

    def validateFileName(self, view, old_file, new_file):
        if len(new_file) is 0:
            print("ABORT: No new filename given.")
            return False
        if view.isLoading():
            print("ABORT: The file is still loading.")
            return False
        if view.isReadOnly():
            print("ABORT: The file is read-only.")
            return False
        if(new_file == old_file):
            print("ABORT: The new file name was the same as the old one.")
            return False
        return True

    def fileOperations(self, window, old_file, new_file):
        window.runCommand("close")
        shutil.move(old_file, new_file)
        window.openFile(new_file)
        if old_file.endswith(".py"):
            os.remove(old_file + "c")

    def setSelection(self, old_view, new_view):
        new_view.sel().clear()
        new_view.sel().addAll(old_view.sel())
