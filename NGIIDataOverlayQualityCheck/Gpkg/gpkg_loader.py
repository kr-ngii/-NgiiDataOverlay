# -*- coding: utf-8 -*-

import os
from qgis.core import *
from osgeo import ogr, gdal
from PyQt4.QtCore import Qt
from .. calc_utils import force_gui_update

ogr.UseExceptions()


class GpkgLoader():
    iface = None
    parent = None

    def __init__(self, iface, parent):
        self.iface = iface
        self.parent = parent

    def runImport(self, filePath):
        # 그룹부터 만들고
        filename, _ = os.path.splitext(os.path.basename(filePath))
        title = self.parent.getNewGroupTitle(u"[GPKG]" + filename)

        root = QgsProject.instance().layerTreeRoot()
        layerTreeGroup = root.addGroup(title)

        # 하나씩 임포트
        try:
            self.importGpkg(filePath, layerTreeGroup)

        except Exception as e:
            raise e

        self.parent.appendGroupBox(layerTreeGroup, "gpkg")

    def importGpkg(self, filePath, layerTreeGroup):
        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        gpkg = None

        try:
            # TODO: 속도 향상에 아래 문장이 매우 중요. 다른 곳에도 적용하자!!
            gdal.SetConfigOption('OGR_SQLITE_SYNCHRONOUS', 'OFF')
            gpkg = ogr.Open(filePath)
            if not gpkg:
                raise Exception()

            # Load Layer
            for layer in gpkg:
                force_gui_update()
                layerName = unicode(layer.GetName().decode('utf-8'))

                uri = u"{}|layername={}".format(filePath, layerName)
                layer = QgsVectorLayer(uri, layerName, "ogr")
                QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                layerTreeGroup.insertChildNode(1, QgsLayerTreeLayer(layer))
        except Exception as e:
            raise e
        finally:
            QgsApplication.restoreOverrideCursor()
            self.progressMain.setValue(0)
            self.progressSub.setValue(0)
            del gpkg