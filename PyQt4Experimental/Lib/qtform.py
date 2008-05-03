#################################### IMPORTS ###################################

import sublime

from functools import partial

from PyQt4.QtCore import *
from PyQt4.QtGui import *

################################## PYQT4 FORM ##################################

class Ruler(QDialog):
  def __init__(self, plugin, parent=None):
    super(Ruler, self).__init__(parent)
    self.plugin = plugin
    
    self.rulers = QSpinBox()
    self.rulers.setRange(-1, 80)
    self.rulers.setValue(80)
    self.rulers.setAccelerated(True)
    self.rulers.setWrapping(True)

    layout = QGridLayout()
    layout.addWidget(self.rulers, 0,0)
        
    self.setLayout(layout)

    self.connect(self.rulers, SIGNAL("valueChanged(int)"), self.updateRuler)
    
  def updateRuler(self):
    " timeOut's are run in blocking call in main thread and are safe to use"

    sublime.setTimeout(
       partial(self.plugin.setRuler, self.rulers.value()), 20
    )
    
################################################################################