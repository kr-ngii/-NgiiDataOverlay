# -*- coding: utf-8 -*-

import os
from qgis.core import *
from PyQt4.QtCore import Qt, QSettings
from .. calc_utils import findMapNo, mapNoToCrs

#########################
# MAIN CLASS
#########################
class ImageLoader():
    iface = None
    parent = None

    def __init__(self, iface, parent):
        self.iface = iface
        self.parent = parent
        self.progressMain = parent.prgMain
        self.progressSub = parent.prgSub
        self.lblStatus = parent.lblStatus

        self.info = parent.info
        self.error = parent.error
        self.debug = parent.debug
        self.comment = parent.comment
        self.progText = parent.progText
        self.alert = parent.alert

    def runImport(self, filePath):
        # 그룹부터 만들고
        filename, ext = os.path.splitext(os.path.basename(filePath))
        title = self.parent.getNewGroupTitle(u"[IMG]"+filename)

        root = QgsProject.instance().layerTreeRoot()
        layerTreeGroup = root.addGroup(title)

        self.importImg(filePath, layerTreeGroup)

        self.parent.appendGroupBox(layerTreeGroup, ext.lstrip("."))

    def importImg(self, filePath, layerTreeGroup):
        fileBase, extension = os.path.splitext(os.path.basename(filePath))

        # 좌표계 판단
        mapNo = findMapNo(fileBase, flagImage=True)
        if mapNo is None:
            crsID = 5179
        else:
            crsID = mapNoToCrs(mapNo)

        QgsApplication.setOverrideCursor(Qt.WaitCursor)

        # 좌표계 정보 누락시 QGIS가 띄우는 창 막기
        # https://gis.stackexchange.com/questions/80025/accessing-qgis-program-settings-programmatically
        settings = QSettings()
        # Take the "CRS for new layers" config, overwrite it while loading layers and...
        oldProjValue = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")

        try:
            filename, ext = os.path.splitext(os.path.basename(filePath))
            self.progText(u"{}{} 파일 읽는 중".format(filename, ext))

            rlayer = QgsRasterLayer(filePath, filename)
            rlayer.setCrs(QgsCoordinateReferenceSystem(crsID, QgsCoordinateReferenceSystem.EpsgCrsId))
            if not rlayer.isValid():
                raise Exception(u"Layer failed to load!")

            settings.setValue("/Projections/defaultBehaviour", oldProjValue)

            QgsMapLayerRegistry.instance().addMapLayer(rlayer, False)
            layerTreeGroup.insertChildNode(1, QgsLayerTreeLayer(rlayer))
        except Exception as e:
            raise e
        finally:
            self.progressSub.setValue(0)
            self.progText(u"DXF에서 정보 추출 완료")
            settings.setValue("/Projections/defaultBehaviour", oldProjValue)
            self.progressMain.setValue(0)
            self.progressSub.setValue(0)

            QgsApplication.restoreOverrideCursor()
            self.progressSub.setValue(0)