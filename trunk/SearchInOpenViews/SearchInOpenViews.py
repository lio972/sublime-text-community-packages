import sublime, sublimeplugin
import functools

#------------------------------------------------------------------
#------------------------------------------------------------------
class SearchInOpenViewsCommand(sublimeplugin.TextCommand):
   def run(self, view, args):
      view_list = self.get_view_list(view)
           
      first_selection = view.sel()[0]
      if first_selection.begin() - first_selection.end() != 0:
         init_pattern = view.substr(first_selection)
      else:
         init_pattern = ""
         
      view.window().showInputPanel("Search in open files:", init_pattern,
         functools.partial(self.on_start_searching, view, view_list),
         self.on_change, self.on_cancel)

   #------------------------------------------------------------------
   def on_start_searching(self, view, view_list, pattern):
      result = []
      for v in view_list:
         result += self.search_term(v, pattern)
           
      display = []
      for (file, line, txt, region) in result:
         display.append(file + ":" + str(line) + ": " + txt)
                                     
      flags = 0
      view.window().showSelectPanel(display,
         functools.partial(self.open_selection, view, view_list, result), None,
         flags)
      
   def on_change(self, input):
      pass
   
   def on_cancel(self):
      pass   
      
   #------------------------------------------------------------------
   def search_term(self, view, pattern):
      result = []
      for region in view.findAll(pattern):
         (row, col) = view.rowcol(region.begin())
         # collect all the information
         file_name = view.fileName()
         line_number = row+1
         line_text = view.substr(view.line(region))
         res_tuple = (file_name, line_number, line_text, region)
         # add the information tuple to result list
         result.append(res_tuple)
      
      return result
   
   #------------------------------------------------------------------
   def get_view_list(self, view):
      unique_views = []
      file_names = []
      for v in view.window().views():
         # avoid re-searching same view (if opened twice)
         if not v.fileName() in unique_views:
            unique_views.append(v)
            file_names.append(v.fileName())
      return unique_views
   
   #------------------------------------------------------------------
   def isEnabled(self, view, args):
      if view.fileName() is not None:
         return True
      else:
         return False
   
   #------------------------------------------------------------------
   def advance_line(self, view, last_region):
      (row, col) = view.rowcol(last_region.begin())
      next_point = view.textPoint(row+1, 0)
      next_region = view.line(next_point)
      
      if next_region.begin() > last_region.end():
         return next_region
      else:
         return False

#------------------------------------------------------------------
   def open_selection(self, view, view_list, results_list, index):
      (file, row, text, region) = results_list[index]
      
      for v in view_list:
         if file == v.fileName():
            view.window().focusView(v)
            # reset selection
            view_selection = v.sel()
            view_selection.clear()
            # add new selection
            view_selection.add(region)
            v.show(region)