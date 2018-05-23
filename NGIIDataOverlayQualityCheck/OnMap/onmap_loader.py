# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import copy
import os
from PIL import Image
from io import BytesIO
import tempfile
import threading, time
from shutil import copyfile

from .. calc_utils import *
from .. stopped_by_user_exception import StoppedByUserException

# import OGR
from osgeo import ogr, gdal, osr

gdal.UseExceptions()

try:
    from .. import PyPDF2
    from ..PyPDF2.filters import *
except:
    import pip

    pip.main(['install', "PyPDF2"])
    from .. import PyPDF2
    from ..PyPDF2.filters import *

# 기본 설정값
LAYER_FILTER = u"지도정보_"
MAP_BOX_LAYER = u"지도정보_도곽"
MAP_CLIP_LAYER = u"지도정보_Other"
NUM_FILTER = re.compile('.*_(\d*)')
SKIP_IMAGE_WIDTH = 2000
TEST_PDF_FILE_NAME = u"C:\\Temp\\(B090)온맵_37612058.pdf"


#########################
# CLASS for multitasking PDF Open
#########################
class PdfOpenThread(threading.Thread):
    # pdf = srcDriver.Open(self.pdfPath, 0)
    pdfPath = None
    outPdf = None

    def __init__(self,  pdfPath):
        self.pdfPath = pdfPath
        threading.Thread.__init__(self)

    def run(self):
        srcDriver = ogr.GetDriverByName("PDF")
        self.outPdf = srcDriver.Open(self.pdfPath, 0)

        return


