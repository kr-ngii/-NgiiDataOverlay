# -*- coding: utf-8 -*-

import os
from qgis.core import *
from osgeo import ogr
from PyQt4.QtCore import Qt, QSettings
from .. calc_utils import force_gui_update, findEncoding, findMapNo, mapNoToCrs

ogr.UseExceptions()


class ShpLoader():
    iface = None
    parent = None

    def __init__(self, iface, parent):
        self.iface = iface
        self.parent = parent
        try:
            self.progressMain = parent.prgMain
            self.progressSub = parent.prgSub

            self.info = parent.info
            self.error = parent.error
            self.debug = parent.debug
            self.comment = parent.comment
            self.progText = parent.progText
            self.alert = parent.alert
        except Exception as e:
            raise e

    def runImport(self, fileList):
        if len(fileList) <= 0: return

        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        # 좌표계 정보 누락시 QGIS가 띄우는 창 막기
        # https://gis.stackexchange.com/questions/80025/accessing-qgis-program-settings-programmatically
        settings = QSettings()
        # Take the "CRS for new layers" config, overwrite it while loading layers and...
        oldProjValue = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")

        try:
            self.info(u"SHP 중첩 시작")
            self.progText(u"SHP 중첩 중...")
            self.progressMain.setMinimum(0)
            self.progressMain.setMaximum(len(fileList))

            # 그룹명을 폴더명으로
            title = os.path.basename(os.path.split(fileList[0])[0])
            if title == "":
                title = u"ESRI Shape"

            groupTitle = self.parent.getNewGroupTitle(u"[SHP]" + title)

            # 그룹부터 만들고
            root = QgsProject.instance().layerTreeRoot()
            layerTreeGroup = root.addGroup(groupTitle)

            # Shape 좌표계는 항상 전국 좌표계
            crsID = 5179

            # 하나씩 임포트
            i = 0
            for filePath in fileList:
                i += 1
                self.progressMain.setValue(i)

                force_gui_update()
                self.importShp(filePath, layerTreeGroup, crsID)

            self.parent.appendGroupBox(layerTreeGroup, "shp")

            self.info(u"SHP 중첩 완료")

        except Exception as e:
            raise e
        finally:
            settings.setValue("/Projections/defaultBehaviour", oldProjValue)
            QgsApplication.restoreOverrideCursor()

            self.progText(u"")
            self.progressMain.setValue(0)
            self.progressSub.setValue(0)


    def importShp(self, filePath, layerTreeGroup, crsID):
        fileBase, extension = os.path.splitext(os.path.basename(filePath))

        layer = QgsVectorLayer(filePath, fileBase, "ogr")

        # 좌표계 설정
        crs = layer.crs()
        crs.createFromId(crsID)
        layer.setCrs(crs)

        # 한글 코드 판단
        dbfFilePath = filePath.rstrip(extension) + ".dbf"
        encoding = findEncoding(dbfFilePath)

        # 인코딩 설정
        layer.setProviderEncoding(encoding)
        layer.dataProvider().setEncoding(encoding)

        # 레이어 패널에 추가하지 않고 레이어 등록
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)

        # 그룹에 추가
        layerTreeGroup.insertChildNode(1, QgsLayerTreeLayer(layer))

