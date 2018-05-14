# -*- coding: utf-8 -*-

from osgeo import ogr, gdal, osr

gdal.UseExceptions()

#########################
# MAIN CLASS
#########################
class ImageLoader():
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