#########################
# MAIN CLASS
#########################
class OnMapLoader():
    iface = None
    parent = None
    progressMain = None
    progressSub = None
    editLog = None

    pdfPath = None
    pdf = None
    layerInfoList = None
    affineTransform = None
    crsId = None
    mapNo = None
    bbox = None
    imgBox = None

    scrollAreaWidgetContents = None
    gridLayout_2 = None

    isOnProcessing = False
    forceStop = False

    def __init__(self, iface, parent):
        """Constructor."""
        self.iface = iface
        self.parent = parent
        try:
            self.progressMain = parent.prgMain
            self.progressSub = parent.prgSub
            self.lblStatus = parent.lblStatus
            self.editLog = parent.editLog
            self.scrollAreaWidgetContents = parent.scrollAreaWidgetContents
            self.gridLayout_2 = parent.gridLayout_2

            self.info = parent.info
            self.error = parent.error
            self.debug = parent.debug
            self.comment = parent.comment
            self.progText = parent.progText
            self.alert = parent.alert

            self.appendGroupBox = parent.appendGroupBox
            self.removeGroupBox = parent.removeGroupBox

        except Exception as e:
            raise e

    def runImport(self, filepath=TEST_PDF_FILE_NAME):
        self.pdfPath = filepath
        try:
            self.isOnProcessing = True

            if not os.path.exists(self.pdfPath):
                raise Exception(u"선택한 온맵(PDF) 파일이 존재하지 않습니다.")

            rc = self.getPdfInformation()
            if not rc:
                self.error(u"PDF 파일에서 정보를 추출하지 못했습니다. 온맵 PDF가 아닌 듯 합니다.")
                raise Exception(u"PDF 파일에서 정보를 추출하지 못했습니다. 온맵 PDF가 아닌 듯 합니다.")

            if self.forceStop:
                raise StoppedByUserException()

            # create layer group
            root = QgsProject.instance().layerTreeRoot()
            filename, extension = os.path.splitext(os.path.basename(self.pdfPath))

            groupTitle = self.parent.getNewGroupTitle(u"[PDF]"+filename)

            layerTreeGroup = root.addGroup(groupTitle)

            self.importPdfVector(layerTreeGroup)
            if self.forceStop:
                raise StoppedByUserException()

            self.importPdfRaster(layerTreeGroup)
            if self.forceStop:
                raise StoppedByUserException()

            canvas = self.iface.mapCanvas()
            canvas.setExtent(canvas.mapSettings().fullExtent())

            self.info(u"온맵 불러오기 성공!")
            self.progressMain.setValue(0)
            self.progressSub.setValue(0)

            self.appendGroupBox(layerTreeGroup, "onmap")

            self.isOnProcessing = False

            self.progText(u"온맵 불러오기 성공!")

        except StoppedByUserException:
            pass
        except Exception as e:
            self.error(unicode(e))
        finally:
            QgsApplication.restoreOverrideCursor()
            self.isOnProcessing = False

    # 실제 동작중 이벤트가 오지 않는 문제가 있어 개발 중지
    def stopProcessing(self):
        if not self.isOnProcessing:
            return False

        rc = QMessageBox.question(self.parent, u"작업 강제 중지",
                                  u"현재 작업을 강제로 중지하시겠습니까?\n\n"
                                  u"작업 중지는 오류의 원인이 될 수도 있습니다.",
                                  QMessageBox.Yes | QMessageBox.No)
        if rc != QMessageBox.Yes:
            return False

        self.forceStop = True

        return True

    def getPdfInformation(self):
        self.progressMain.setMinimum(0)
        self.progressMain.setMaximum(0)
        self.progText(u"선택한 온맵 파일 분석중...")
        self.info(u"PDF 파일에서 정보추출 시작...")
        force_gui_update()

        mapNo = findMapNo(os.path.basename(self.pdfPath))
        if mapNo is None:
            return

        boxLL, boxLR, boxTL, boxTR, scale = None, None, None, None, 5000
        try:
            boxLL, boxLR, boxTL, boxTR, scale = mapNoToMapBox(mapNo)
        except NotImplementedError as e:
            self.error(repr(e))
        except:
            self.error(u"해석할 수 없는 도엽명이어서 중단됩니다.")
            return

        if scale != 5000:
            rc = QMessageBox.question(self.parent, u"계속 진행 확인",
                                      u"선택하신 온맵은 변환시간이 매우 오래 걸릴 수 있습니다.\n"
                                      u"때문에 마치 프로그램이 죽은 것처럼 보일 수 있습니다.\n\n"
                                      u"그래도 계속 변환하시겠습니까?",
                                      QMessageBox.Yes | QMessageBox.No)

            if rc != QMessageBox.Yes:
                return

        try:
            # opening the PDF
            # pdf = srcDriver.Open(self.pdfPath, 0)
            trd = PdfOpenThread(self.pdfPath)
            trd.start()

            while threading.activeCount() > 1:
                force_gui_update()
                time.sleep(0.1)

            pdf = trd.outPdf

        except Exception, e:
            self.error(unicode(e))
            return

        # 좌표계 판단
        if boxLL[0] < 126.0:
            crsId = 5185
        elif boxLL[0] < 128.0:
            crsId = 5186
        elif boxLL[0] < 130.0:
            crsId = 5187
        else:
            crsId = 5188

        fromCrs = osr.SpatialReference()
        fromCrs.ImportFromEPSG(4326)
        toCrs = osr.SpatialReference()
        toCrs.ImportFromEPSG(crsId)
        p = osr.CoordinateTransformation(fromCrs, toCrs)
        tmBoxLL = p.TransformPoint(boxLL[0], boxLL[1])
        tmBoxLR = p.TransformPoint(boxLR[0], boxLR[1])
        tmBoxTL = p.TransformPoint(boxTL[0], boxTL[1])
        tmBoxTR = p.TransformPoint(boxTR[0], boxTR[1])

        # use OGR specific exceptions
        # list to store layers'names
        layerInfoList = list()

        # parsing layers by index
        # 레이어 ID, 레이어 이름, 객체 수, 지오매트리 유형
        mapBoxLayerId = None
        mapClipLayerId = None
        mapBoxGeometry = None
        mapClipGeometry = None
        boxLL, boxLR, boxTL, boxTR = None, None, None, None
        imgLL, imgLR, imgTL, imgTR = None, None, None, None
        for iLayer in range(pdf.GetLayerCount()):
            pdfLayer = pdf.GetLayerByIndex(iLayer)
            name = unicode(pdfLayer.GetName().decode('utf-8'))

            if name.find(MAP_BOX_LAYER) >= 0:
                mapBoxLayerId = iLayer
            if name.find(MAP_CLIP_LAYER) >= 0:
                mapClipLayerId = iLayer
            totalFeatureCnt = pdfLayer.GetFeatureCount()
            pointCount = 0
            lineCount = 0
            polygonCount = 0

            for feature in pdfLayer:
                force_gui_update()
                geometry = feature.GetGeometryRef()
                geomType = geometry.GetGeometryType()
                if geomType == ogr.wkbPoint or geomType == ogr.wkbMultiPoint:
                    pointCount += 1
                elif geomType == ogr.wkbLineString or geomType == ogr.wkbMultiLineString:
                    lineCount += 1
                elif geomType == ogr.wkbPolygon or geomType == ogr.wkbMultiPolygon:
                    polygonCount += 1
                else:
                    self.error(u"[Unknown Type] " + ogr.GeometryTypeToName(geomType))

                # 도곽을 찾아 정보 추출
                if mapBoxLayerId and mapBoxGeometry is None:
                    if geometry.GetPointCount() > 0 \
                            and geometry.GetX(0) == geometry.GetX(geometry.GetPointCount() - 1) \
                            and geometry.GetY(0) == geometry.GetY(geometry.GetPointCount() - 1):
                        mapBoxGeometry = geometry
                        mapBoxPoints = geometry.GetPoints()
                        boxLL, boxLR, boxTL, boxTR = findConner(mapBoxPoints)

                # 영상영역 찾아 정보 추출
                if mapClipLayerId and mapClipGeometry is None:
                    if geometry.GetPointCount() > 0 \
                            and geometry.GetX(0) == geometry.GetX(geometry.GetPointCount() - 1) \
                            and geometry.GetY(0) == geometry.GetY(geometry.GetPointCount() - 1):
                        mapClipGeometry = geometry
                        mapClipPoints = geometry.GetPoints()
                        imgLL, imgLR, imgTL, imgTR = findConner(mapClipPoints)

            pdfLayer.ResetReading()

            if mapBoxLayerId:
                mapBoxLayerId = None

            layerInfoList.append({'id': iLayer, 'name': name, "totalCount": totalFeatureCnt,
                                  "pointCount": pointCount, "lineCount": lineCount, "polygonCount": polygonCount})

        self.debug(unicode((boxLL, boxLR, boxTL, boxTR)))

        affineTransform, _ = calcAffineTransform(boxLL, boxLR, boxTL, boxTR, tmBoxLL, tmBoxLR, tmBoxTL, tmBoxTR)

        srcList = [[imgLL[0], imgLL[1]], [imgLR[0], imgLR[1]], [imgTL[0], imgTL[1]], [imgTR[0], imgTR[1]]]
        srcNpArray = np.array(srcList, dtype=np.float32)
        tgtNpArray = affineTransform(srcNpArray)

        self.info(u"정보추출 완료.")
        self.progText(u"작업 대기중")
        self.progressMain.setMinimum(0)
        self.progressMain.setMaximum(100)

        # Return Values
        self.pdf = pdf
        self.layerInfoList = layerInfoList
        self.affineTransform = affineTransform
        self.crsId = crsId
        self.mapNo = mapNo
        self.bbox = (tmBoxLL, tmBoxLR, tmBoxTL, tmBoxTR)
        self.imgBox = (tgtNpArray[0], tgtNpArray[1], tgtNpArray[2], tgtNpArray[3])

        return True

    def importPdfVector(self, layerTreeGroup):
        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.info(u"PDF에서 벡터정보 추출 시작...")

            # 좌표계 정보 생성
            crs = osr.SpatialReference()
            crs.ImportFromEPSG(self.crsId)
            crsWkt = crs.ExportToWkt()

            subGroup = None
            subGroupName = None

            # Create QGIS Layer
            totalCount = len(self.layerInfoList)
            crrIndex = 0
            self.progressMain.setMinimum(0)
            self.progressMain.setMaximum(totalCount + 3)
            self.progressMain.setValue(0)

            for layerInfo in self.layerInfoList:
                crrIndex += 1
                self.progressMain.setValue(self.progressMain.value() + 1)

                vPointLayer = None
                vLineLayer = None
                vPolygonLayer = None

                # 지도정보_ 로 시작하는 레이만 처리
                layerName = layerInfo["name"]
                if not layerName.startswith(LAYER_FILTER):
                    continue

                layerName = layerName.replace(LAYER_FILTER, "")
                self.progText(u"{} 레이어 처리중({}/{})...".format(layerName, crrIndex, totalCount))

                # 서브 그룹 만들기
                layerGroupSpilt = layerName.split(u"_")
                if subGroupName != layerGroupSpilt[0]:
                    subGroupName = layerGroupSpilt[0]
                    if subGroup:
                        subGroup.setExpanded(False)
                    subGroup = layerTreeGroup.addGroup(subGroupName)

                self.progText(u"{} 레이어 처리중({}/{})...".format(layerName, crrIndex, totalCount))

                # 선택된 레이어만 가져오기
                self.debug(u"Processing Layer: {}".format(layerName))

                pdfLayer = self.pdf.GetLayerByIndex(layerInfo["id"])
                totalFeature = pdfLayer.GetFeatureCount()
                crrFeatureIndex = 0
                self.progressSub.setMinimum(0)
                self.progressSub.setMaximum(100)
                oldPct = -1
                for ogrFeature in pdfLayer:
                    crrFeatureIndex += 1
                    crrPct = int(crrFeatureIndex * 100 / totalFeature)
                    if crrPct != oldPct:
                        oldPct = crrPct
                        self.progressSub.setValue(crrPct)
                        self.progText(u"객체 추출중 ({}/{})...".format(crrFeatureIndex, totalFeature))
                    force_gui_update()

                    if self.forceStop:
                        raise StoppedByUserException()

                    geometry = ogrFeature.GetGeometryRef()
                    geomType = geometry.GetGeometryType()

                    if geomType == ogr.wkbPoint or geomType == ogr.wkbMultiPoint:
                        if not vPointLayer:
                            outLayerName = u"{}_Point".format(layerName)
                            vPointLayer = QgsVectorLayer("Point?crs={}".format(crsWkt), outLayerName, "memory")
                            vPointLayer.dataProvider().addAttributes([QgsField("GID", QVariant.Int)])
                            vPointLayer.updateFields()
                            QgsMapLayerRegistry.instance().addMapLayer(vPointLayer, False)
                            subGroup.insertChildNode(1, QgsLayerTreeLayer(vPointLayer))
                            self.debug(u"layerName:" + outLayerName)
                            self.debug(u"outLayerName:" + outLayerName)
                        vLayer = vPointLayer
                    elif geomType == ogr.wkbLineString or geomType == ogr.wkbMultiLineString:
                        if not vLineLayer:
                            outLayerName = u"{}_Line".format(layerName)
                            vLineLayer = QgsVectorLayer("LineString?crs={}".format(crsWkt), outLayerName, "memory")
                            vLineLayer.dataProvider().addAttributes([QgsField("GID", QVariant.Int)])
                            vLineLayer.updateFields()
                            QgsMapLayerRegistry.instance().addMapLayer(vLineLayer, False)
                            subGroup.insertChildNode(1, QgsLayerTreeLayer(vLineLayer))
                            self.debug(u"layerName:" + layerName)
                            self.debug(u"outLayerName:" + outLayerName)
                        vLayer = vLineLayer
                    elif geomType == ogr.wkbPolygon or geomType == ogr.wkbMultiPolygon:
                        if not vPolygonLayer:
                            outLayerName = u"{}_Polygon".format(layerName)
                            vPolygonLayer = QgsVectorLayer("Polygon?crs={}".format(crsWkt), outLayerName, "memory")
                            vPolygonLayer.dataProvider().addAttributes([QgsField("GID", QVariant.Int)])
                            vPolygonLayer.updateFields()
                            QgsMapLayerRegistry.instance().addMapLayer(vPolygonLayer, False)
                            subGroup.insertChildNode(1, QgsLayerTreeLayer(vPolygonLayer))
                            self.debug(u"layerName:" + layerName)
                            self.debug(u"outLayerName:" + outLayerName)
                        vLayer = vPolygonLayer
                    else:
                        self.error(u"[ERROR] Unknown geometry type: " + geometry.GetGeometryName())
                        continue

                    geomWkb = geometry.ExportToWkb()
                    fid = ogrFeature.GetFID()

                    qgisFeature = QgsFeature()
                    qgisGeom = QgsGeometry()
                    qgisGeom.fromWkb(geomWkb)
                    self._TransformGeom(qgisGeom)
                    qgisFeature.setGeometry(qgisGeom)

                    qgisFeature.setAttributes([fid])
                    vLayer.dataProvider().addFeatures([qgisFeature])
                vLayer.triggerRepaint()

            if subGroup is not None: subGroup.setExpanded(False)

            self.info(u"벡터 가져오기 완료")
        except StoppedByUserException:
            self.error(u"사용자에 의해 중지됨")
            QgsApplication.restoreOverrideCursor()
            return False
        except Exception as e:
            self.error(e)
            self.error(u"벡터 가져오기 실패")
            QgsApplication.restoreOverrideCursor()
            return False
        finally:
            self.iface.mapCanvas().refresh()
            QgsApplication.restoreOverrideCursor()
            force_gui_update()

        return True

    def _TransformGeom(self, geometry):
        i = 0
        vertex = geometry.vertexAt(i)
        srcList = []
        while (vertex != QgsPoint(0, 0)):
            srcList.append([vertex.x(), vertex.y()])
            i += 1
            vertex = geometry.vertexAt(i)

        srcNpArray = np.array(srcList)

        # transform all vertex
        tgtNpList = self.affineTransform(srcNpArray)

        # move vertex
        for i in range(0, len(srcNpArray)):
            geometry.moveVertex(tgtNpList[i, 0], tgtNpList[i, 1], i)

    def importPdfRaster(self, layerTreeGroup):
        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.info(u"영상 정보 추출시작")

            fh = open(self.pdfPath, "rb")
            pdfObj = PyPDF2.PdfFileReader(fh)

            pageObj = pdfObj.getPage(0)

            try:
                xObject = pageObj['/Resources']['/XObject'].getObject()
            except KeyError:
                raise Exception(u"영상 레이어가 없어 가져올 수 없습니다.")

            self.progressMain.setValue(self.progressMain.value() + 1)
            self.info(u"영상 조각 추출중...")
            if self.forceStop:
                raise StoppedByUserException()

            images = {}
            totalCount = len(xObject)
            self.progressSub.setMinimum(0)
            self.progressSub.setMaximum(totalCount)
            crrIndex = 0

            for obj in xObject:
                crrIndex += 1
                self.progressSub.setValue(crrIndex)
                self.progText(u"영상 조각 처리중({}/{})...".format(crrIndex, totalCount))
                force_gui_update()
                if self.forceStop:
                    raise StoppedByUserException()

                if xObject[obj]['/Subtype'] == '/Image':
                    name = obj[1:]
                    m = NUM_FILTER.search(name)
                    try:
                        id = int(m.group(1))
                    except:
                        continue
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])

                    # 작은 이미지 무시
                    if size[0] < SKIP_IMAGE_WIDTH:
                        continue

                    colorSpace = xObject[obj]['/ColorSpace']
                    if colorSpace == '/DeviceRGB':
                        mode = "RGB"
                    elif colorSpace == '/DeviceCMYK':
                        mode = "CMYK"
                    elif colorSpace == '/DeviceGray':
                        mode = "L"
                    elif colorSpace[0] == "/Indexed":
                        mode = "P"
                        colorSpace, base, hival, lookup = [v.getObject() for v in colorSpace]
                        palette = lookup.getData()
                    elif colorSpace[0] == "/ICCBased":
                        mode = "P"
                        lookup = colorSpace[1].getObject()
                        palette = lookup.getData()
                    else:
                        continue

                    try:
                        stream = xObject[obj]
                        data = stream._data
                        filters = stream.get("/Filter", ())
                        if type(filters) is not PyPDF2.generic.ArrayObject:
                            filters = [filters]
                        leftFilters = copy.deepcopy(filters)

                        if data:
                            for filterType in filters:
                                if filterType == "/FlateDecode" or filterType == "/Fl":
                                    data = FlateDecode.decode(data, stream.get("/DecodeParms"))
                                    leftFilters.remove(filterType)
                                elif filterType == "/ASCIIHexDecode" or filterType == "/AHx":
                                    data = ASCIIHexDecode.decode(data)
                                    leftFilters.remove(filterType)
                                elif filterType == "/LZWDecode" or filterType == "/LZW":
                                    data = LZWDecode.decode(data, stream.get("/DecodeParms"))
                                    leftFilters.remove(filterType)
                                elif filterType == "/ASCII85Decode" or filterType == "/A85":
                                    data = ASCII85Decode.decode(data)
                                    leftFilters.remove(filterType)
                                elif filterType == "/Crypt":
                                    decodeParams = stream.get("/DecodeParams", {})
                                    if "/Name" not in decodeParams and "/Type" not in decodeParams:
                                        pass
                                    else:
                                        raise NotImplementedError("/Crypt filter with /Name or /Type not supported yet")
                                    leftFilters.remove(filterType)
                                elif filterType == ():
                                    leftFilters.remove(filterType)

                            # case of Flat image
                            if len(leftFilters) == 0:
                                img = Image.frombytes(mode, size, data)
                                if mode == "P":
                                    img.putpalette(palette)
                                if mode == "CMYK":
                                    img = img.convert('RGB')
                                images[id] = img

                            # case of JPEG
                            elif len(leftFilters) == 1 and leftFilters[0] == '/DCTDecode':
                                jpgData = BytesIO(data)
                                img = Image.open(jpgData)
                                if mode == "CMYK":
                                    imgData = np.frombuffer(img.tobytes(), dtype='B')
                                    invData = np.full(imgData.shape, 255, dtype='B')
                                    invData -= imgData
                                    img = Image.frombytes(img.mode, img.size, invData.tobytes())
                                images[id] = img
                    except:
                        pass

            fh.close()
            del pdfObj

            # 이미지를 ID 순으로 연결
            self.info(u"영상 병합 시작")
            self.progressMain.setValue(self.progressMain.value() + 1)
            self.info(u"영상 병합중...")
            if self.forceStop:
                raise StoppedByUserException()

            keys = images.keys()
            keys.sort()

            totalCount = len(keys)
            self.progressSub.setMinimum(0)
            self.progressSub.setMaximum(totalCount)

            mergedWidth = None
            mergedHeight = None
            mergedMode = None
            crrIndex = 0
            for key in keys:
                crrIndex += 1
                self.progressSub.setValue(crrIndex)
                self.progText(u"영상 조각 처리중({}/{})...".format(crrIndex, totalCount))
                force_gui_update()
                if self.forceStop:
                    raise StoppedByUserException()

                image = images[key]
                width, height = image.size

                if mergedWidth is None:
                    mergedWidth, mergedHeight = width, height
                    mergedMode = image.mode
                    continue

                if width != mergedWidth:
                    break

                mergedHeight += height

            mergedImage = Image.new("RGB", (mergedWidth, mergedHeight))
            crrY = 0
            for key in keys:
                image = images[key].transpose(Image.FLIP_TOP_BOTTOM)
                mergedImage.paste(image, (0, crrY))
                crrY += image.height
                del image
                del images[key]

            images.clear()

            self.info(u"병합된 영상을 저장")
            self.progressMain.setValue(self.progressMain.value() + 1)
            if self.forceStop:
                raise StoppedByUserException()

            self.progressSub.setMinimum(0)
            self.progressSub.setMaximum(5)
            self.progressSub.setValue(0)
            self.progText(u"정사영상 저장중...")
            if self.forceStop:
                raise StoppedByUserException()

            # TIFF 파일로 이미지 저장
            root, ext = os.path.splitext(self.pdfPath)
            outputFilePath = root + ".tif"
            _, tempFilePath = tempfile.mkstemp(".tif")
            mergedImage.save(tempFilePath)
            del mergedImage

            # 좌표계 정보 생성
            self.progressSub.setValue(1)
            self.progText(u"좌표계 정보 생성중...")
            crs = osr.SpatialReference()
            crs.ImportFromEPSG(self.crsId)
            crs_wkt = crs.ExportToWkt()

            # 매트릭스 계산
            srcList = [
                [0, mergedHeight],
                [mergedWidth, mergedHeight],
                [0, 0],
                [mergedWidth, 0]
            ]
            srcNpArray = np.array(srcList, dtype=np.float32)

            _, matrix = calcAffineTransform(
                srcNpArray[0], srcNpArray[1], srcNpArray[2], srcNpArray[3],
                self.imgBox[0], self.imgBox[1], self.imgBox[2], self.imgBox[3]
            )

            # GeoTIFF 만들기
            self.progressSub.setValue(2)
            self.progText(u"GeoTIFF로 저장중...")
            outImage = gdal.Open(tempFilePath)
            driver = gdal.GetDriverByName('GTiff')

            _, tempGeoTiffFilePath = tempfile.mkstemp(".tif")
            gtiff = driver.CreateCopy(tempGeoTiffFilePath, outImage)
            gtiff.SetProjection(crs_wkt)

            # P1(C): x_origin,
            # P2(A): cos(rotation) * x_pixel_size,
            # P3(D): -sin(rotation) * x_pixel_size,
            # P4(F): y_origin,
            # P5(B): sin(rotation) * y_pixel_size,
            # P6(E): cos(rotation) * y_pixel_size)
            gtiff.SetGeoTransform((matrix[0][2], matrix[0][0], matrix[1][0], matrix[1][2], matrix[0][1], matrix[1][1]))

            # gtiff.close()
            del gtiff

            # Temp 파일을 정식 이름으로 복사하여 오픈 시도
            geoTiffPath = outputFilePath
            try:
                copyfile(tempGeoTiffFilePath, outputFilePath)
            except:
                geoTiffPath = tempGeoTiffFilePath

            try:
                os.remove(tempGeoTiffFilePath)
            except:
                pass

            self.info(u"정사영상 추출 완료")

            rasterLayer = QgsRasterLayer(geoTiffPath, u"정사영상")
            QgsMapLayerRegistry.instance().addMapLayer(rasterLayer, False)
            layerTreeGroup.addLayer(rasterLayer)

            force_gui_update()

        except StoppedByUserException:
            QgsApplication.restoreOverrideCursor()
            self.error(u"사용자에 의해 중지됨")
            return False
        except Exception as e:
            self.error(e)
            QgsApplication.restoreOverrideCursor()
            self.error(u"영상 가져오기 실패")
            return False
        finally:
            QgsApplication.restoreOverrideCursor()
            self.iface.mapCanvas().refresh()
            self.progressMain.setValue(0)
            self.progressSub.setValue(0)
            force_gui_update()

        self.info(u"영상 가져오기 완료")
        return True
