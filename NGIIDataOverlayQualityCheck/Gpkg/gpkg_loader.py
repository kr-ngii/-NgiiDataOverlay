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


    def runImport(self, filePath):
        QgsApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            self.info(u"GPKG 중첩 시작")
            self.progText(u"GPKG 중첩 중...")
            self.progressMain.setMinimum(0)
            self.progressMain.setMaximum(0)

            # 그룹부터 만들고
            filename, _ = os.path.splitext(os.path.basename(filePath))
            title = self.parent.getNewGroupTitle(u"[GPKG]" + filename)

            root = QgsProject.instance().layerTreeRoot()
            layerTreeGroup = root.addGroup(title)

            try:
                self.importGpkg(filePath, layerTreeGroup)

            except Exception as e:
                raise e

            self.parent.appendGroupBox(layerTreeGroup, "gpkg")
            self.info(u"GPKG 중첩 완료")
        except Exception as e:
            raise e
        finally:
            QgsApplication.restoreOverrideCursor()

            self.progText(u"")
            self.progressMain.setValue(0)
            self.progressSub.setValue(0)


    def importGpkg(self, filePath, layerTreeGroup):
        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        gpkg = None

        try:
            # TODO: GPKG 속도 향상에 아래 문장이 매우 중요. 다른 곳에도 적용하자!!
            gdal.SetConfigOption('OGR_SQLITE_SYNCHRONOUS', 'OFF')
            gpkg = ogr.Open(filePath)
            if not gpkg:
                raise Exception()

            # Load Layer
            numLayer = gpkg.GetLayerCount()
            self.progressMain.setMaximum(numLayer)

            i = 0
            for layer in gpkg:
                i += 1
                self.progressMain.setValue(i)

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
            self.progressMain.setMaximum(100)
            del gpkg