# coding=windows-1250
from PyQt4 import QtCore, QtGui
import logging
import re

logging.basicConfig(level=logging.DEBUG, format='%(lineno)d: %(message)s')
logger = logging.getLogger()

class KlicoveSlovo(QtGui.QWidget):
    def __init__(self, parent=None):
        logger.debug('init>')
        super(KlicoveSlovo, self).__init__(parent)

        nameLabel = QtGui.QLabel("Fragment:")
        self.nameLine = QtGui.QLineEdit()
        addressLabel = QtGui.QLabel("Možnosti:".decode('windows-1250'))
        self.addressText = QtGui.QTextEdit()
        self.hledejUprostred = QtGui.QCheckBox('hledat i uprostřed slov'.decode('windows-1250'))
        self.ignorujDiakritiku = QtGui.QCheckBox('ignorovat diakritiku'.decode('windows-1250'))
        self.ignorujZnelost = QtGui.QCheckBox('zaměnovat znělé a neznělé souhlásky'.decode('windows-1250'))


        self.input = self.nameLine
        self.input.returnPressed.connect(self.setSelected)
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.hledejUprostred, 0, 0)
        mainLayout.addWidget(self.ignorujDiakritiku, 0, 1)
        mainLayout.addWidget(self.ignorujZnelost, 0, 2, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(nameLabel, 1, 0)
        mainLayout.addWidget(self.nameLine, 1, 1)
        mainLayout.addWidget(addressLabel, 2, 0, QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.addressText, 2, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Klíčové slovo".decode('windows-1250'))

        self.connect(self.nameLine, QtCore.SIGNAL("textChanged(QString)"),
                     self.text_changed)

    def setSelected(self):
        logger.debug('setSelected>')
        self.nameLine.selectAll()



    def text_changed(self):
        pattern = unicode(self.nameLine.text())
        logger.debug('pattern:%s' %pattern)
        # logger.debug(self.hledejUprostred.isChecked())
        if self.ignorujDiakritiku.isChecked():
            pattern = strip_accents(pattern)
            logger.debug('pattern:%s' %pattern)

        if self.ignorujZnelost.isChecked():
            regexpPattern = patternizuj_znelost(pattern)
            if self.hledejUprostred.isChecked():
                logger.debug('rozsirim o hledani odprostred - .*')
                regexpPattern = '.*' + regexpPattern
            else:
                logger.debug('rozsirim o znak ^ pro hledani od zacatku')
                regexpPattern = '^' + regexpPattern

            logger.debug('regexpPattern:' + regexpPattern)
            r = re.compile(regexpPattern)


        if len(pattern) >= 1:
            if self.hledejUprostred.isChecked():
                if self.ignorujDiakritiku.isChecked():
                    if self.ignorujZnelost.isChecked():
                        self.new_list = filter(r.match, vse_diafree)
                    else:
                        self.new_list = [item for item in vse_diafree if pattern in strip_accents(item)]
                else:
                    if self.ignorujZnelost.isChecked():
                        self.new_list = filter(r.match, vse)
                    else:
                        self.new_list = [item for item in vse if pattern in item]
            else:
                if self.ignorujDiakritiku.isChecked():
                    if self.ignorujZnelost.isChecked():
                        self.new_list = filter(r.match, vse_diafree)
                    else:
                        self.new_list = [item for item in vse_diafree if item.startswith(pattern)]
                else:
                    if self.ignorujZnelost.isChecked():
                        self.new_list = filter(r.match, vse)
                    else:
                        self.new_list = [item for item in vse if item.startswith(pattern)]
            self.addressText.setText('\n'.join(self.new_list))

def patternizuj_znelost(a_str):
    '''
    nahradi ve stringu vsechny parove znele ci neznele souhlasky jejich parem
    párové: znělé b v d ď z ž g h
          neznělé p f t ť s š k ch
    :param a_str:
    :return:
    '''
    global mapa
    global vsechny
    result = ''
    for index, c in enumerate(a_str):
        if c in vsechny:
            # pro "c", ktere je casti "ch" nedelej nic
            if c == 'c' and len(c) > index + 1 and c[index + 1] == 'h':
                logger.debug('c z ch')
            else:
                result += mapa[c]
        else:
            result += c

    return result


import unicodedata
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def je_podobny(a_pattern, a_item):
    '''
    Vrati true, pokud je pattern obsazeny v itemu bez ohledu na znelost souhlasek: obed, opet => true
    :param a_pattern:
    :param a_item:
    :return:
    '''


pary = ['bp', 'vf', 'dt', 'ďť'.decode('windows-1250'), 'zs', 'žš'.decode('windows-1250'), 'gk']
vsechny = "".join(pary) + 'hch'
mapa = {}
for par in pary:
    for c in par:
        mapa[c] = '['+ par + ']'
mapa ['h'] = '(h|ch)'
mapa ['ch'] = '(h|ch)'


with open('syn2010_lemma_abc.txt', 'r') as in_file:
    vse = in_file.readlines()
    vse = [slovo.split('\t')[1].decode('windows-1250') for slovo in vse]
    vse_diafree = [strip_accents(item) for item in vse]
in_file.close()

if __name__ == '__main__':
    import sys


    app = QtGui.QApplication(sys.argv)

    KlicoveSlovo = KlicoveSlovo()
    KlicoveSlovo.show()

    sys.exit(app.exec_())
