# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ngii_data_utils_dockwidget_base.ui'
#
# Created: Sun May 13 13:24:05 2018
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
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 213, 266))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox_1 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_1.sizePolicy().hasHeightForWidth())
        self.groupBox_1.setSizePolicy(sizePolicy)
        self.groupBox_1.setMaximumSize(QtCore.QSize(16777215, 130))
        self.groupBox_1.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.groupBox_1.setObjectName(_fromUtf8("groupBox_1"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horLayout1_1 = QtGui.QHBoxLayout()
        self.horLayout1_1.setObjectName(_fromUtf8("horLayout1_1"))
        self.btnToSpWin_1 = QtGui.QPushButton(self.groupBox_1)
        self.btnToSpWin_1.setObjectName(_fromUtf8("btnToSpWin_1"))
        self.horLayout1_1.addWidget(self.btnToSpWin_1)
        self.btnRemove_1 = QtGui.QPushButton(self.groupBox_1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRemove_1.sizePolicy().hasHeightForWidth())
        self.btnRemove_1.setSizePolicy(sizePolicy)
        self.btnRemove_1.setMinimumSize(QtCore.QSize(30, 0))
        self.btnRemove_1.setMaximumSize(QtCore.QSize(30, 16777215))
        self.btnRemove_1.setObjectName(_fromUtf8("btnRemove_1"))
        self.horLayout1_1.addWidget(self.btnRemove_1)
        self.gridLayout.addLayout(self.horLayout1_1, 0, 0, 1, 1)
        self.horLayout3_1 = QtGui.QHBoxLayout()
        self.horLayout3_1.setObjectName(_fromUtf8("horLayout3_1"))
        self.lblColor_1 = QtGui.QLabel(self.groupBox_1)
        self.lblColor_1.setObjectName(_fromUtf8("lblColor_1"))
        self.horLayout3_1.addWidget(self.lblColor_1)
        self.btnSelColor_1 = QtGui.QPushButton(self.groupBox_1)
        self.btnSelColor_1.setObjectName(_fromUtf8("btnSelColor_1"))
        self.horLayout3_1.addWidget(self.btnSelColor_1)
        self.btnResetColor_1 = QtGui.QPushButton(self.groupBox_1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnResetColor_1.sizePolicy().hasHeightForWidth())
        self.btnResetColor_1.setSizePolicy(sizePolicy)
        self.btnResetColor_1.setMinimumSize(QtCore.QSize(50, 0))
        self.btnResetColor_1.setMaximumSize(QtCore.QSize(50, 16777215))
        self.btnResetColor_1.setObjectName(_fromUtf8("btnResetColor_1"))
        self.horLayout3_1.addWidget(self.btnResetColor_1)
        self.gridLayout.addLayout(self.horLayout3_1, 2, 0, 1, 1)
        self.horLayout2_1 = QtGui.QHBoxLayout()
        self.horLayout2_1.setObjectName(_fromUtf8("horLayout2_1"))
        self.lblTrans_1 = QtGui.QLabel(self.groupBox_1)
        self.lblTrans_1.setObjectName(_fromUtf8("lblTrans_1"))
        self.horLayout2_1.addWidget(self.lblTrans_1)
        self.sldTrans_1 = phonon.Phonon.SeekSlider(self.groupBox_1)
        self.sldTrans_1.setObjectName(_fromUtf8("sldTrans_1"))
        self.horLayout2_1.addWidget(self.sldTrans_1)
        self.gridLayout.addLayout(self.horLayout2_1, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_1, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 130))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.horLayout1_2 = QtGui.QHBoxLayout()
        self.horLayout1_2.setObjectName(_fromUtf8("horLayout1_2"))
        self.btnToSpWin_2 = QtGui.QPushButton(self.groupBox)
        self.btnToSpWin_2.setObjectName(_fromUtf8("btnToSpWin_2"))
        self.horLayout1_2.addWidget(self.btnToSpWin_2)
        self.btnRemove_2 = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRemove_2.sizePolicy().hasHeightForWidth())
        self.btnRemove_2.setSizePolicy(sizePolicy)
        self.btnRemove_2.setMinimumSize(QtCore.QSize(30, 0))
        self.btnRemove_2.setMaximumSize(QtCore.QSize(30, 16777215))
        self.btnRemove_2.setObjectName(_fromUtf8("btnRemove_2"))
        self.horLayout1_2.addWidget(self.btnRemove_2)
        self.gridLayout_4.addLayout(self.horLayout1_2, 0, 0, 1, 1)
        self.horLayout2_2 = QtGui.QHBoxLayout()
        self.horLayout2_2.setObjectName(_fromUtf8("horLayout2_2"))
        self.lblTrans_2 = QtGui.QLabel(self.groupBox)
        self.lblTrans_2.setObjectName(_fromUtf8("lblTrans_2"))
        self.horLayout2_2.addWidget(self.lblTrans_2)
        self.sldTrans_2 = phonon.Phonon.SeekSlider(self.groupBox)
        self.sldTrans_2.setObjectName(_fromUtf8("sldTrans_2"))
        self.horLayout2_2.addWidget(self.sldTrans_2)
        self.gridLayout_4.addLayout(self.horLayout2_2, 1, 0, 1, 1)
        self.horLayout3_2 = QtGui.QHBoxLayout()
        self.horLayout3_2.setObjectName(_fromUtf8("horLayout3_2"))
        self.lblColor_2 = QtGui.QLabel(self.groupBox)
        self.lblColor_2.setObjectName(_fromUtf8("lblColor_2"))
        self.horLayout3_2.addWidget(self.lblColor_2)
        self.btnSelColor_2 = QtGui.QPushButton(self.groupBox)
        self.btnSelColor_2.setEnabled(False)
        self.btnSelColor_2.setObjectName(_fromUtf8("btnSelColor_2"))
        self.horLayout3_2.addWidget(self.btnSelColor_2)
        self.btnResetColor_2 = QtGui.QPushButton(self.groupBox)
        self.btnResetColor_2.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnResetColor_2.sizePolicy().hasHeightForWidth())
        self.btnResetColor_2.setSizePolicy(sizePolicy)
        self.btnResetColor_2.setMinimumSize(QtCore.QSize(50, 0))
        self.btnResetColor_2.setMaximumSize(QtCore.QSize(50, 16777215))
        self.btnResetColor_2.setObjectName(_fromUtf8("btnResetColor_2"))
        self.horLayout3_2.addWidget(self.btnResetColor_2)
        self.gridLayout_4.addLayout(self.horLayout3_2, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 1, 1)
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
        NgiiDataUtilsDockWidgetBase.setWindowTitle(_translate("NgiiDataUtilsDockWidgetBase", "국토지리정보원 공간정보 중첩 검사", None))
        self.btnLoadInternetBaseMap.setText(_translate("NgiiDataUtilsDockWidgetBase", "인터넷지도해당 국토기본정보 불러오기", None))
        self.btnLoadImage.setText(_translate("NgiiDataUtilsDockWidgetBase", "영상(GeoTIFF/IMG) 불러오기", None))
        self.btnLoadOnmapBaseMap.setText(_translate("NgiiDataUtilsDockWidgetBase", "온맵해당 국토기본정보 불러오기", None))
        self.btnLoadBaseMap.setText(_translate("NgiiDataUtilsDockWidgetBase", "최신 국토기본정보(전레이어) 불러오기", None))
        self.btnLoadVector.setText(_translate("NgiiDataUtilsDockWidgetBase", "온맵/지형도/공공측량성과 불러오기", None))
        self.btnLoadTms.setText(_translate("NgiiDataUtilsDockWidgetBase", "국가 인터넷지도 불러오기", None))
        self.btnAutoDetect.setText(_translate("NgiiDataUtilsDockWidgetBase", "변화내용 자동탐지", None))
        self.btnReportError.setText(_translate("NgiiDataUtilsDockWidgetBase", "오류사항 기록", None))
        self.groupBox_1.setTitle(_translate("NgiiDataUtilsDockWidgetBase", "[온맵](B090)온맵_37612068.pdf", None))
        self.btnToSpWin_1.setText(_translate("NgiiDataUtilsDockWidgetBase", "분할창으로 띄우기", None))
        self.btnRemove_1.setText(_translate("NgiiDataUtilsDockWidgetBase", "제거", None))
        self.lblColor_1.setText(_translate("NgiiDataUtilsDockWidgetBase", "색  상:", None))
        self.btnSelColor_1.setText(_translate("NgiiDataUtilsDockWidgetBase", "COLOR", None))
        self.btnResetColor_1.setText(_translate("NgiiDataUtilsDockWidgetBase", "초기화", None))
        self.lblTrans_1.setText(_translate("NgiiDataUtilsDockWidgetBase", "투명도:", None))
        self.groupBox.setTitle(_translate("NgiiDataUtilsDockWidgetBase", "[인터넷지도]", None))
        self.btnToSpWin_2.setText(_translate("NgiiDataUtilsDockWidgetBase", "분할창으로 띄우기", None))
        self.btnRemove_2.setText(_translate("NgiiDataUtilsDockWidgetBase", "제거", None))
        self.lblTrans_2.setText(_translate("NgiiDataUtilsDockWidgetBase", "투명도:", None))
        self.lblColor_2.setText(_translate("NgiiDataUtilsDockWidgetBase", "색  상:", None))
        self.btnSelColor_2.setText(_translate("NgiiDataUtilsDockWidgetBase", "COLOR", None))
        self.btnResetColor_2.setText(_translate("NgiiDataUtilsDockWidgetBase", "초기화", None))
        self.lblStatus.setText(_translate("NgiiDataUtilsDockWidgetBase", "진행상황 표시", None))

from PyQt4 import phonon
