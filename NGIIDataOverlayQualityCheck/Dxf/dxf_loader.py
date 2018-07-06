# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import *
from qgis.core import *
from osgeo import ogr, osr
from .. calc_utils import force_gui_update, findMapNo, mapNoToCrs

ogr.UseExceptions()


class DxfLoader():
    iface = None
    parent = None

    layerCountDict = None
    layerListDict = None

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
        self.layerCountDict = dict()
        self.layerListDict = dict()

        # 그룹부터 만들고
        filename, _ = os.path.splitext(os.path.basename(filePath))
        title = self.parent.getNewGroupTitle(u"[DXF]"+filename)

        root = QgsProject.instance().layerTreeRoot()
        layerTreeGroup = root.addGroup(title)

        # 하나씩 임포트
        try:
            self.importDxf(filePath, layerTreeGroup)

        except Exception as e:
            raise e

        self.parent.appendGroupBox(layerTreeGroup, "dxf")

    def importDxf(self, filePath, layerTreeGroup):
        self.parent.debug("1")
        fileBase, extension = os.path.splitext(os.path.basename(filePath))

        # 좌표계 판단
        self.parent.debug("2")
        mapNo = findMapNo(fileBase)
        if mapNo is None:
            crsID = 5179
        else:
            crsID = mapNoToCrs(mapNo)

        self.parent.debug("3")
        self.parent.info(u"CRS = {}".format(crsID))

        # 좌표계 정보 생성
        self.parent.debug("4")
        crs = osr.SpatialReference()
        crs.ImportFromEPSG(crsID)
        self.crsWkt = crs.ExportToWkt()

        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        # 좌표계 정보 누락시 QGIS가 띄우는 창 막기
        # https://gis.stackexchange.com/questions/80025/accessing-qgis-program-settings-programmatically
        settings = QSettings()
        # Take the "CRS for new layers" config, overwrite it while loading layers and...
        oldProjValue = settings.value("/Projections/defaultBehaviour", "prompt", type=str)
        settings.setValue("/Projections/defaultBehaviour", "useProject")

        dxfLayer = None
        try:
            self.progText(u"DXF에서 정보 추출 시작...")
            self.info(u"DXF에서 정보 추출 중")

            dxfLayer = QgsVectorLayer(filePath, None, "ogr")
            crs = dxfLayer.crs()
            crs.createFromId(crsID)
            dxfLayer.setCrs(crs)

            if not dxfLayer:
                raise Exception()

            dxfFeatures = dxfLayer.getFeatures()
            totalFeature = dxfLayer.featureCount()

            crrFeatureIndex = 0
            self.progressMain.setMinimum(0)
            self.progressMain.setMaximum(totalFeature)
            for dxfFeature in dxfFeatures:
                force_gui_update()

                crrFeatureIndex += 1
                self.progressMain.setValue(crrFeatureIndex)

                layerName = dxfFeature["Layer"]
                layerType = dxfFeature["SubClasses"]
                Linetype = dxfFeature["Linetype"]
                EntityHandle = dxfFeature["EntityHandle"]
                Text = dxfFeature["Text"]

                if layerType == "AcDbEntity:AcDbBlockReference":
                    entityType = "point"
                elif layerType == "AcDbEntity:AcDbPolyline":
                    entityType = "line"
                elif layerType == "AcDbEntity:AcDbText:AcDbText":
                    entityType = "point"
                else:
                    continue

                # layer 만들거나 얻어오기
                layerFullName = self.getLayerFullName(layerName, entityType)
                layer = self.layerListDict[layerFullName]

                geometry = dxfFeature.geometry()
                qgisFeature = QgsFeature()
                qgisFeature.setGeometry(geometry)

                qgisFeature.setAttributes([Linetype, EntityHandle, Text])
                layer.dataProvider().addFeatures([qgisFeature])


            for key in self.layerListDict.keys():
                layer = self.layerListDict[key]

                QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                layerTreeGroup.insertChildNode(1, QgsLayerTreeLayer(layer))
                layer.triggerRepaint()

        except Exception as e:
            raise e
        finally:
            self.progressMain.setValue(0)
            self.progText(u"")
            self.info(u"DXF에서 정보 추출 완료")
            settings.setValue("/Projections/defaultBehaviour", oldProjValue)
            self.progressMain.setValue(0)
            self.progressSub.setValue(0)

            QgsApplication.restoreOverrideCursor()
            self.progressSub.setValue(0)

            del dxfLayer

    def getLayerFullName(self, layerName, entityType):
        layerFullName = u"{}_{}".format(layerName, entityType)

        if self.layerCountDict.has_key(layerFullName):
            return layerFullName

        else:
            if entityType == "point":
                vPointLayer = QgsVectorLayer("Point?crs={}".format(self.crsWkt), layerFullName, "memory")
                vPointLayer.dataProvider().addAttributes([QgsField("Linetype", QVariant.String)])
                vPointLayer.dataProvider().addAttributes([QgsField("EntityHandle", QVariant.String)])
                vPointLayer.dataProvider().addAttributes([QgsField("Text", QVariant.String)])
                vPointLayer.updateFields()
                QgsMapLayerRegistry.instance().addMapLayer(vPointLayer, False)
                self.debug(u"layerName:" + layerFullName)
                vLayer = vPointLayer
            elif entityType == "line":
                vLineLayer = QgsVectorLayer("LineString?crs={}".format(self.crsWkt), layerFullName, "memory")
                vLineLayer.dataProvider().addAttributes([QgsField("Linetype", QVariant.String)])
                vLineLayer.dataProvider().addAttributes([QgsField("EntityHandle", QVariant.String)])
                vLineLayer.dataProvider().addAttributes([QgsField("Text", QVariant.String)])
                vLineLayer.updateFields()
                QgsMapLayerRegistry.instance().addMapLayer(vLineLayer, False)
                self.debug(u"layerName:" + layerFullName)
                vLayer = vLineLayer

            self.layerCountDict[layerFullName] = 0
            self.layerListDict[layerFullName] = vLayer

            return layerFullName
