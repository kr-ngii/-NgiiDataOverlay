# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NgiiDataUtilsDockWidget
                                 A QGIS plugin
 국토지리정보원 데이터 사용지원 툴
                             -------------------
        begin                : 2018-04-03
        git sha              : $Format:%H$
        copyright            : (C) 2018 by NGII
        email                : jangbi882@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, uic
from ngii_data_utils_dockwidget_base import Ui_NgiiDataUtilsDockWidgetBase
from OnMap import OnMapLoader
from Dxf import DxfLoader

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ngii_data_utils_dockwidget_base.ui'))


# class NgiiDataUtilsDockWidget(QtGui.QDockWidget, FORM_CLASS):
class NgiiDataUtilsDockWidget(QtGui.QDockWidget, Ui_NgiiDataUtilsDockWidgetBase):
    closingPlugin = pyqtSignal()
    OnMapLoader = None

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(NgiiDataUtilsDockWidget, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self._connect_action()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def _connect_action(self):
        self.connect(self.btnAutoDetect, SIGNAL("clicked()"), self._on_click_btnAutoDetect)
        self.connect(self.btnLoadVector, SIGNAL("clicked()"), self._on_click_btnLoadVector)
        self.connect(self.btnLoadImage, SIGNAL("clicked()"), self._on_click_btnLoadImage)
        self.connect(self.btnLoadTms, SIGNAL("clicked()"), self._on_click_btnLoadTms)
        self.connect(self.btnLoadBaseMap, SIGNAL("clicked()"), self._on_click_btnLoadBaseMap)
        self.connect(self.btnLoadOnmapBaseMap, SIGNAL("clicked()"), self._on_click_btnLoadOnmapBaseMap)
        self.connect(self.btnLoadInternetBaseMap, SIGNAL("clicked()"), self._on_click_btnLoadInternetBaseMap)
        self.connect(self.btnReportError, SIGNAL("clicked()"), self._on_click_btnReportError)

    def _on_click_btnAutoDetect(self):
        pass

    def _on_click_btnLoadVector(self):
        # 기존 폴더 유지하게 옵션 추가: https://stackoverflow.com/questions/23002801/pyqt-how-to-make-getopenfilename-remember-last-opening-path
        vectorPath = QFileDialog.getOpenFileName(caption=u"국토지리정보 벡터파일 선택", filter=u"온맵(*.pdf);;지형도(*.dxf);;공공측량성과(*.dxf)", options=QFileDialog.DontUseNativeDialog)
        if vectorPath is None:
            return

        filename, extension = os.path.splitext(vectorPath)

        if extension.lower() == ".pdf":
            OnMapLoader.load(vectorPath, self.iface)
        elif extension.lower() == ".dxf":
            DxfLoader.load(vectorPath)


    def _on_click_btnLoadImage(self):
        pass

    def _on_click_btnLoadTms(self):
        pass

    def _on_click_btnLoadBaseMap(self):
        pass

    def _on_click_btnLoadOnmapBaseMap(self):
        pass

    def _on_click_btnLoadInternetBaseMap(self):
        pass

    def _on_click_btnReportError(self):
        pass
