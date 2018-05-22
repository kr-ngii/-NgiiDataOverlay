# -*- coding: utf-8 -*-

import os
from qgis.core import *
from osgeo import ogr
from PyQt4.QtCore import Qt, QSettings
from .. calc_utils import force_gui_update

ogr.UseExceptions()


class ShpLoader():
    iface = None
    parent = None

    def __init__(self, iface, parent):
        self.iface = iface
        self.parent = parent

    def runImport(self, fileList):
        if len(fileList) <= 0: return

        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        # 좌표계 안물어보게 하기
        # https://gis.stackexchange.com/questions/80025/accessing-qgis-program-settings-programmatically
        settings = QSettings()
        # Take the "CRS for new layers" config, overwrite it while loading layers and...
        oldProjValue = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")

        try:

            # 그룹명을 폴더명으로
            title = os.path.basename(os.path.split(fileList[0])[0])
            if title == "":
                title = u"ESRI Shape"

            title = self.parent.getNewGroupTitle(title)

            # 그룹부터 만들고
            root = QgsProject.instance().layerTreeRoot()
            layerTreeGroup = root.addGroup(title)

            # 하나씩 임포트
            for filePath in fileList:
                force_gui_update()
                self.importShp(filePath, layerTreeGroup)


            self.parent.appendGroupBox(layerTreeGroup, "shp")

        except Exception as e:
            raise e
        finally:
            settings.setValue("/Projections/defaultBehaviour", oldProjValue)
            QgsApplication.restoreOverrideCursor()

    def importShp(self, filePath, layerTreeGroup):
        filename, extension = os.path.splitext(os.path.basename(filePath))

        # TODO: 좌표계가 없을 가능성에 대비하라
        layer = QgsVectorLayer(filePath, filename, "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        layerTreeGroup.insertChildNode(1, QgsLayerTreeLayer(layer))

