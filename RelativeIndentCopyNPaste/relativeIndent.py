import sublime, sublimeplugin, re

class RelativeIndentPasteCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        selection = sublime.getClipboard()
        spacesList = []
        spaces = 0
        
        split = selection.split("\n")
        for l in split:
            for ch in l:
                if ch.isspace(): spaces += 1
                else:
                    spacesList.append(spaces)
                    spaces = 0
                    break
                                           
        anchorPoint = min(spacesList)
        selection = "\n".join([l[anchorPoint:] for l in split])
                
        view.runCommand('insertInlineSnippet', ['$PARAM1', selection])
        
class RelativeIndentCopyCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        view.runCommand('expandSelectionTo line')
        view.runCommand('copy')