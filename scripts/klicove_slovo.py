# coding=windows-1250
from PyQt4 import QtCore, QtGui
import logging

class KlicoveSlovo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(KlicoveSlovo, self).__init__(parent)

        nameLabel = QtGui.QLabel("Fragment:")
        self.nameLine = QtGui.QLineEdit()
        addressLabel = QtGui.QLabel("Možnosti:".decode('windows-1250'))
        self.addressText = QtGui.QTextEdit()



        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addWidget(self.nameLine, 0, 1)
        mainLayout.addWidget(addressLabel, 1, 0, QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.addressText, 1, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Klíčové slovo".decode('windows-1250'))

        self.connect(self.nameLine, QtCore.SIGNAL("textChanged(QString)"),
                     self.text_changed)
    def text_changed(self):
        pattern = unicode(self.nameLine.text())
        if len(pattern) >= 1:
            self.new_list = [item for item in vse if item.find(pattern) == 0]
            self.addressText.setText('\n'.join(self.new_list))


with open('syn2010_lemma_abc.txt', 'r') as in_file:
    vse = in_file.readlines()
    vse = [slovo.split('\t')[1].decode('windows-1250') for slovo in vse]
in_file.close()

if __name__ == '__main__':
    import sys


    app = QtGui.QApplication(sys.argv)

    KlicoveSlovo = KlicoveSlovo()
    KlicoveSlovo.show()

    sys.exit(app.exec_())
