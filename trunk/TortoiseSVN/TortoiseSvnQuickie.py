import sublime, sublimeplugin

# This simple plugin will add 'Hello, World!' to the end of the buffer when run.
# To run it, save it within the User/ directory, then open the console (Ctrl+~),
# and type: view.runCommand('sample')
#
# See http://www.sublimetext.com/docs/plugin-basics for more information
class TortoiseSvnQuickieCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        
        desc = [
            "File    Update",
            "File    Commit",
            "File    Diff",
            "File    Revert",
            "File    Log",
            "File    Add",
            "File    Ignore"
            "Project Update",
            "Project Commit",
            "Project Diff",
            "Project Revert",
            "Project Log",
            ]

        print desc.len
        
        args = [
            "'' 'tortoiseproc /command:update      /path:$ProjectDir /closeonend:4'",
            "'' 'tortoiseproc /command:commit      /path:$File /closeonend:4'",
            "'' 'tortoiseproc /command:diff        /path:$File /closeonend:4'",
            "'' 'tortoiseproc /command:revert      /path:$File /closeonend:4'",
            "'' 'tortoiseproc /command:log         /path:$File /closeonend:4'",
            "'' 'tortoiseproc /command:add         /path:$File /closeonend:4'",
            "'' 'tortoiseproc /command:ignore      /path:$File /closeonend:4'",
            "'' 'tortoiseproc /command:update      /path:$ProjectDir /closeonend:4'",
            "'' 'tortoiseproc /command:commit      /path:$ProjectDir /closeonend:4'",
            "'' 'tortoiseproc /command:showcompare /path:$ProjectDir /closeonend:0'",
            "'' 'tortoiseproc /command:revert      /path:$ProjectDir /closeonend:4'",
            "'' 'tortoiseproc /command:log         /path:$ProjectDir /closeonend:4'",
            ]

        print args.length
    
        # showQuickPanel(key, command, args, <displayArgs>, <flags>)
        view.window().showQuickPanel("", "exec", args, desc)