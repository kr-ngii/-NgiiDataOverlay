# -*- coding: utf-8 -*-

import os
from qgis.core import *
from osgeo import ogr

ogr.UseExceptions()


class ShpLoader():
    iface = None
    parent = None

    def __init__(self, iface, parent):
        self.iface = iface
        self.parent = parent

    def runImport(self, fileList):
        if len(fileList) <= 0: return

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
            try:
                self.importShp(filePath, layerTreeGroup)
            except Exception as e:
                raise e

        self.parent.appendGroupBox(layerTreeGroup, "shp")


    def importShp(self, filePath, layerTreeGroup):
        filename, extension = os.path.splitext(os.path.basename(filePath))

        # TODO: 좌표계가 없을 가능성에 대비하라
        layer = QgsVectorLayer(filePath, filename, "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        layerTreeGroup.insertChildNode(1, QgsLayerTreeLayer(layer))

