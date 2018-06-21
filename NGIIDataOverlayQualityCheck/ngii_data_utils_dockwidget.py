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
import re
import tempfile
import urllib2
from PIL import Image
import json
from subprocess import call

# from ngii_data_utils_dockwidget_base import Ui_NgiiDataUtilsDockWidgetBase
from AutoDetect import AutoDetect
from OnMap import OnMapLoader
from Shp import ShpLoader
from Gpkg import GpkgLoader
from Dxf import DxfLoader
from Image import ImageLoader
import socket

import TmsForKorea
from TmsForKorea import *
from TmsForKorea.weblayers.daum_maps import OlDaumStreetLayer, OlDaumHybridLayer
from TmsForKorea.weblayers.naver_maps import OlNaverStreetLayer, OlNaverHybridLayer
from TmsForKorea.weblayers.olleh_maps import OlOllehStreetLayer, OlOllehHybridLayer, OlOllehSimpleLayer
from TmsForKorea.weblayers.ngii_maps import OlNgiiStreetLayer, OlNgiiPhotoLayer, OlNgiiBlankLayer, OlNgiiHighDensityLayer, \
    OlNgiiColorBlindLayer, OlNgiiEnglishLayer, OlNgiiChineseLayer, OlNgiiJapaneseLayer

from dlg_report_error import DlgReportError
from map_select_dlg import DlgMapSelect
from DockableMirrorMap.dockableMirrorMap import DockableMirrorMap


class QMyGroupBox(QGroupBox):
    groupId = None

    def __init__(self, *__args):
        super(QMyGroupBox, self).__init__(*__args)


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ngii_data_utils_dockwidget_base.ui'))


