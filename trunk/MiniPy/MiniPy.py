from math import *
from random import *
import re
import sublime, sublimeplugin

class MiniPyCommand(sublimeplugin.TextCommand):
   def run(self, view, args):
      x = 0
      # replace each special char $ with the next index from serial_number list
      # and eval the expression
      for region in view.sel():
         result = eval(view.substr(region))
         x = result
         view.replace(region, str(result))
      
   def isEnabled(self, view, args):
      return True
