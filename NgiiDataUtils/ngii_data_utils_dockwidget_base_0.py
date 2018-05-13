# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ngii_data_utils_dockwidget_base_empty.ui'
#
# Created: Sun May 13 15:32:32 2018
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_NgiiDataUtilsDockWidgetBase(object):
    def setupUi(self, NgiiDataUtilsDockWidgetBase):
        NgiiDataUtilsDockWidgetBase.setObjectName(_fromUtf8("NgiiDataUtilsDockWidgetBase"))
        NgiiDataUtilsDockWidgetBase.resize(238, 609)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout_3 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.prgSub = QtGui.QProgressBar(self.dockWidgetContents)
        self.prgSub.setMinimumSize(QtCore.QSize(0, 3))
        self.prgSub.setMaximumSize(QtCore.QSize(16777215, 3))
        self.prgSub.setProperty("value", 0)
        self.prgSub.setTextVisible(False)
        self.prgSub.setObjectName(_fromUtf8("prgSub"))
        self.gridLayout_3.addWidget(self.prgSub, 8, 0, 1, 1)
        self.btnLoadInternetBaseMap = QtGui.QPushButton(self.dockWidgetContents)
        self.btnLoadInternetBaseMap.setObjectName(_fromUtf8("btnLoadInternetBaseMap"))
        self.gridLayout_3.addWidget(self.btnLoadInternetBaseMap, 6, 0, 1, 1)
        self.btnLoadImage = QtGui.QPushButton(self.dockWidgetContents)
        self.btnLoadImage.setObjectName(_fromUtf8("btnLoadImage"))
        self.gridLayout_3.addWidget(self.btnLoadImage, 2, 0, 1, 1)
        self.btnLoadOnmapBaseMap = QtGui.QPushButton(self.dockWidgetContents)
        self.btnLoadOnmapBaseMap.setObjectName(_fromUtf8("btnLoadOnmapBaseMap"))
        self.gridLayout_3.addWidget(self.btnLoadOnmapBaseMap, 5, 0, 1, 1)
        self.btnLoadBaseMap = QtGui.QPushButton(self.dockWidgetContents)
        self.btnLoadBaseMap.setObjectName(_fromUtf8("btnLoadBaseMap"))
        self.gridLayout_3.addWidget(self.btnLoadBaseMap, 4, 0, 1, 1)
        self.btnLoadVector = QtGui.QPushButton(self.dockWidgetContents)
        self.btnLoadVector.setObjectName(_fromUtf8("btnLoadVector"))
        self.gridLayout_3.addWidget(self.btnLoadVector, 1, 0, 1, 1)
        self.btnLoadTms = QtGui.QPushButton(self.dockWidgetContents)
        self.btnLoadTms.setObjectName(_fromUtf8("btnLoadTms"))
        self.gridLayout_3.addWidget(self.btnLoadTms, 3, 0, 1, 1)
        self.prgMain = QtGui.QProgressBar(self.dockWidgetContents)
        self.prgMain.setMinimumSize(QtCore.QSize(0, 5))
        self.prgMain.setMaximumSize(QtCore.QSize(16777215, 5))
        self.prgMain.setProperty("value", 0)
        self.prgMain.setTextVisible(False)
        self.prgMain.setObjectName(_fromUtf8("prgMain"))
        self.gridLayout_3.addWidget(self.prgMain, 9, 0, 1, 1)
        self.btnAutoDetect = QtGui.QPushButton(self.dockWidgetContents)
        self.btnAutoDetect.setObjectName(_fromUtf8("btnAutoDetect"))
        self.gridLayout_3.addWidget(self.btnAutoDetect, 0, 0, 1, 1)
        self.btnReportError = QtGui.QPushButton(self.dockWidgetContents)
        self.btnReportError.setObjectName(_fromUtf8("btnReportError"))
        self.gridLayout_3.addWidget(self.btnReportError, 13, 0, 1, 1)
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 218, 193))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.scrollArea, 14, 0, 1, 1)
        self.editLog = QtGui.QPlainTextEdit(self.dockWidgetContents)
        self.editLog.setMinimumSize(QtCore.QSize(0, 50))
        self.editLog.setAutoFillBackground(False)
        self.editLog.setReadOnly(True)
        self.editLog.setBackgroundVisible(False)
        self.editLog.setObjectName(_fromUtf8("editLog"))
        self.gridLayout_3.addWidget(self.editLog, 12, 0, 1, 1)
        self.lblStatus = QtGui.QLabel(self.dockWidgetContents)
        self.lblStatus.setEnabled(True)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridLayout_3.addWidget(self.lblStatus, 11, 0, 1, 1)
        NgiiDataUtilsDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(NgiiDataUtilsDockWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(NgiiDataUtilsDockWidgetBase)

    def retranslateUi(self, NgiiDataUtilsDockWidgetBase):
        NgiiDataUtilsDockWidgetBase.setWindowTitle(_translate("NgiiDataUtilsDockWidgetBase", "국토지리정보원 데이터 중첩검사", None))
        self.btnLoadInternetBaseMap.setText(_translate("NgiiDataUtilsDockWidgetBase", "인터넷지도해당 국토기본정보 불러오기", None))
        self.btnLoadImage.setText(_translate("NgiiDataUtilsDockWidgetBase", "영상(GeoTIFF/IMG) 불러오기", None))
        self.btnLoadOnmapBaseMap.setText(_translate("NgiiDataUtilsDockWidgetBase", "온맵해당 국토기본정보 불러오기", None))
        self.btnLoadBaseMap.setText(_translate("NgiiDataUtilsDockWidgetBase", "최신 국토기본정보(전레이어) 불러오기", None))
        self.btnLoadVector.setText(_translate("NgiiDataUtilsDockWidgetBase", "온맵/지형도/공공측량성과 불러오기", None))
        self.btnLoadTms.setText(_translate("NgiiDataUtilsDockWidgetBase", "국가 인터넷지도 불러오기", None))
        self.btnAutoDetect.setText(_translate("NgiiDataUtilsDockWidgetBase", "변화내용 자동탐지", None))
        self.btnReportError.setText(_translate("NgiiDataUtilsDockWidgetBase", "오류사항 기록", None))
        self.lblStatus.setText(_translate("NgiiDataUtilsDockWidgetBase", "진행상황 표시", None))

