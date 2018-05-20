# -*- coding: utf-8 -*-

import os
from qgis.core import *
from osgeo import ogr


class DxfLoader():
    iface = None
    parent = None

    def __init__(self, iface, filePath):
        self.iface
        self.parent

    def runImport(self, filePath):
        srcDriver = ogr.GetDriverByName("DXF")

        # 그룹부터 만들고
        filename, _ = os.path.splitext(os.path.basename(filePath))
        root = QgsProject.instance().layerTreeRoot()
        mainGroup = root.addGroup(filename)

        # 하나씩 임포트
        try:
            # TODO: 좌표계는 일단 무조건 5186으로
            layer = srcDriver.Open(filePath, 0)
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            mainGroup.insertChildNode(1, QgsLayerTreeLayer(layer))

        except Exception as e:
            raise e
