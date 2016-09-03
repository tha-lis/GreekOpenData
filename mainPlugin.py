# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GreekOpenData
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

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,QRectF,Qt,QEvent
from PyQt4.QtGui import QAction, QIcon,QTableWidgetItem,QMessageBox,QHeaderView,QFont,QWidget,QTextCursor
from PyQt4.QtGui import QGraphicsScene,QPixmap,QGraphicsPixmapItem,QPainter, QAbstractItemView

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from GreekOpenData_dialog import GreekOpenDataDialog
from webService_CLASS import WebServiceParams
import os.path
import csv, Image
from qgis.gui import *
from qgis.core import *
import sys
reload(sys)
sys.setdefaultencoding("utf-8")





class GreekOpenData:
    """QGIS Plugin Implementation."""   

    
    def __init__(self, iface):
        
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GreekOpenData_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = GreekOpenDataDialog()
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Greek Open Data')
        self.language = "GR"  #start language
        self.csvWithDatasets = os.path.join(os.path.dirname(__file__),"data.csv")
        self.quicklooks_dir =  os.path.join(os.path.dirname(__file__),"quicklooks")
        
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GreekOpenData')
        self.toolbar.setObjectName(u'GreekOpenData')
        # define the datasets used. List of webServices custon objects
        self.datasets = self.loadDatasets()        
        #events        
        self.dlg.tableWidget.itemSelectionChanged.connect(self.updateDescAndQL)
        self.dlg.load_btn.released.connect(self.loadWebService)
        self.dlg.close_btn.released.connect(self.close)        
        self.init_table()
        self.updateLanguage()        
        self.dlg.search_lineEdit.textEdited.connect(self.search)        
        self.dlg.language_comboBox.currentIndexChanged.connect(self.updateLanguage)
  
   

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GreekOpenData', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, "Greek Open Data", parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis("Greek Open data" )

        if add_to_toolbar:
            self.iface.addWebToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)
            

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GreekOpenData/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())        


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Greek Open Data'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def getSelectedNameAndType(self):
        """Gets the name and servive type of the selected dataset."""
        # get the selected row (list with indices)
        selectedIndexes = self.dlg.tableWidget.selectionModel().selectedRows()        
        row = selectedIndexes[0].row()

        # get name and service typeof selected row
        dataset_name = self.dlg.tableWidget.item(row, 0).text()
        dataset_serviceType = self.dlg.tableWidget.item(row, 1).text()
        #dataset_name = unicode(dataset_name, 'utf-8')
        return [dataset_name,dataset_serviceType]


    def loadDatasets(self):
        f = open(self.csvWithDatasets, "rb")
        reader = csv.reader(f)       
        
        webServicesList = []
        rownum = 0
        for row in reader:
            #make sure we exclude the header
            if rownum!=0:
                nameGr = row[1]
                nameEn = row[3]
                name = nameEn
                sourceGR = row[2]
                sourceEN = row[4]
                creationDate = row[6]
                lastUpdate = row[5]
                QLname = row[7]
                descEN = row[8]
                descGR = row[9]
                serviceType = row[10]
                layerName = row[11]
                server = row[12]

                webServiceObj = WebServiceParams(name, nameGr,nameEn,sourceGR,sourceEN,creationDate,lastUpdate,
                                                 descEN,descGR,serviceType, layerName,server,QLname)
                         

                webServicesList.append(webServiceObj)
            rownum = rownum + 1
                
        f.close()
        return webServicesList
    def updateLanguage(self):
        # get the new language
        language = str(self.dlg.language_comboBox.currentText())        
        # Change the self.language propertie and change the labe;s
        if language == "English":
            self.language = "EN"
            self.dlg.desc_lbl.setText("Description")
            self.dlg.preview_lbl.setText("Preview")
            self.dlg.load_btn.setText("Load")
            self.dlg.close_btn.setText("Close")
            self.dlg.search_lbl.setText("Search")
        elif language == "Greek":
            self.language = "GR"
            self.dlg.desc_lbl.setText(unicode("Περιγραφή", 'utf-8'))
            self.dlg.preview_lbl.setText(unicode("Προεπισκόπηση",'utf-8'))
            self.dlg.load_btn.setText(unicode("Φόρτωση",'utf-8'))
            self.dlg.close_btn.setText(unicode("Κλείσιμο",'utf-8'))
            self.dlg.search_lbl.setText(unicode("Αναζήτηση",'utf-8'))

        self.dlg.preview_lbl.setAlignment(Qt.AlignRight)
        #refill the table
        self.init_table()
        # clear description and quicklook
        self.dlg.textEdit.clear()
        # clear search box
        #text = self.dlg.search_lineEdit.setText("")
        self.init_searchBox()
        # make a new emptey scene to show
        if not self.dlg.graphicsView is None:
            scene = QGraphicsScene()
            pic = QPixmap()
            scene.addItem(QGraphicsPixmapItem(pic))
            self.dlg.graphicsView.setScene(scene)        
            self.dlg.graphicsView.show()          

        
        
    def updateDescAndQL(self):
        # get the name of the selected dataset
        dataset_name, dataset_serviceType = self.getSelectedNameAndType()        

        #custom web service object
        dataset = self.selectdataSets(dataset_name,dataset_serviceType)        

        quicklook = os.path.join(self.quicklooks_dir, dataset.QLname+".jpg")
        desc = dataset.getDescription(self.language)
        name = dataset.getName(self.language)

        #update decription
        self.dlg.textEdit.clear()       
        #creation and last update
        if self.language =="EN":
            crDate = "Creation date : "+dataset.creationDate 
            update = "Last update : "+dataset.lastUpdate            
        elif self.language =="GR":            
            crDate = unicode("Ημερομηνια δημιουργιας : "+dataset.creationDate,'utf-8')
            update = unicode("Τελευταία ενημέρωση : "+dataset.lastUpdate,'utf-8')

        cursor = QTextCursor(self.dlg.textEdit.document())
        cursor.insertHtml("<h3> "+name+" <br><br></h3>")
        cursor.insertHtml("<p> "+desc+" <br><br><br></p>")
        cursor.insertHtml("<p><i> "+crDate+" <br></i></p>")
        #cursor.insertHtml("<p><i> "+update+" <br></i></p>")

        self.dlg.textEdit.setReadOnly(True)
        #update quicklook       
        
        #GET DIMENSIONS OF THE IMAGE
        img = Image.open(quicklook)
        w, h = img.size

        scene = QGraphicsScene()
        pic = QPixmap(quicklook)
        scene.addItem(QGraphicsPixmapItem(pic))

        self.dlg.graphicsView.setScene(scene)
        self.dlg.graphicsView.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        self.dlg.graphicsView.show()        
        

    def selectdataSets(self, dataset_name, dataset_serviceType):

        for dataset in self.datasets:
            # get the names both in Green and in English in UTF-8 encoding
            dataset_nameGR = unicode(dataset.nameGr, 'utf-8')
            dataset_nameEN = unicode(dataset.nameEn, 'utf-8')
            # check which dataset has the name we are looking for 
            if dataset_name == dataset_nameGR or dataset_name == dataset_nameEN:
                if dataset_serviceType == dataset.serviceType:
                    selectedDataset = dataset
                    break
        
        return selectedDataset

    def setTableWidgetBehavour(self):

        #set rows and columns default sizze and lock it       

        self.dlg.tableWidget.setColumnWidth(0,200)
        self.dlg.tableWidget.setColumnWidth(1,45)
        self.dlg.tableWidget.setColumnWidth(2,358)
        self.dlg.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Fixed)
        self.dlg.tableWidget.verticalHeader().setResizeMode(QHeaderView.Fixed)        
        
        self.dlg.tableWidget.resizeRowsToContents() 
        
        # qtableWidget behavour
        self.dlg.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dlg.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    def fill_table(self,datasetsList):
         # first delete all elements of table        
        self.dlg.tableWidget.setRowCount(0)
        self.dlg.tableWidget.setColumnCount(3)

                        
        #FILL THE TABLE WIDGET
        # get a sorted version of lirt with WebServiceObjects
        WebServiceObjects = self.sort(datasetsList)
    
        for dataset in WebServiceObjects:
            index = WebServiceObjects.index(dataset)
            self.dlg.tableWidget.insertRow(index)            
        # fill layer name
            self.dlg.tableWidget.setItem(index , 0, QTableWidgetItem(dataset.getName(self.language))) #dataset name
            self.dlg.tableWidget.setItem(index , 1, QTableWidgetItem(dataset.serviceType)) # webservice type
            self.dlg.tableWidget.setItem(index , 2, QTableWidgetItem(dataset.getSource(self.language))) # source organization

        #name of columns
        if self.language == "EN":
            self.dlg.tableWidget.setHorizontalHeaderLabels(["Name","Type","Organization"])
        elif self.language == "GR":
            namegr =  unicode("Όνομα", 'utf-8')
            typegr = unicode("Τύπος", 'utf-8')
            orggr = unicode("Οργανισμός", 'utf-8')
            self.dlg.tableWidget.setHorizontalHeaderLabels([namegr,typegr,orggr])

        self.setTableWidgetBehavour() 
        

    def init_table(self):
        # fille the table with the entire dataset collection
        self.fill_table(self.datasets)

    def init_searchBox(self):
        font = self.dlg.search_lineEdit.font()
        font.setItalic(True)
        self.dlg.search_lineEdit.setFont(font)
