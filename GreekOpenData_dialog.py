# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GreekOpenDataDialog
                                 A QGIS plugin
 View free Greek Web-services
                             -------------------
        begin                : 2015-10-18
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Simitzi Eirini;Thanos Strantzalis
        email                : simitzi.irini@gmail.com;thanos.strantzalis@gmail.com
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

import os
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget, QLineEdit, QApplication,QMessageBox
from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GreekOpenData_dialog_base.ui'))

class extQLineEdit(QLineEdit):
	# modified QLineEdir object to support the click event
    def __init__(self,parent):
	QLineEdit.__init__(self,parent)	
		
    def mousePressEvent(self,QMouseEvent):
        self.emit(SIGNAL("clicked()")) # emit the event




class GreekOpenDataDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GreekOpenDataDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        #geom = self.search_lineEdit.geometry()
	self.search_lineEdit = extQLineEdit(self.search_lineEdit)
	self.search_lineEdit.setGeometry(1,1,473,20)	
	self.connect(self.search_lineEdit,SIGNAL("clicked()"),self.search_clicked )



    def search_clicked(self):
        # clear the welcome message when clicked
        welcomeEN = "Search for dataset name,"
        welcomeGR = unicode("Αναζήτηση για όνομα,","utf-8")
               
        text = self.search_lineEdit.text()

        if welcomeEN in text or welcomeGR in text:
            self.search_lineEdit.setText("")        
        