# class NgiiDataUtilsDockWidget(QtGui.QDockWidget, Ui_NgiiDataUtilsDockWidgetBase):
class NgiiDataUtilsDockWidget(QtGui.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    _autoDetecter = None
    _onMapLoader = None
    _shpLoader = None
    _gpkgLoader = None
    _dxfLoader = None
    _imageLoader = None

    _orgColor = None
    _last_opened_folder = None
    _willRemoveGroupIds = None

    iGroupBox = 0
    groupBoxList = None

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
        # self.btnReportError.hide()

        self.groupBoxList = dict()

        self.dockableMirrors = []
        self.lastDockableMirror = 0

        ip = socket.gethostbyname(socket.gethostname())
        # 지리원 내부 IP 확인
        # if re.match(r"10\.98\..*", ip) is not None:
        if False:
            self.btnLoadTms.setVisible(False)
            self.btnLoadBaseMap.setVisible(True)
        else:
            self.btnLoadTms.setVisible(True)
            self.btnLoadBaseMap.setVisible(False)

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

    def info(self, msg):
        if not self.displayInfo:
            return
        self.editLog.appendHtml(u'<font color="black">{}</font>'.format(msg))

    def debug(self, msg):
        if not self.displayDebug:
            return
        self.editLog.appendHtml(u'<font color="green">{}</font>'.format(msg))

    def comment(self, msg):
        if not self.displayComment:
            return
        self.editLog.appendHtml(u'<font color="blue"><b>{}</b></font>'.format(msg))

    # 상태정보 표시
    def progText(self, text):
        self.lblStatus.setText(text)

    @staticmethod
    def alert(text, icon=QMessageBox.Information):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle(u"국토기본정보 공간정보 중첩 검사 툴")
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()

    def _connect_action(self):
        self.connect(self.btnAutoDetect, SIGNAL("clicked()"), self._on_click_btnAutoDetect)
        self.connect(self.btnLoadVector, SIGNAL("clicked()"), self._on_click_btnLoadVector)
        self.connect(self.btnLoadImage, SIGNAL("clicked()"), self._on_click_btnLoadImage)
        self.connect(self.btnLoadTms, SIGNAL("clicked()"), self._on_click_btnLoadTms)
        self.connect(self.btnLoadBaseMap, SIGNAL("clicked()"), self._on_click_btnLoadBaseMap)
        self.connect(self.btnReportError, SIGNAL("clicked()"), self._on_click_btnReportError)

        root = QgsProject.instance().layerTreeRoot()
        root.willRemoveChildren.connect(self.onWillRemoveChildren)  # 이 이벤트는 제거되거나 이동되는 레이어를 찾을 수 있음
        root.removedChildren.connect(self.onRemovedChildren)  # 이 이벤트는 제거된 후에 남은 레이어를 찾을 수 있음

    def onWillRemoveChildren(self, node, indexFrom, indexTo):
        self.debug("[Will] indexFrom: {}, indexTo:{}".format(indexFrom, indexTo))
        self._willRemoveGroupIds = list()

        # 제거 예정인 그룹박스 ID 확보
        children = node.children()[indexFrom : indexTo + 1]
        for realNode in children:
            groupId = realNode.customProperty("groupId")
            if groupId is not None:
                self._willRemoveGroupIds.append(int(groupId))

    def onRemovedChildren(self, node, indexFrom, indexTo):
        self.debug("[remover] indexFrom: {}, indexTo:{}".format(indexFrom, indexTo))
        remainedGroupIds = list()

        # 남아있는 그룹박스 ID 확보
        children = node.children()
        for realNode in children:
            groupId = realNode.customProperty("groupId")
            if groupId is not None:
                remainedGroupIds.append(int(groupId))

        # 트리 그룹이 단순히 이동되었을 때를 위해 삭제 표시된 것 중 남아있는 것 제외하고 제거 실행
        removedGroupIds = [item for item in self._willRemoveGroupIds if item not in remainedGroupIds]
        for groupId in removedGroupIds:
            self.debug("Remove GroupID: {}".format(groupId))
            self.removeLayerTreeByGroupId(groupId)

    def _createLoader(self):
        self._autoDetecter = AutoDetect(self.iface, self)
        self._onMapLoader = OnMapLoader(self.iface, self)
        self._shpLoader = ShpLoader(self.iface, self)
        self._gpkgLoader = GpkgLoader(self.iface, self)
        self._dxfLoader = DxfLoader(self.iface, self)
        self._imageLoader = ImageLoader(self.iface, self)

    def _on_click_btnAutoDetect(self):
        res = self._autoDetecter.checkEnv()
        if not res:
            return

        self._autoDetecter.connectPg()
        self._autoDetecter.show()

    def _on_click_btnLoadVector(self):
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
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        if self._last_opened_folder is not None:
            dialog.setDirectory(self._last_opened_folder)
        # dialog.setFileMode(QtGui.QFileDialog.Directory )

        filters = [u"국토지리정보 영상 파일(*.img *.tif)"]
        dialog.setNameFilters(filters)

        if (dialog.exec_()):
            fileList = dialog.selectedFiles()
        else:
            return

        for rasterPath in fileList:
            filename, extension = os.path.splitext(rasterPath)

            if extension.lower() == ".img" or extension.lower() == ".tif":
                self._imageLoader.runImport(rasterPath)

    def _on_click_btnLoadTms(self):
        # 지도종류 선택 받기
        dlg = DlgMapSelect(self.iface.mainWindow())
        rc = dlg.exec_()
        if rc != QDialog.Accepted:
            return

        internetMap = TmsForKorea.classFactory(self.iface)

        # 최상위 그룹 찾고
        root = QgsProject.instance().layerTreeRoot()

        # '인터넷지도' 그룹이 있는지 확인
        layerTreeGroup = root.findGroup(u"인터넷지도")

        if layerTreeGroup:  # 있으면 속한 레이어 지우고
            for layerNode in layerTreeGroup.findLayers():
                extLayer = layerNode.layer()
                layerTreeGroup.removeLayer(extLayer)
        else:  # 없으면 만들기
            layerTreeGroup = root.addGroup(u"인터넷지도")

        if dlg.rdoNgiiMap.isChecked():
            internetMap.addLayer(OlNgiiStreetLayer(), layerTreeGroup)
        elif dlg.rdoNgiiContrast.isChecked():
            internetMap.addLayer(OlNgiiColorBlindLayer(), layerTreeGroup)
        elif dlg.rdoNgiiBigFont.isChecked():
            internetMap.addLayer(OlNgiiHighDensityLayer(), layerTreeGroup)
        elif dlg.rdoNgiiWhite.isChecked():
            internetMap.addLayer(OlNgiiBlankLayer(), layerTreeGroup)
        elif dlg.rdoNgiiEng.isChecked():
            internetMap.addLayer(OlNgiiEnglishLayer(), layerTreeGroup)
        elif dlg.rdoNgiiChn.isChecked():
            internetMap.addLayer(OlNgiiChineseLayer(), layerTreeGroup)
        elif dlg.rdoNgiiJpn.isChecked():
            internetMap.addLayer(OlNgiiJapaneseLayer(), layerTreeGroup)
        elif dlg.rdoDaumMap.isChecked():
            internetMap.addLayer(OlDaumStreetLayer(), layerTreeGroup)
        elif dlg.rdoDaumPhoto.isChecked():
            internetMap.addLayer(OlDaumHybridLayer(), layerTreeGroup)
        elif dlg.rdoNaverMap.isChecked():
            internetMap.addLayer(OlNaverStreetLayer(), layerTreeGroup)
        elif dlg.rdoNaverPhoto.isChecked():
            internetMap.addLayer(OlNaverHybridLayer(), layerTreeGroup)
        elif dlg.rdoOllehMap.isChecked():
            internetMap.addLayer(OlOllehStreetLayer(), layerTreeGroup)
        elif dlg.rdoOllehImage.isChecked():
            internetMap.addLayer(OlOllehHybridLayer(), layerTreeGroup)
        elif dlg.rdoOllehLight.isChecked():
            internetMap.addLayer(OlOllehSimpleLayer(), layerTreeGroup)

        # 투명도 조절이나 색상 변경이 안된다.
        # self.appendGroupBox(layerTreeGroup, "TMS")

    def loadWms(self, layerList, title):
        layersText = u"&layers=".join(layerList)
        stylesText = u"&styles=" * len(layerList)
        # urlWithParams = u'crs=EPSG:5179&dpiMode=7&format=image/png&layers={}{}&url=http://seoul.gaia3d.com:8989/geoserver/wms?'.format(layersText, stylesText)
        urlWithParams = u'crs=EPSG:5179&dpiMode=7&format=image/png&layers={}{}&url=http://10.98.25.39:8080/geoserver/wms?'.format(layersText, stylesText)
        self.debug(urlWithParams)
        rlayer = QgsRasterLayer(urlWithParams, title, 'wms')
        rlayer.isValid()
        QgsMapLayerRegistry.instance().addMapLayer(rlayer)

    def _on_click_btnLoadBaseMap(self):
        canvas = self.iface.mapCanvas()
        scale = canvas.scale()
        if scale > 50000:
            self.alert(u"1:50,000 보다 크게 확대하셔야 사용 가능합니다.")
            return

        # TODO: 레이어를 선택할 수 있는 대화상자를 만들어야 한다.
        # layerList = ["tn_alpt","tn_arafc","tn_arhfc","tn_arpgr","tn_arrfc","tn_arsfc","tn_arwfc","tn_bcycl_ctln","tn_buld","tn_buld_adcls","tn_ctprvn_bndry","tn_ctrln","tn_emd_bndry","tn_fclty_zone_bndry","tn_fmlnd_bndry","tn_ftpth_bndry","tn_ftpth_ctln","tn_lkmh","tn_lnafc","tn_lnpgr","tn_lnrfc","tn_lnsfc","tn_mtc_bndry","tn_ptafc","tn_pthfc","tn_ptpgr","tn_ptrfc","tn_ptsfc","tn_ptwfc","tn_river_bndry","tn_river_bt","tn_river_ctln","tn_rlroad_bndry","tn_rlroad_ctln","tn_rodway_bndry","tn_rodway_ctln","tn_shorline","tn_signgu_bndry","tn_wtcors_fclty"]
        # layerList = ["tn_shorline","tn_lkmh", "tn_river_bt","tn_river_bndry","tn_river_ctln", "tn_fmlnd_bndry","tn_rodway_bndry","tn_rodway_ctln","tn_ctrln","tn_buld_adcls","tn_buld"]
        layerList = ["ngd_all"]
        self.loadWms(layerList, u'국토기본정보')

    def _on_click_btnReportError(self):
        if self.displayDebug:
            self.connectRemoteDebugger()
        else:
            self.enterReasion()

    def enterReasion(self):
        dlg = DlgReportError(self)
        if not dlg.exec_():
            return

        _, tempFilePath = tempfile.mkstemp(".png")
        self.iface.mapCanvas().saveAsImage(tempFilePath)
        self.debug(tempFilePath)

        with open(tempFilePath, "rb") as imgFile:
            imgStr = imgFile.read().encode('base64')

        # 썸네일 생성
        tnImgPath = "{}_tn.png".format(os.path.splitext(tempFilePath)[0])
        size = (256, 256)
        try:
            im = Image.open(tempFilePath)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(tnImgPath)

            result = True
        except IOError:
            return

        with open(tnImgPath, "rb") as imgFile:
            imgTnStr = imgFile.read().encode('base64')

        imgExtent = self.iface.mapCanvas().extent()

        # API 호출
        saveUrl = 'http://seoul.gaia3d.com:8989/kqiweb/'
        restapiUrl = saveUrl + 'kgi/insert_overlay.do'

        savaData = {
            "insTargetNm": "", # 오버레이 대상명 리스트
            "insResult": dlg.lineEdit.text(),
            "imgNm": os.path.basename(tempFilePath),
            "img": imgStr,
            "imgTn": imgTnStr,
            "minX": round(imgExtent.xMinimum(), 2),
            "minY": round(imgExtent.yMinimum(), 2),
            "maxX": round(imgExtent.xMaximum(), 2),
            "maxY": round(imgExtent.yMaximum(), 2)
        }

        try:
            request = urllib2.Request(restapiUrl, json.dumps(savaData),
                                      {'Content-Type': 'application/json'})
            response = urllib2.urlopen(request)

            res_code = response.getcode()
            if res_code != 200:
                self.logger.warning(response.info())
                return result

        except Exception as e:
            return


    def getNewGroupTitle(self, title):
        dupeCount = 0

        filter = u"{}(\\d*)".format(title)
        for key in self.groupBoxList:
            groupBox = self.groupBoxList[key]
            if re.match(filter, title):
                dupeCount += 1

        if dupeCount > 0:
            title += u"({})".format(dupeCount + 1)

        return title

    def appendGroupBox(self, layerTreeGroup, type):
        if layerTreeGroup is not None:
            title = layerTreeGroup.name()
        else:
            raise Exception("mainGroup not defined")

        if type == "img" or type == "tif":
            isRaster = True
        else:
            isRaster = False

        self.iGroupBox += 1
        layerTreeGroup.uiId = self.iGroupBox
        layerTreeGroup.type = type

        self.groupBoxList[self.iGroupBox] = dict()
        self.groupBoxList[self.iGroupBox]["id"] = self.iGroupBox
        self.groupBoxList[self.iGroupBox]["type"] = type
        self.groupBoxList[self.iGroupBox]["title"] = title
        self.groupBoxList[self.iGroupBox]["treeItem"] = layerTreeGroup
        self.groupBoxList[self.iGroupBox]["groupBox"] = None

        spacerItem = self.gridLayout_2.itemAtPosition(self.iGroupBox - 1, 0)
        if spacerItem is not None:
            self.gridLayout_2.removeItem(spacerItem)

        groupBox_1 = self.groupBoxList[self.iGroupBox]["groupBox"] = QMyGroupBox(self.scrollAreaWidgetContents)
        groupBox_1.id = self.iGroupBox
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(groupBox_1.sizePolicy().hasHeightForWidth())
        groupBox_1.setSizePolicy(sizePolicy)
        groupBox_1.setMaximumSize(QSize(280, 130))
        groupBox_1.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        groupBox_1.setObjectName("groupBox_{}".format(self.iGroupBox))
        gridLayout = QGridLayout(groupBox_1)
        gridLayout.setObjectName("gridLayout")

        horLayout1_1 = QHBoxLayout()
        horLayout1_1.setObjectName("horLayout1_{}".format(self.iGroupBox))
        btnToSpWin_1 = QPushButton(groupBox_1)
        btnToSpWin_1.setObjectName("btnToSpWin_{}".format(self.iGroupBox))
        horLayout1_1.addWidget(btnToSpWin_1)
        # btnRemove_1 = QPushButton(groupBox_1)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(btnRemove_1.sizePolicy().hasHeightForWidth())
        # btnRemove_1.setSizePolicy(sizePolicy)
        # btnRemove_1.setObjectName("btnRemove_{}".format(self.iGroupBox))
        # horLayout1_1.addWidget(btnRemove_1)
        gridLayout.addLayout(horLayout1_1, 0, 0, 1, 1)

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

        groupBox_1.setTitle(title)
        btnToSpWin_1.setText(u"분할창에 띄우기")
        # btnRemove_1.setText(u"제거")
        lblTrans_1.setText(u"투명도:")

        if not isRaster:
            horLayout3_1 = QHBoxLayout()
            horLayout3_1.setObjectName("horLayout3_{}".format(self.iGroupBox))
            lblColor_1 = QLabel(groupBox_1)
            lblColor_1.setObjectName("lblColor_{}".format(self.iGroupBox))
            lblColor_1.setText(u"색  상:")
            horLayout3_1.addWidget(lblColor_1)
            btnSelColor_1 = QgsColorButton(groupBox_1)
            btnSelColor_1.setObjectName("btnSelColor_{}".format(self.iGroupBox))
            horLayout3_1.addWidget(btnSelColor_1)
            gridLayout.addLayout(horLayout3_1, 2, 0, 1, 1)

        self.gridLayout_2.addWidget(groupBox_1, self.iGroupBox - 1, 0, 1, 1)

        # 그룹을 위한 버튼들 액션 추가
        btnToSpWin_1.clicked.connect(lambda: self._onGroupBoxSubButtonClick(btnToSpWin_1))
        # btnRemove_1.clicked.connect(lambda: self._onGroupBoxSubButtonClick(btnRemove_1))
        if not isRaster:
            btnSelColor_1.clicked.connect(lambda: self._onGroupBoxColorButtonClick(btnSelColor_1))
            btnSelColor_1.colorChanged.connect(lambda: self._onGroupBoxColorChanged(btnSelColor_1))
        sldTrans_1.sliderReleased.connect(lambda: self._onGroupBoxSliderReleased(sldTrans_1))

        # 레이어 트리의 제거시 액션 추가
        layerTreeGroup.setCustomProperty("groupId", self.iGroupBox)
        groupBox_1.groupId = self.iGroupBox

        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, self.iGroupBox, 0, 1, 1)

    def removeLayerTreeByGroupId(self, groupId):
        if len(self.groupBoxList) <= 0:
            return

        items = (self.gridLayout_2.itemAt(i) for i in range(self.gridLayout_2.count()))
        for item in items:
            widget = item.widget()
            if not widget:
                continue

            if isinstance(widget, QMyGroupBox):
                if widget.groupId == groupId:
                    try:
                        self.groupBoxList.pop(groupId)
                        widget.deleteLater()
                    except KeyError:
                        pass

    def removeGroupBox(self, groupObj):
        if not groupObj: return

        groupBox = groupObj["groupBox"]
        if not groupBox: return

        self.debug(u"Remove Group Box {}".format(groupBox.title()))
        groupBox.deleteLater()

        treeNode = groupObj["treeItem"]
        if not treeNode: return
        parentNode = treeNode.parent()
        if not parentNode: return
        parentNode.removeChildNode(treeNode)

    def _onGroupBoxSubButtonClick(self, buttonObj):
        try:
            groupId = buttonObj.parent().id
            buttonTitle = buttonObj.text()

            try:
                groupObj = self.groupBoxList[groupId]
            except Exception as e:
                raise e

        except Exception as e:
            raise e

        if buttonTitle == u"제거":
            self.removeGroupBox(groupObj)
        elif buttonTitle == u"분할창에 띄우기":
            self.createSplitWindow(groupObj)
        else:
            return

    def createSplitWindow(self, groupObj):
        # self.splitWidget = MirrorMap(self, self.iface)
        # \\self.location = Qt.BottomDockWidgetArea
        wdg = DockableMirrorMap(self.iface.mainWindow(), self.iface)
        wdg.setLocation(Qt.BottomDockWidgetArea)

        minsize = wdg.minimumSize()
        maxsize = wdg.maximumSize()

        self.setupDockWidget(wdg)
        self.addDockWidget(wdg)

        wdg.setMinimumSize(minsize)
        wdg.setMaximumSize(maxsize)

        # if wdg.isFloating():
        #     wdg.move(50, 50)  # move the widget to the center

        treeNode = groupObj["treeItem"]
        self.addGroupToSplitWindow(treeNode, wdg)
        treeNode.setVisible(Qt.Unchecked)


    def addGroupToSplitWindow(self, treeNode, wdg):
        for node in treeNode.children():
            nodeType = node.nodeType()

            # 그룹인 경우 재귀호출
            if nodeType == QgsLayerTreeNode.NodeGroup:
                self.addGroupToSplitWindow(node, wdg)
            elif nodeType == QgsLayerTreeNode.NodeLayer:
                layer = node.layer()
                self.iface.layerTreeView().setCurrentLayer(layer)
                wdg.mainWidget.addLayer()

    def setupDockWidget(self, wdg):
        # othersize = QGridLayout().verticalSpacing()
        #
        # if len(self.dockableMirrors) <= 0:
        #     width = self.iface.mapCanvas().size().width() / 2 - othersize
        #     wdg.setLocation(Qt.RightDockWidgetArea)
        #     wdg.setMinimumWidth(width)
        #     wdg.setMaximumWidth(width)
        #
        # elif len(self.dockableMirrors) == 1:
        #     height = self.dockableMirrors[0].size().height() / 2 - othersize / 2
        #     wdg.setLocation(Qt.RightDockWidgetArea)
        #     wdg.setMinimumHeight(height)
        #     wdg.setMaximumHeight(height)
        #
        # elif len(self.dockableMirrors) == 2:
        #     height = self.iface.mapCanvas().size().height() / 2 - othersize / 2
        #     wdg.setLocation(Qt.BottomDockWidgetArea)
        #     wdg.setMinimumHeight(height)
        #     wdg.setMaximumHeight(height)
        #
        # else:
        #     wdg.setLocation(Qt.BottomDockWidgetArea)
        #     wdg.setFloating(True)

        height = self.iface.mapCanvas().size().height() / 2
        wdg.setMinimumHeight(height)
        wdg.setMaximumHeight(height)
        wdg.setLocation(Qt.BottomDockWidgetArea)

    def addDockWidget(self, wdg, position=None):
        if position == None:
            position = wdg.getLocation()
        else:
            wdg.setLocation(position)

        mapCanvas = self.iface.mapCanvas()
        oldSize = mapCanvas.size()

        prevFlag = mapCanvas.renderFlag()
        mapCanvas.setRenderFlag(False)
        self.iface.addDockWidget(position, wdg)

        wdg.setNumber(self.lastDockableMirror)
        self.lastDockableMirror = self.lastDockableMirror + 1
        self.dockableMirrors.append(wdg)

        QObject.connect(wdg, SIGNAL("closed(PyQt_PyObject)"), self.onCloseDockableMirror)

        newSize = mapCanvas.size()
        if newSize != oldSize:
            # trick: update the canvas size
            mapCanvas.resize(newSize.width() - 1, newSize.height())
            mapCanvas.setRenderFlag(prevFlag)
            mapCanvas.resize(newSize)
        else:
            mapCanvas.setRenderFlag(prevFlag)

    def onCloseDockableMirror(self, wdg):
        if self.dockableMirrors.count(wdg) > 0:
            self.dockableMirrors.remove(wdg)

        if len(self.dockableMirrors) <= 0:
            self.lastDockableMirror = 0

    def _onGroupBoxSliderReleased(self, sliderObj):
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

    def _onGroupBoxColorButtonClick(self, buttonObj):
        self._orgColor = buttonObj.color()
        buttonObj.show()

    def _onGroupBoxColorChanged(self, buttonObj):
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
                        # TODO: 패턴이 먹게 수정 필요
                        symbol = QgsFillSymbolV2().createSimple({'color': colorText, 'outline_color': colorText, 'name': 'x'})
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
