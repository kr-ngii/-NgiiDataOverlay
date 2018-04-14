# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NgiiDataUtils
                                 A QGIS plugin
 국토지리정보원 데이터 사용지원 툴
                              -------------------
        begin                : 2018-04-03
        git sha              : $Format:%H$
        copyright            : (C) 2018 by NGII
        email                : jangbi882@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QMenu, QToolBar, QMenuBar,  QToolButton

# Import the code for the DockWidget
from ngii_data_utils_dockwidget import NgiiDataUtilsDockWidget
import os.path


class NgiiDataUtils:
    """QGIS Plugin Implementation."""
    mainMenuTitle = u"NGII"
    mainMenu = None
    menuBar = None

    menuIcons = []
    menuTexts = []
    menuActions = []
    menuActions = []
    toolbarActions = []

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'NgiiDataUtils_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.pluginIsActive = False
        self.dockwidget = None

    def initGui(self):
        # 기존 NGII 메뉴가 있으면 재사용. 없으면 추가
        self.addNgiiMenu()
        self.togglePanel()

    def addNgiiMenu(self):
        # https://gis.stackexchange.com/questions/227876/finding-name-of-qgis-toolbar-in-python
        qgisMenuBar = self.iface.mainWindow().menuBar()

        # 이미 NGII 메뉴 있는지 찾아보기
        ngiiMenu = None
        for action in qgisMenuBar.actions():
            if action.text() == self.mainMenuTitle:
                ngiiMenu = action.menu()
                break

        # 없음 만들고 있음 그냥 사용
        if ngiiMenu is None:
            self.mainMenu = QMenu(self.iface.mainWindow())
            self.mainMenu.setTitle(self.mainMenuTitle)
            qgisMenuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.mainMenu)
        else:
            self.mainMenu = ngiiMenu

        # 이미 NGII 툴바 있는지 찾아보기
        ngiiToolbar = None
        for toolbar in self.iface.mainWindow().findChildren(QToolBar):
            # if toolbar.objectName() == self.mainMenuTitle:
            if toolbar.windowTitle() == self.mainMenuTitle:
                ngiiToolbar = toolbar
                break

        # 없음 만들고 있음 그냥 사용
        if ngiiToolbar is None:
            self.toolbar = self.iface.addToolBar(self.mainMenuTitle)
            self.toolbar.setObjectName(self.mainMenuTitle)
        else:
            self.toolbar = ngiiToolbar

        # 세부 메뉴, 버튼 추가
        menuIcons = ['icon.png']
        menuTexts = [u'국토지리정보원 데이터 중첩검사']
        menuActions = [self.togglePanel]

        assert (len(menuIcons) == len(menuTexts))
        assert (len(menuTexts) == len(menuActions))

        self.menuActions = []
        self.toolbarActions = []
        for i in range(0, len(menuTexts)):
            icon = QIcon(os.path.join(os.path.dirname(__file__), 'icons', menuIcons[i]))
            text = menuTexts[i]
            action = QAction(icon, text, self.iface.mainWindow())
            self.mainMenu.addAction(action)
            action.triggered.connect(menuActions[i])
            button = self.toolbar.addAction(icon, text, menuActions[i])

            self.menuActions.append(action)
            self.toolbarActions.append(button)

    def removeNgiiMenu(self):
        if self.toolbar is not None:
            # 내가 등록한 툴바 아이템 제거
            for action in self.toolbarActions:
                self.toolbar.removeAction(action)
            # 더이상 항목이 없으면 부모 제거
            if len(self.toolbar.actions()) == 0:
                self.toolbar.deleteLater()

        if self.mainMenu is not None:
            for action in self.menuActions:
                self.mainMenu.removeAction(action)
            print len(self.mainMenu.actions())
            if len(self.mainMenu.actions()) == 0:
                self.mainMenu.deleteLater()

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING NgiiDataUtils"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        self.iface.removeDockWidget(self.dockwidget)
        self.removeNgiiMenu()

    #--------------------------------------------------------------------------

    def togglePanel(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING NgiiDataUtils"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = NgiiDataUtilsDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
        else:
            self.dockwidget.close()