##        self.dlg.search_lineEdit.setFont(font)
        # welcome text
        if self.language == "EN":
            self.dlg.search_lineEdit.setText("Search for dataset name, service type or organization...")
        elif self.language == "GR":
            self.dlg.search_lineEdit.setText(unicode("Αναζήτηση για όνομα, τύπο υπηρεσίας ή οργανισμό...","utf-8"))

        
           

    def search(self):
        # first set/change the  font of the serach box
        font = self.dlg.search_lineEdit.font()
        font.setItalic(False)
        self.dlg.search_lineEdit.setFont(font)

        # clear description and quicklook
        self.dlg.textEdit.clear()
        
        # make a new emptey scene to show
        if not self.dlg.graphicsView is None:
            scene = QGraphicsScene()
            pic = QPixmap()
            scene.addItem(QGraphicsPixmapItem(pic))
            self.dlg.graphicsView.setScene(scene)        
            self.dlg.graphicsView.show()  
        
        # function the searches for a string in the datasets name, service type and otganization
        text = self.dlg.search_lineEdit.text()        
        # convert to lower case and remove greek accents in case of Greek
        text = text.lower()
        text = self.removeGreekAccents(text)  
        foundDatasets = []
        for dataset in self.datasets:
            # use lowercase characters and remove greek accents , to make the comparison
            name = self.removeGreekAccents(dataset.getName(self.language).lower())
            source = self.removeGreekAccents(dataset.getSource(self.language).lower())
            serviceType = self.removeGreekAccents(dataset.serviceType.lower())
            
            if text in name or text in source or text in serviceType:            
            #QMessageBox.information(None, "DEBUG:", str(type(dataset.getName(self.language))))                           
                foundDatasets.append(dataset)
        #fill the table with the found datasets
        self.fill_table(foundDatasets)     
            
        

    def sort(self,listOfWebServiceObj):
        """Sorts the datasets by name."""
        # make new list of list[name, obj) and sort it
        sortedList = []
        for WebServiceObj in listOfWebServiceObj:
            name = WebServiceObj.getName(self.language)
            # convert to lowercase and remove Greek accents to order properly
            name = name.lower()
            name = self.removeGreekAccents(name)         
            
            sortedList.append([name,WebServiceObj])
        sortedList.sort()
        #build the output list (only with the WebServiceObj)
        outputList = []
        for element in sortedList:
            outputList.append(element[1])       

        return outputList

    def removeGreekAccents(self,utext):
        #function to removes the Greek accents from a unicode lowercase string           
        if "ά" in utext:
            #SQMessageBox.information(None, "DEBUG:", str("removeGreekAccents condition reached"))
            utext = utext.replace("ά","α")
        if "έ" in utext:
            utext = utext.replace("έ","ε")
        if "ή" in utext:
            utext = utext.replace("ή","η")
        if "ί" in utext:
            utext = utext.replace("ί","ι")
        if "ό" in utext:
            utext = utext.replace("ό","ο")
        if "ύ" in utext:
            utext = utext.replace("ύ","υ")
        if "ώ" in utext:
            utext = utext.replace("ώ","ω")        
               
        return utext
            
  

    def loadWebService(self):
        # get the selected row
        dataset_name,dataset_serviceType = self.getSelectedNameAndType()        

        #custom web service object
        dataset = self.selectdataSets(dataset_name,dataset_serviceType)        
                
        urlWithParams = dataset.webServiceParams()        
        if dataset.serviceType== "WMS":
            rlayer = QgsRasterLayer(dataset.webServiceParams(), dataset.getName(self.language), dataset.serviceType.lower())
            if not rlayer.isValid():
                QMessageBox.information(None, "ERROR:", str(dataset_name + "  cannot be loaded. Check your internet connection."))
               
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)
        elif dataset.serviceType== "WFS":                       
            vlayer = QgsVectorLayer(dataset.webServiceParams(), dataset.getName(self.language), dataset.serviceType)
            #QMessageBox.information(None, "ERROR:", str(dataset.webServiceParams())) 
            if not vlayer.isValid():
                QMessageBox.information(None, "ERROR:", str(dataset_name + "  cannot be loaded. Check your internet connection."))
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            #re-appear window
            self.dlg.raise_()
            self.dlg.activateWindow()

                
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def close(self):
        #clear everything
        self.init_table()
        # clear description and quicklook
        self.dlg.textEdit.clear()
        # clear search box
        #text = self.dlg.search_lineEdit.setText("")
        self.init_searchBox()
        # make a new emptey scene to show
        if not self.dlg.graphicsView is None:
            scene = QGraphicsScene()
            pic = QPixmap()
            scene.addItem(QGraphicsPixmapItem(pic))
            self.dlg.graphicsView.setScene(scene)        
            self.dlg.graphicsView.show()
        """close the dialog"""
        self.dlg.close()
