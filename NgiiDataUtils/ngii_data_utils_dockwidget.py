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

# from ngii_data_utils_dockwidget_base import Ui_NgiiDataUtilsDockWidgetBase
from OnMap import OnMapLoader
from Dxf import DxfLoader

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ngii_data_utils_dockwidget_base.ui'))


class NgiiDataUtilsDockWidget(QtGui.QDockWidget, FORM_CLASS):
# class NgiiDataUtilsDockWidget(QtGui.QDockWidget, Ui_NgiiDataUtilsDockWidgetBase):
    closingPlugin = pyqtSignal()
    _onMapLoader = None

    displayDebug = False
    displayInfo = True
    displayComment = True
    displayError = True

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(NgiiDataUtilsDockWidget, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self._connect_action()
        self._createLoader()

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

    def _createLoader(self):
        self._onMapLoader = OnMapLoader(self.iface, self)

    def _on_click_btnAutoDetect(self):
        pass

    def _on_click_btnLoadVector(self):
        # 기존 폴더 유지하게 옵션 추가: https://stackoverflow.com/questions/23002801/pyqt-how-to-make-getopenfilename-remember-last-opening-path
        vectorPath = QFileDialog.getOpenFileName(caption=u"국토지리정보 벡터파일 선택", filter=u"국토지리정보 벡터파일(*.gpkg *.shp *.pdf *.dxf)", options=QFileDialog.DontUseNativeDialog)
        if vectorPath is None:
            return

        filename, extension = os.path.splitext(vectorPath)

        if extension.lower() == ".pdf":
            if self._onMapLoader:
                self._onMapLoader.runImport(vectorPath)
        elif extension.lower() == ".shp":
            DxfLoader.load(vectorPath)
        elif extension.lower() == ".pdf":
            DxfLoader.load(vectorPath)
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

    #############################
    # 로그 표시
    def error(self, msg):
        if not self.displayError:
            return
        self.editLog.appendHtml(u'<font color="red"><b>{}</b></font>'.format(msg))
        self.editLog.moveCursor(QTextCursor.End)

    def info(self, msg):
        if not self.displayInfo:
            return
        self.editLog.appendHtml(u'<font color="black">{}</font>'.format(msg))
        self.editLog.moveCursor(QTextCursor.End)

    def debug(self, msg):
        if not self.displayDebug:
            return
        self.editLog.appendHtml(u'<font color="green">{}</font>'.format(msg))
        self.editLog.moveCursor(QTextCursor.End)

    def comment(self, msg):
        if not self.displayComment:
            return
        self.editLog.appendHtml(u'<font color="blue"><b>{}</b></font>'.format(msg))
        self.editLog.moveCursor(QTextCursor.End)
    #############################

    def _on_click_btnReportError(self):
        pass

    def onButton(self, buttonObj):
        id = buttonObj.parent().id
        myTitle = buttonObj.text()
        groupTitle = buttonObj.parent().title()
        self.info(u"[{}] {} : {}".format(id, groupTitle, myTitle))

    def onSlider(self, sliderObj):
        value = sliderObj.value()
        id = sliderObj.parent().id
        myTitle = "slider"
        groupTitle = sliderObj.parent().title()
        self.info(u"[{}] {} : {}".format(id, groupTitle, value))

    def onColor(self, buttonObj):
        id = buttonObj.parent().id
        myTitle = buttonObj.text()
        groupTitle = buttonObj.parent().title()
        self.info(u"[{}] {} : {}".format(id, groupTitle, myTitle))
        rc = buttonObj.show()

    def onColorChanged(self, buttonObj):
        color = buttonObj.color()
        self.info("COLOR: ")
        self.info(str(buttonObj.color()))

    def makeMirrorWindow(self):
        from qgis import utils

        try:
            mirrorMapPlugin = utils.plugins['DockableMirrorMap']
        except:
            self.alert(u"Dockable MirrorMap을 설치 하셔야 동작 가능합니다.\n\n"
                       u"QGIS의 [플러그인 - 플러그인 관리 및 설치] 메뉴로 플러그인 관리자를 실행해\n"
                       u"Dockable MirrorMap 플러그인을 검색하시면 쉽게 설치하실 수 있습니다.")
            return

        mirrorMapPlugin.runDockableMirror()

        pass