import sublime, sublimeplugin, re

def open_project_file(file_matcher, window, auto_set_view=-1):
    proj_files = window.project().mountPoints()[0]['files']
    for f in proj_files:
        if file_matcher.search(f):
            file_view = window.openFile(f)
            if auto_set_view >= 0: # don't set the view unless specified
                window.setViewPosition(file_view, auto_set_view, 0)
            print("Opened " + f)
            return

class OpenCeedlingFileCommand(sublimeplugin.TextCommand):

    def run(self, view, args):
        current_file_path = view.fileName()
        window = view.window()
        
        if args[0] == 'config':
            config_matcher = re.compile(r"(\\\\)?(project|test)\.yml$")
            open_project_file(config_matcher, window)
        
        elif re.search(r"\w+\.[ch]\w*$", current_file_path):
            
            current_file = re.search(r"([\w\.]+)$", current_file_path).group(1)
            base_name = re.search(r"(\w+)\.(\w+)$", current_file).group(1)
            base_name = re.sub('^test_', '', base_name)
            
            source_matcher = re.compile("\\\\" + base_name + "\.c$")
            header_matcher = re.compile("\\\\" + base_name + "\.h$")
            test_matcher   = re.compile("\\\\test_" + base_name + "\.c$")
            
            if args[0] == 'next':
                if re.match("test_", current_file):
                    open_project_file(source_matcher, window)
                elif re.search(r"\.c", current_file):
                    open_project_file(header_matcher, window)
                elif re.search(r"\.h", current_file):
                    open_project_file(test_matcher, window)
            elif args[0] == 'source':
                open_project_file(source_matcher, window)
            elif args[0] == 'test':
                open_project_file(test_matcher, window)
            elif args[0] == 'header':
                open_project_file(header_matcher, window)
            elif args[0] == 'test_and_source':
                window.runCommand('layoutDoubleVert')
                open_project_file(test_matcher, window, 0)
                open_project_file(source_matcher, window, 1)