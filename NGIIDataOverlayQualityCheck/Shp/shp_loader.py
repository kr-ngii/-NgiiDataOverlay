# -*- coding: utf-8 -*-

import os
from qgis.core import *
from osgeo import ogr

ogr.UseExceptions()


class ShpLoader():
    iface = None
    parent = None

    def __init__(self, iface, parent):
        self.iface
        self.parent

    def runImport(self, fileList):
        # 그룹부터 만들고
        root = QgsProject.instance().layerTreeRoot()
        mainGroup = root.addGroup(u"ESRI Shape")

        # 하나씩 임포트
        for filePath in fileList:
            try:
                filename, extension = os.path.splitext(os.path.basename(filePath))

                # TODO: 좌표계가 없을 가능성에 대비하라
                layer = QgsVectorLayer(filePath, filename, "ogr")
                QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                mainGroup.insertChildNode(1, QgsLayerTreeLayer(layer))

            except Exception as e:
                raise e
