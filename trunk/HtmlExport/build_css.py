from __future__ import with_statement

import plist, string

def camelizeString(toCamel):
    toCamel = [(l if l in string.ascii_letters else ' ') for l in toCamel]
    toCamel =  [w.capitalize() for w in "".join(toCamel).split(' ')]
    toCamel = "".join(toCamel)
    
    return toCamel[:1].lower() + toCamel[1:]    #sometimes toCamel will be ''
    
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
    return createRule(["pre.%s {" % camelizeString(themeName)], listing)

def createScopeRule(listing, themeName): 
    name = camelizeString(listing['name'])
    return createRule(["pre.%s .%s {" % (camelizeString(themeName), name)], 
                        listing)
    
def getCSSFromThemeDict(theme):
    name = theme['name']
    settings = theme['settings']
    mainSettings = settings[0]
    
    css = [createMainRule(mainSettings, name)]

    for scopeRule in settings[1:]:
        css.append(createScopeRule(scopeRule, name))
    
    css+=["pre.%s .lineNumber {\n    color: #7f909f;\n}" % camelizeString(name)]
    
    return "\n\n".join(css) + ln

def getScopes(theme):
    scopes = {}
    for scope in theme["settings"][1:]:
        if 'scope' in scope:
            scopes[camelizeString(scope['name'])] = scope['scope'].split(',')
    return scopes
    
if __name__ == "__main__":
    if 1:
        from blackboard_theme import blackBoard
        with open('Blackboard.css', 'w') as fh:
            fh.write(getCSSFromThemeDict(blackBoard))
            
        if 1:
            import pprint
            pprint.pprint( getScopes(blackBoard))