from __future__ import with_statement

import plist

CSSMAP = {
    
    'background':     'background-color',
    'caret':          None,
    'fontStyle':      None,
    'foreground':     'color',
    'invisibles':     None,
    'lineHighlight':  None,
    'selection':      None,
}

def createTitle(input_dict):    
    name, author = input_dict['name'], input_dict['author']
    return "Theme: %s\nAuthor: %s" % (name, author)

def getCSSFromTMSettings(settings):
    css = {}
    for rule in settings:
        if rule in CSSMAP and CSSMAP[rule]:
            css[CSSMAP[rule]] = settings[rule]
    
    return sorted(css.items())

def createRule(rule_starter, listing):
    rule = rule_starter
    css = getCSSFromTMSettings(listing['settings'])
    for property_, value in css:
        rule.append("    %s: %s;" % (property_, value))
    rule.append("}")
    return "\n".join(rule)

def createMainRule(listing, themeName):
    selector = "pre.sublime.%s, pre.sublime.%s #line-number {"
    return createRule([selector % tuple([themeName]*2)], listing)

def createScopeRule(listing, themeName):
    scope = ['.' + c for c in listing['scope'].split(" ")]
    scope = " ".join(scope).split(",")
    
    selectors = [("pre.sublime.%s " % themeName) + sel for sel in scope]
    
    return createRule([", ".join(selectors) + " {"], listing)
    
def getCSSFromThemeDict(theme):
    name = theme['name']
    settings = theme['settings']
    mainSettings = settings[0]
    
    css = [createMainRule(mainSettings, name)]
    
    for scopeRule in settings[1:]:
        css.append(createScopeRule(scopeRule, name))
    
    return "\n\n".join(css)
    
if __name__ == "__main__":
    if 1:
        from blackboard_theme import blackBoard
        with open('Blackboard.css', 'w') as fh:
            fh.write(getCSSFromThemeDict(blackBoard))