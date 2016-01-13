#Just a fix to an Anki add-on by unknown autor  -1125592690
#Usage:
#download the original (contains pictures) add-on and then replace file c:\Users\<your win login>\Documents\Anki\addons\showdogs.py with this one

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
from anki.hooks import wrap

import os
import random
import logging
from anki.utils import  namedtmp

LOGFILE = namedtmp('showdogs.log')

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', filename=LOGFILE, datefmt='%d.%m.%Y %H:%M:%S%p)')
logger = logging.getLogger()

mw.showdogs = {}
mw.showdogs['card_count'] = 0
mw.showdogs['interval'] = 9

def showDog():
    mw.showdogs['card_count'] = mw.showdogs['card_count'] + 1
    if mw.showdogs['card_count'] % mw.showdogs['interval'] != 0:
        return

    dialog = QDialog(mw)
    layout = QVBoxLayout(dialog)
    dialog.setLayout(layout)

    dogs_dir = os.path.join(mw.pm.addonFolder(), 'showdogs')
    logger.debug(dogs_dir)
    image_path = random.choice(os.listdir(dogs_dir))
    logger.debug(image_path)
    label = QLabel()
    myPixmap = QPixmap(os.path.join(dogs_dir, image_path))
    myScaledPixmap = myPixmap.scaled(label.size(), Qt.KeepAspectRatio)
    label.setPixmap(myScaledPixmap)

    label.show()
    layout.addWidget(label)

    dialog.exec_()

mw.reviewer.nextCard = wrap(mw.reviewer.nextCard, showDog)