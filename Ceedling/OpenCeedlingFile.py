import sublime
import sublimeplugin
import re

class OpenCeedlingFileCommand(sublimeplugin.TextCommand):

    def run(self, view, args):
        self.views = []
        current_file_path = view.fileName()
        window = view.window()
        option = args[0]
        
        if option == 'config':
            config_matcher = re.compile(r"(\\\\)?(project|test)\.yml$")
            self.open_project_file(config_matcher, window)
        
        elif re.search(r"\w+\.[ch]\w*$", current_file_path):
            
            current_file = re.search(r"([\w\.]+)$", current_file_path).group(1)
            base_name = re.search(r"(\w+)\.(\w+)$", current_file).group(1)
            base_name = re.sub('^test_', '', base_name)
            
            source_matcher = re.compile("\\\\" + base_name + "\.c$")
            header_matcher = re.compile("\\\\" + base_name + "\.h$")
            test_matcher   = re.compile("\\\\test_" + base_name + "\.c$")
            
            if option == 'next':
                if re.match("test_", current_file):
                    self.open_project_file(source_matcher, window)
                elif re.search(r"\.c", current_file):
                    self.open_project_file(header_matcher, window)
                elif re.search(r"\.h", current_file):
                    self.open_project_file(test_matcher, window)
            elif option == 'source':
                self.open_project_file(source_matcher, window)
            elif option == 'test':
                self.open_project_file(test_matcher, window)
            elif option == 'header':
                self.open_project_file(header_matcher, window)
            elif option == 'test_and_source':
                window.runCommand('layoutDoubleVert')
                self.open_project_file(test_matcher, window, 0)
                self.open_project_file(source_matcher, window, 1)
            
        for v in self.views:
            window.focusView(v)
                
    def open_project_file(self, file_matcher, window, auto_set_view=-1):
        proj_files = window.project().mountPoints()[0]['files']
        for f in proj_files:
            if file_matcher.search(f):
                file_view = window.openFile(f)
                if auto_set_view >= 0: # don't set the view unless specified
                    window.setViewPosition(file_view, auto_set_view, 0)
                self.views.append(file_view)
                print("Opened " + f)
