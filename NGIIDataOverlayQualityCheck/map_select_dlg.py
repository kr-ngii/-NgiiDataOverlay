# -*- coding: utf-8 -*-
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, uic

MapSelect_FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'map_select.ui'))


class DlgMapSelect(QDialog, MapSelect_FORM_CLASS):
    def __init__(self, parent=None):
        super(DlgMapSelect, self).__init__(parent)
        self.setupUi(self)

