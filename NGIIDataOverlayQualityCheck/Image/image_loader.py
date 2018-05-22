# -*- coding: utf-8 -*-

import os
from qgis.core import *
from PyQt4.QtCore import Qt, QSettings

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
        title = self.parent.getNewGroupTitle(filename)

        root = QgsProject.instance().layerTreeRoot()
        layerTreeGroup = root.addGroup(title)

        self.importImg(filePath, layerTreeGroup)

        self.parent.appendGroupBox(layerTreeGroup, ext)

    def importImg(self, filePath, layerTreeGroup):
        # TODO: 파일명에서 좌표계를 찾아라!
        QgsApplication.setOverrideCursor(Qt.WaitCursor)

        # 좌표계 안물어보게 하기
        # https://gis.stackexchange.com/questions/80025/accessing-qgis-program-settings-programmatically
        settings = QSettings()
        # Take the "CRS for new layers" config, overwrite it while loading layers and...
        oldProjValue = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")

        try:
            filename, ext = os.path.splitext(os.path.basename(filePath))
            self.progText(u"{}{} 파일 읽는 중".format(filename, ext))

            rlayer = QgsRasterLayer(filePath, filename)
            rlayer.setCrs(QgsCoordinateReferenceSystem(5186, QgsCoordinateReferenceSystem.EpsgCrsId))
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

            QgsApplication.restoreOverrideCursor()
            self.progressSub.setValue(0)