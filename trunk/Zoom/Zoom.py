import sublime, sublimeplugin

class ZoomInCommand(sublimeplugin.TextCommand):
   def run(self, view, args):
      current_font = view.options().get('font')
      (font, sep, size) = current_font.rpartition(" ")
      new_size = int(size) + 1
      new_font = font + " " + str(new_size)
      view.options().set('font', new_font)
      print "set new font to: " + new_font
      
   def isEnabled(self, view, args):
      return True


class ZoomOutCommand(sublimeplugin.TextCommand):
   def run(self, view, args):
      current_font = view.options().get('font')
      (font, sep, size) = current_font.rpartition(" ")
      new_size = int(size) - 1
      new_font = font + " " + str(new_size)
      view.options().set('font', new_font)
      print "set new font to: " + new_font
		
   def isEnabled(self, view, args):
      return True
