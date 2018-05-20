# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NgiiDataUtils
                                 A QGIS plugin
 국토지리정보원 데이터 사용지원 툴
                             -------------------
        begin                : 2018-04-03
        copyright            : (C) 2018 by NGII
        email                : jangbi882@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load NgiiDataUtils class from file NgiiDataUtils.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .ngii_data_utils import NgiiDataUtils
    return NgiiDataUtils(iface)
