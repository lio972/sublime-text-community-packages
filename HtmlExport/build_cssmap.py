import os, re, plist, pprint

themesPath = r"C:\Users\Nick\AppData\Roaming\Sublime Text\Packages\Color Scheme - Default"

themes = [t for t in os.listdir(themesPath) if t.endswith('tmTheme')]

os.chdir(themesPath)
settings = set()

for theme in (plist.parse_plist(t) for t in themes):
    for ruleset in theme['settings']:
        for rule in ruleset['settings']:
            settings.add(rule)
            
pprint.pprint( dict(zip(settings, settings)) )