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
from qgis.gui import QgsColorButton
from qgis.core import *

# from ngii_data_utils_dockwidget_base import Ui_NgiiDataUtilsDockWidgetBase
from OnMap import OnMapLoader
from Shp import ShpLoader
from Gpkg import GpkgLoader
from Dxf import DxfLoader


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ngii_data_utils_dockwidget_base.ui'))


# class NgiiDataUtilsDockWidget(QtGui.QDockWidget, Ui_NgiiDataUtilsDockWidgetBase):
class NgiiDataUtilsDockWidget(QtGui.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    _onMapLoader = None
    _shpLoader = None
    _gpkgLoader = None
    _dxfLoader = None

    _orgColor = None
    _last_opened_folder = None

    iGroupBox = 0
    groupBoxList = None
    mainGroup = None

    displayDebug = True
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

        self.groupBoxList = dict()

    def connectRemoteDebugger(self):
        try:
            import pydevd

            self.alert(u"곧 Debugger 가 연결됩니다. \nPyCharm의 Debug 탭에서 [플래이] 버튼을 누르세요.")

            pydevd.settrace('localhost',
                            port=9999,
                            stdoutToServer=True,
                            stderrToServer=True)
        except Exception as e:
            print e

    # 독 윈도우 토글 처리
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

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

    # 상태정보 표시
    def progText(self, text):
        self.lblStatus.setText(text)

    @staticmethod
    def alert(text, icon=QMessageBox.Information):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle(u"국토기본정보 데이터 중첩검사 유틸")
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()

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
        self._shpLoader = ShpLoader(self.iface, self)
        self._gpkgLoader = GpkgLoader(self.iface, self)
        self._dxfLoader = DxfLoader(self.iface, self)

    def _on_click_btnAutoDetect(self):
        res = self._autoDetecter.checkEnv()
        if not res:
            return

        self._autoDetecter.connectPg()
        self._autoDetecter.show()

    def _on_click_btnLoadVector(self):
        # 기존 폴더 유지하게 옵션 추가: https://stackoverflow.com/questions/23002801/pyqt-how-to-make-getopenfilename-remember-last-opening-path
        # vectorPath = QFileDialog.getOpenFileName(caption=u"국토지리정보 벡터파일 선택",
        #                                          filter=u"국토지리정보 벡터파일(*.gpkg *.shp *.pdf *.dxf)",
        #                                          options=QFileDialog.DontUseNativeDialog,
        #                                          fileMode=QFileDialog.ExistingFiles)
        # if vectorPath is None:
        #     return
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        if self._last_opened_folder is not None:
            dialog.setDirectory(self._last_opened_folder)
        # dialog.setFileMode(QtGui.QFileDialog.Directory )

        filters = [u"국토지리정보 벡터파일(*.gpkg *.shp *.pdf *.dxf)"]
        dialog.setNameFilters(filters)

        if (dialog.exec_()):
            fileList = dialog.selectedFiles()
        else:
            return

        pdfList = list()
        shpList = list()
        gpkgList = list()
        dxfList = list()

        for vectorPath in fileList:
            filename, extension = os.path.splitext(vectorPath)

            if extension.lower() == ".pdf":
                pdfList.append(vectorPath)
            elif extension.lower() == ".shp":
                shpList.append(vectorPath)
            elif extension.lower() == ".gpkg":
                gpkgList.append(vectorPath)
            elif extension.lower() == ".dxf":
                dxfList.append(vectorPath)

        # 온맵은 한 파일씩 그룹으로 임포트
        if self._onMapLoader:
            for vectorPath in pdfList:
                self._onMapLoader.runImport(vectorPath)

        # Shp의 경우 여러 파일을 하나의 그룹으로 묵어 임포트
        if self._shpLoader:
            self._shpLoader.runImport(shpList)

        # Gpkg 한 파일씩 그룹으로 임포트
        if self._gpkgLoader:
            for vectorPath in gpkgList:
                self._gpkgLoader.runImport(vectorPath)

        # DXF 한 파일씩 그룹으로 임포트
        if self._dxfLoader:
            for vectorPath in dxfList:
                self._dxfLoader.runImport(vectorPath)

    def _on_click_btnLoadImage(self):
        rasterPath = QFileDialog.getOpenFileName(caption=u"국토지리정보 영상 파일 선택", filter=u"국토지리정보 영상 파일(*.img *.tif)", options=QFileDialog.DontUseNativeDialog)
        if rasterPath is None:
            return

        filename, extension = os.path.splitext(rasterPath)

        if extension.lower() == ".pdf":
            if self._onMapLoader:
                self._onMapLoader.runImport(rasterPath)
        elif extension.lower() == ".shp":
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
        self.connectRemoteDebugger()
        pass

    def appendGroupBox(self):
        if self.mainGroup is not None:
            title = self.mainGroup.name()
        else:
            raise Exception("manGroup not defined")

        spacerItem = self.gridLayout_2.itemAtPosition(self.iGroupBox, 0)
        if spacerItem is not None:
            self.gridLayout_2.removeItem(spacerItem)

        self.iGroupBox += 1

        groupBox_1 = QGroupBox(self.scrollAreaWidgetContents)
        groupBox_1.id = self.iGroupBox
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(groupBox_1.sizePolicy().hasHeightForWidth())
        groupBox_1.setSizePolicy(sizePolicy)
        groupBox_1.setMaximumSize(QSize(16777215, 130))
        groupBox_1.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        groupBox_1.setObjectName("groupBox_{}".format(self.iGroupBox))
        gridLayout = QGridLayout(groupBox_1)
        gridLayout.setObjectName("gridLayout")
        horLayout1_1 = QHBoxLayout()
        horLayout1_1.setObjectName("horLayout1_{}".format(self.iGroupBox))
        btnToSpWin_1 = QPushButton(groupBox_1)
        btnToSpWin_1.setObjectName("btnToSpWin_{}".format(self.iGroupBox))
        horLayout1_1.addWidget(btnToSpWin_1)
        btnRemove_1 = QPushButton(groupBox_1)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(btnRemove_1.sizePolicy().hasHeightForWidth())
        btnRemove_1.setSizePolicy(sizePolicy)
        btnRemove_1.setMinimumSize(QSize(30, 0))
        btnRemove_1.setMaximumSize(QSize(30, 16777215))
        btnRemove_1.setObjectName("btnRemove_{}".format(self.iGroupBox))
        horLayout1_1.addWidget(btnRemove_1)
        gridLayout.addLayout(horLayout1_1, 0, 0, 1, 1)
        horLayout3_1 = QHBoxLayout()
        horLayout3_1.setObjectName("horLayout3_{}".format(self.iGroupBox))
        lblColor_1 = QLabel(groupBox_1)
        lblColor_1.setObjectName("lblColor_{}".format(self.iGroupBox))
        horLayout3_1.addWidget(lblColor_1)
        # btnSelColor_1 = QPushButton(groupBox_1)
        btnSelColor_1 = QgsColorButton(groupBox_1)
        btnSelColor_1.setObjectName("btnSelColor_{}".format(self.iGroupBox))
        horLayout3_1.addWidget(btnSelColor_1)
        # btnResetColor_1 = QPushButton(groupBox_1)
        # sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(btnResetColor_1.sizePolicy().hasHeightForWidth())
        # btnResetColor_1.setSizePolicy(sizePolicy)
        # btnResetColor_1.setMinimumSize(QSize(50, 0))
        # btnResetColor_1.setMaximumSize(QSize(50, 16777215))
        # btnResetColor_1.setObjectName("btnResetColor_{}".format(self.iGroupBox))
        # horLayout3_1.addWidget(btnResetColor_1)
        gridLayout.addLayout(horLayout3_1, 2, 0, 1, 1)
        horLayout2_1 = QHBoxLayout()
        horLayout2_1.setObjectName("horLayout2_{}".format(self.iGroupBox))
        lblTrans_1 = QLabel(groupBox_1)
        lblTrans_1.setObjectName("lblTrans_{}".format(self.iGroupBox))
        horLayout2_1.addWidget(lblTrans_1)

        sldTrans_1 = QSlider(groupBox_1)
        sldTrans_1.setOrientation(Qt.Horizontal)
        sldTrans_1.setObjectName("sldTrans_{}".format(self.iGroupBox))
        # 값의 범위를 0 ~ 90 으로 한정
        sldTrans_1.setRange(0, 90)
        horLayout2_1.addWidget(sldTrans_1)
        gridLayout.addLayout(horLayout2_1, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(groupBox_1, self.iGroupBox - 1, 0, 1, 1)

        groupBox_1.setTitle(title)
        btnToSpWin_1.setText(u"분할창으로 띄우기")
        btnRemove_1.setText(u"제거")
        lblColor_1.setText(u"색  상:")
        # btnResetColor_1.setText(u"초기화")
        lblTrans_1.setText(u"투명도:")

        groupBox = {
            "id": self.iGroupBox,
            "type": "onmap",
            "title": title,
            "treeItem": self.mainGroup,
            "groupBox": groupBox_1,
            "btnToSpWin": btnToSpWin_1,
            "btnRemove": btnRemove_1,
            "btnSelColor": btnSelColor_1,
            # "btnResetColor": btnResetColor_1,
            "sldTrans": sldTrans_1
        }

        self.groupBoxList[self.iGroupBox] = groupBox

        btnToSpWin_1.clicked.connect(lambda: self._onButtonClickHandler(btnToSpWin_1))
        btnRemove_1.clicked.connect(lambda: self._onButtonClickHandler(btnRemove_1))
        btnSelColor_1.clicked.connect(lambda: self._onClickColorButton(btnSelColor_1))
        btnSelColor_1.colorChanged.connect(lambda: self._onColorChanged(btnSelColor_1))
        sldTrans_1.sliderReleased.connect(lambda: self._onSliderReleased(sldTrans_1))

        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, self.iGroupBox, 0, 1, 1)

    @staticmethod
    def removeGroupBox(groupObj):
        treeNode = groupObj["treeItem"]
        parentNode = treeNode.parent()
        parentNode.removeChildNode(treeNode)

        groupBox = groupObj["groupBox"]
        groupBox.deleteLater()

    def _onButtonClickHandler(self, buttonObj):
        try:
            groupId = buttonObj.parent().id
            buttonTitle = buttonObj.text()
            groupTitle = buttonObj.parent().title()

            try:
                groupObj = self.groupBoxList[groupId]
            except Exception as e:
                raise e

        except Exception as e:
            raise e

        if buttonTitle == u"제거":
            self.removeGroupBox(groupObj)
        else:
            return

    def _onSliderReleased(self, sliderObj):
        value = sliderObj.value()
        self.debug(u"투명도: {}".format(value))
        groupId = sliderObj.parent().id
        groupObj = self.groupBoxList[groupId]

        treeNode = groupObj["treeItem"]
        self.setNodeTransparency(treeNode, value)

    def setNodeTransparency(self, treeNode, value):
        for node in treeNode.children():
            nodeType = node.nodeType()

            # 그룹인 경우 재귀호출
            if nodeType == QgsLayerTreeNode.NodeGroup:
                self.setNodeTransparency(node, value)
            elif nodeType == QgsLayerTreeNode.NodeLayer:
                layer = node.layer()
                if layer.type() == 0:  # QgsVectorLayer
                    layer.setLayerTransparency(value)
                else:  # QgsRasterLayer
                    layer.renderer().setOpacity(1.0 - (value * 0.01))

                layer.triggerRepaint()

    def _onClickColorButton(self, buttonObj):
        self._orgColor = buttonObj.color()
        buttonObj.show()

    def _onColorChanged(self, buttonObj):
        newColor = buttonObj.color()
        if self._orgColor == newColor:
            return

        groupId = buttonObj.parent().id
        groupObj = self.groupBoxList[groupId]

        treeNode = groupObj["treeItem"]
        self.setNodeColor(treeNode, newColor)

    def setNodeColor(self, treeNode, newColor):
        colorText = "{},{},{}".format(newColor.red(), newColor.green(), newColor.blue())

        for node in treeNode.children():
            nodeType = node.nodeType()

            # 그룹인 경우 재귀호출
            if nodeType == QgsLayerTreeNode.NodeGroup:
                self.setNodeColor(node, newColor)
            elif node.nodeType() == QgsLayerTreeNode.NodeLayer:
                layer = node.layer()
                self.debug(u"Layer: {}".format(layer.name()))
                if layer.type() == QgsMapLayer.VectorLayer:  # QgsVectorLayer
                    geomType = layer.geometryType()
                    # if geomType == QGis.Point:
                    if geomType == 0:
                        symbol = QgsMarkerSymbolV2().createSimple({'color': colorText, 'name': 'circle'})
                    # elif geomType == QGis.Line:
                    elif geomType == 1:
                        symbol = QgsLineSymbolV2().createSimple({'color': colorText})
                    # elif geomType == QGis.Polygon:
                    elif geomType == 2:
                        symbol = QgsFillSymbolV2().createSimple({'color': colorText, 'style_border':'no', 'style': 'solid'})
                    else:
                        continue

                    ddp = QgsDataDefined(True, True, "@symbol_color")
                    symbol.symbolLayer(0).setDataDefinedProperty("color_border", ddp)
                    renderer = QgsRuleBasedRendererV2(symbol)
                    root_rule = renderer.rootRule()

                    rule = root_rule.children()[0].clone()
                    rule.symbol().setColor(newColor)
                    root_rule.appendChild(rule)

                    root_rule.removeChildAt(0)
                    layer.setRendererV2(renderer)
                    layer.triggerRepaint()

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
