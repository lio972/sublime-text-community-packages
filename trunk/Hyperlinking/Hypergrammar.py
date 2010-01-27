import os

class GrammarGenerator:
  """generates a grammar for a view"""
  
  
  def __init__(self, folderPath):
    self.folderPath = os.path.abspath(folderPath)
    self.head = """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>uuid</key>
        <string>F15EC19A-970E-4a82-B3AD-C6F8B6DF9F09</string>
        <key>patterns</key>
        <array>
"""

    self.foot = """
        </array>
        <key>name</key>
        <string>Custom grammar for ${wikiname}</string>
        <key>scopeName</key>
        <string>string</string>
        <key>fileTypes</key>
        <array>
            <string>.wiki</string>
        </array>
    </dict>
</plist>"""

    self.template = """
        <dict>
          <key>match</key><string>\\b${name}\\b</string>
          <key>name</key><string>markup.italic</string>
        </dict>"""
    
  def syntaxFile(self):
    return os.path.join(self.folderPath, "syntax-highlighting.tmLanguage")
    
    
  def run(self):
    if os.path.exists(self.folderPath) == False:
      print "Folder '%s' does not exist" % self.folderPath
      return None
    
   
    wikiName = os.path.split(self.folderPath)[1]
    
    content = self.head
    files = [f for f in os.listdir(self.folderPath) if f.endswith(".wiki")]
    names  = [os.path.splitext(n)[0] for n in files]
    
    for name in names:
      content = content + self.template.replace("${name}", name)
    content = content + self.foot.replace("${wikiname}", wikiName)
    
    syntaxFile = self.syntaxFile()
  
    f = open(syntaxFile, 'w')
    f.write(content)
    f.close()  
    
    return syntaxFile
   
    
if __name__ == "__main__":
  gen = GrammarGenerator("C:\\usr\\projects\\fiction-modus-operandi")
  syntaxFile = gen.run()
  print syntaxFile