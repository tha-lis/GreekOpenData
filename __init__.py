# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GreekOpenData
                                 A QGIS plugin
 View free Greek Web-services
                             -------------------
        begin                : 2015-10-18
        copyright            : (C) 2015 by Simitzi Eirini;Thanos Strantzalis
        email                : simitzi.irini@gmail.com;thanos.strantzalis@gmail.com
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
    """Load GreekOpenData class from file GreekOpenData.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mainPlugin import GreekOpenData
    return GreekOpenData(iface)
