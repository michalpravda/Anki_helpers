# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *

import re

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def testFunction():
  ids = mw.col.findCards("deck:'slovicka nemecky'")
  with open('d:\\exp.txt', 'w') as f:
      output = set()
      for id in ids:
          card = mw.col.getCard(id)
          note = card.note()
          for (name, value) in note.items():
              if (name == 'Word') or name == 'Text':
                  value = re.sub('{{c.::(.*?)}}', '\\1', value)
                  value = value.replace('&nbsp;', '').replace('<div>', '').replace('</div>', '')
                  output.add(value.encode('utf-8'))
      lis = sorted(list(output))
      for val in lis:
          f.write(val + '\n')
  f.close
# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
mw.connect(action, SIGNAL("triggered()"), testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

