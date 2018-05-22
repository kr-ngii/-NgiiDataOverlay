# -*- coding: utf-8 -*-

import os
from qgis.core import *
from osgeo import ogr


class DxfLoader():
    iface = None
    parent = None

    def __init__(self, iface, parent):
        self.iface = iface
        self.parent = parent

    def runImport(self, filePath):
        srcDriver = ogr.GetDriverByName("DXF")

        # 그룹부터 만들고
        filename, _ = os.path.splitext(os.path.basename(filePath))
        title = self.parent.getNewGroupTitle(filename)

        # 그룹부터 만들고
        root = QgsProject.instance().layerTreeRoot()
        layerTreeGroup = root.addGroup(title)

        # 하나씩 임포트
        try:
            self.importDxf(filePath, layerTreeGroup)

        except Exception as e:
            raise e

        self.parent.appendGroupBox(layerTreeGroup, "dxf")


    def importDxf(self, filePath, layerTreeGroup):
        filename, extension = os.path.splitext(os.path.basename(filePath))

        # TODO: 좌표계가 없을 가능성에 대비하라
        layer = QgsVectorLayer(filePath, filename, "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        layerTreeGroup.insertChildNode(1, QgsLayerTreeLayer(layer))

