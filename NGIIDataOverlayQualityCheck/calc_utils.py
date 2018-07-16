# -*- coding: utf-8 -*-
from PyQt4.QtCore import QEventLoop
from qgis.core import *
import numpy as np
import re

#########################
# UI FUNCTION
#########################
def force_gui_update():
    QgsApplication.processEvents(QEventLoop.ExcludeUserInputEvents)


#########################
# ANALYSIS FUNCTION
#########################
# REFER: https://stackoverflow.com/questions/20546182/how-to-perform-coordinates-affine-transformation-using-python-part-2
def calcAffineTransform(srcP1, srcP2, srcP3, srcP4, tgtP1, tgtP2, tgtP3, tgtP4):
    primary = np.array([[srcP1[0], srcP1[1]],
                        [srcP2[0], srcP2[1]],
                        [srcP3[0], srcP3[1]],
                        [srcP4[0], srcP4[1]]])

    secondary = np.array([[tgtP1[0], tgtP1[1]],
                          [tgtP2[0], tgtP2[1]],
                          [tgtP3[0], tgtP3[1]],
                          [tgtP4[0], tgtP4[1]]])

    # Pad the data with ones, so that our transformation can do translations too
    n = primary.shape[0]
    pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
    unpad = lambda x: x[:, :-1]
    X = pad(primary)
    Y = pad(secondary)

    # Solve the least squares problem X * A = Y
    # to find our transformation matrix A
    A, res, rank, s = np.linalg.lstsq(X, Y)

    affineTransform = lambda x: unpad(np.dot(pad(x), A))
    return affineTransform, A.T


def findConner(points):
    pntLL = pntLR = pntTL = pntTR = None

    xList = [item[0] for item in points]
    yList = [item[1] for item in points]

    xMin = min(xList)
    yMin = min(yList)
    xMax = max(xList)
    yMax = max(yList)

    distLL = None
    distLR = None
    distTL = None
    distTR = None

    for point in points:
        tmpDistLL = (point[0] - xMin) ** 2 + (point[1] - yMax) ** 2
        tmpDistLR = (point[0] - xMax) ** 2 + (point[1] - yMax) ** 2
        tmpDistTL = (point[0] - xMin) ** 2 + (point[1] - yMin) ** 2
        tmpDistTR = (point[0] - xMax) ** 2 + (point[1] - yMin) ** 2

        if distLL is None or distLL > tmpDistLL:
            distLL = tmpDistLL
            pntLL = point
        if distLR is None or distLR > tmpDistLR:
            distLR = tmpDistLR
            pntLR = point
        if distTL is None or distTL > tmpDistTL:
            distTL = tmpDistTL
            pntTL = point
        if distTR is None or distTR > tmpDistTR:
            distTR = tmpDistTR
            pntTR = point

    return pntLL, pntLR, pntTL, pntTR

# (B010)수치지도_36710002_2018_00000238632981.dxf
# (B090)온맵_36710002.pdf
mapNo_re = re.compile(ur"(?i)([ㄱ-ㅣ가-힣]+)\_(\d+)\_*(.*)")
# (B060)정사영상_2017_36706091s.tif
mapNoImg_re = re.compile(ur"(?i)([ㄱ-ㅣ가-힣]+)\_(\d+)\_(\d+)(s*)")

def findMapNo(fileBase, flagImage=False):
    if not flagImage:
        res = mapNo_re.search(fileBase)
        if res:
            return res.group(2)
        else:
            return None
    else:
        res = mapNoImg_re.search(fileBase)
        if res:
            return res.group(3)
        else:
            return None



def mapNoToMapBox(mapNo):
    if not isinstance(mapNo, basestring):
        return None

    if mapNo[:2].upper() == "NJ" or mapNo[:2].upper() == "NI":
        scale = 250000
    elif len(mapNo) == 5:
        scale = 50000
    elif len(mapNo) == 6:
        scale = 25000
    elif len(mapNo) == 8:
        scale = 5000
    else:
        return None

    if scale == 250000:
        raise NotImplementedError(u"죄송합니다.25만 도엽은 지원되지 않습니다.")
        return None

        try:
            keyLat = mapNo[:2]
            keyLon = mapNo[2:5]
            subIndex = int(mapNo[5:])

            if keyLat == "NJ":
                maxLat = 39.0
            elif keyLat == "NI":
                maxLat = 36.0
            else:
                return None

            if keyLon == "52-":
                minLon = 126.0
            elif keyLon == "51-":
                minLon = 120.0
            else:
                return None

            rowIndex = (subIndex - 1) / 3
            colIndex = (subIndex - 1) % 3

            minLon += colIndex * 2.0
            maxLat -= rowIndex * 1.0
            maxLon = minLon + 0.125
            minLat = maxLat - 0.125

        except:
            return None

    else:
        try:
            iLat = int(mapNo[0:2])
            iLon = int(mapNo[2:3]) + 120
            index50k = int(mapNo[3:5])
            rowIndex50k = (index50k - 1) / 4
            colIndex50k = (index50k - 1) % 4
            if scale == 25000:
                index25k = int(mapNo[5:])
                rowIndex25k = (index25k - 1) / 2
                colIndex25k = (index25k - 1) % 2
            elif scale == 5000:
                index5k = int(mapNo[5:])
                rowIndex5k = (index5k - 1) / 10
                colIndex5k = (index5k - 1) % 10
        except:
            return None

        minLon = float(iLon) + colIndex50k * 0.25
        maxLat = float(iLat) + (1 - rowIndex50k * 0.25)
        if scale == 50000:
            maxLon = minLon + 0.25
            minLat = maxLat - 0.25
        elif scale == 25000:
            minLon += colIndex25k * 0.125
            maxLat -= rowIndex25k * 0.125
            maxLon = minLon + 0.125
            minLat = maxLat - 0.125
        else:  # 5000
            minLon += colIndex5k * 0.025
            maxLat -= rowIndex5k * 0.025
            maxLon = minLon + 0.025
            minLat = maxLat - 0.025

    pntLL = (minLon, minLat)
    pntLR = (maxLon, minLat)
    pntTL = (minLon, maxLat)
    pntTR = (maxLon, maxLat)

    return pntLL, pntLR, pntTL, pntTR, scale


def mapNoToCrs(mapNo):
    pntLL, pntLR, pntTL, pntTR, scale = mapNoToMapBox(mapNo)

    # 좌표계 판단
    if pntLL[0] < 126.0:
        crsId = 5185
    elif pntLL[0] < 128.0:
        crsId = 5186
    elif pntLL[0] < 130.0:
        crsId = 5187
    else:
        crsId = 5188

    return crsId


#######
# 한글 인코딩 자동 판단
from dbfread import DBF

hangul_re = re.compile(ur"[ㄱ-ㅣ가-힣]")


def is_hangul(text):
    return hangul_re.search(text) is not None


def testEncoding(dbfFilePath, encoding, numTestRow=100):
    dbf = DBF(dbfFilePath, raw=True, load=True)
    fieldNames = dbf.field_names

    try:
        encoding = encoding

        i = 0
        flagHangulFound = False

        for record in dbf:
            for fieldName in fieldNames:
                val = record[fieldName].decode(encoding)
                if not flagHangulFound:
                    flagHangulFound = is_hangul(val)

            i += 1
            if i >= numTestRow and flagHangulFound:
                break
    except UnicodeDecodeError:
        return False

    return True


def findEncoding(dbfFilePath):
    encodingList = ['cp949', 'utf8', 'euc-kr']

    for encoding in encodingList:
        if testEncoding(dbfFilePath, encoding):
            return encoding

    return "Unknown"
