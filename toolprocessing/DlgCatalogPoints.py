import os
from pathlib import Path

import axipy
from PySide2 import QtCore
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog, QFileDialog

from CatalogPoints.toolprocessing.Utils import getListTabUnicalFields, getListTabFields
def getPathOutTable(path_tab_source,typeOutFile):
    ext_file="tab"
    if not(typeOutFile=="MapInfo"):
        ext_file="xlsx"
    p = Path(path_tab_source)
    folder=str(p.parent)
    name=p.stem
    catalog_path=os.path.join(folder,name+"_CatalogPoints."+ext_file)
    return catalog_path
def getPathOutFolder(path_tab_source):
    p = Path(path_tab_source)
    folder=str(p.parent)
    name=p.stem
    catalog_path=os.path.join(folder,os.sep+name+"CatalogPoints")
    new_path=Path(folder,name+"_CatalogPoints")
    return str(new_path)
class DlgCatalog:
    __statusIsOk=False
    __isChangeStatusUnicalField=False
    __outCoordSys=None
    def __init__(self):
        self.__parentWin=axipy.app.mainwindow.qt_object()
        self.load_ui()
    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "dlgCatalogPoints.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window  = loader.load(ui_file,self.__parentWin)
        ui_file.close()
        self.window.pb_saveas.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "save_as_32.png")))

        #icon=QIcon("save_as_32.png")
        #self.window.pb_saveas.setIcon(QIcon("save_as_32.png"))
        #self.window.setWindowModality(QtCore.Qt.ApplicationModal)
        self.window.setWindowFlags(
            self.window.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.__fillListTable()
        self.window.pbClose.clicked.connect(self.__close)
        self.window.pb_run.clicked.connect(self.__run)
        self.window.pb_coordsys.clicked.connect(self.__change_coordSys)
        self.window.pb_saveas.clicked.connect(self.__select_out_path)
        self.window.cb_tables.currentIndexChanged.connect(self.__changeTable)
        self.window.cb_outFormat.currentIndexChanged.connect(self.__changeTypeOut)
        self.window.rb_oneObjFile.toggled.connect(self.__outMultiFiles)
        self.window.ch_unical.stateChanged.connect(self.__changeUnicalFieldUse)

    def show(self):
        self.window.exec()
    @property
    def isOk(self):
        return self.__statusIsOk
    def __close(self):
        self.__statusIsOk=False
        self.window.close()
    def __run(self):
        self.__statusIsOk=True
        self.__parm_for_build={}
        self.__parm_for_build['source_table']=self.window.cb_tables.currentText()
        self.__parm_for_build['key_field']=self.window.cb_fields.currentText()
        self.__parm_for_build['out_coordSys']=self.__outCoordSys
        self.__parm_for_build['out_path']=self.window.ln_pathOut.text()
        self.__parm_for_build['all_one_files']=self.window.rb_allInOneFile.isChecked()
        self.__parm_for_build['out_format']=self.window.cb_outFormat.currentText()
        self.window.close()
    @property
    def PropertyRun(self):
        return self.__parm_for_build
    def __change_coordSys(self):
        dlgcoordSys= axipy.ChooseCoordSystemDialog(self.__outCoordSys)
        if dlgcoordSys.exec() == QDialog.Accepted:
            self.__outCoordSys=dlgcoordSys.chosenCoordSystem()
            self.window.ln_outCoordSys.setText(self.__outCoordSys.description)

    def __fillListTable(self):
        isUnicalFields=self.window.ch_unical.isChecked()
        self.window.cb_tables.clear()
        list_table= axipy.app.mainwindow.catalog.tables
        self.window.cb_tables.clear()
        isFirstTable=True
        for tab in list_table:
            if not tab.is_spatial:
                continue
            if isUnicalFields:
                list_fields=getListTabUnicalFields(tab)
            else:
                list_fields=getListTabFields(tab)
            if len(list_fields)==0:
                continue
            if isFirstTable:
                isFirstTable=False
                self.__outCoordSys=tab.coordsystem
                path_out=None
                path_out=tab.properties['tabFile']
                if self.window.rb_oneObjFile.isChecked():
                    new_catatalog_path=getPathOutFolder(path_out)
                else:
                    new_catatalog_path=getPathOutTable(path_out,self.window.cb_outFormat.currentText())
                self.window.ln_pathOut.setText(new_catatalog_path)
                self.window.ln_outCoordSys.setText(tab.coordsystem.description)
                self.__setFields(list_fields)
            self.window.cb_tables.addItem(tab.name)
        if len(list_fields)>0:
            self.window.cb_tables.setCurrentIndex(0)
    def __changeUnicalFieldUse(self):
        self.__isChangeStatusUnicalField=True
        self.__fillListTable()
        self.__isChangeStatusUnicalField=False
    def __changeTable(self):
        if self.__isChangeStatusUnicalField:
            return
        isUnicalFields=self.window.ch_unical.isChecked()
        name_tab=self.window.cb_tables.currentText()
        if name_tab=="":
            return
        table=axipy.app.mainwindow.catalog.find(name_tab)
        if isUnicalFields:
            list_fields=getListTabUnicalFields(table)
        else:
            list_fields=getListTabFields(table)
        if len(list_fields)>=0:
            self.__outCoordSys=table.coordsystem
            self.window.ln_outCoordSys.setText(table.coordsystem.description)
            if self.window.rb_oneObjFile.isChecked():
                try:
                    path_out=table.properties['tabFile']
                except:
                    path_out=str(Path.home())+"/"+table.name+".tab"

                new_catatalog_path=getPathOutFolder(path_out)
                self.window.ln_pathOut.setText(new_catatalog_path)
            else:
                try:
                    path_out=table.properties['tabFile']
                except:
                    path_out=str(Path.home())+"/"+table.name+".tab"
                new_catatalog_path=getPathOutTable(path_out,self.window.cb_outFormat.currentText())
                self.window.ln_pathOut.setText(new_catatalog_path)

            self.__setFields(list_fields)
        else:
            self.window.cb_fields.clear()

    def __setFields(self,fields):
        self.window.cb_fields.clear()
        for name in fields:
            self.window.cb_fields.addItem(name)
        self.window.cb_fields.setCurrentIndex(0)
    def __select_out_path(self):
        if self.window.rb_oneObjFile.isChecked():
            base_path=str(Path(self.window.ln_pathOut.text()).parent)
            directory = QFileDialog.getExistingDirectory(self.window, "Выбор директории для сохранения каталога", base_path)
            if directory is not None or directory!='':
                self.window.ln_pathOut.setText(directory)
                return
        return
    def __outMultiFiles(self):
        name_tab=self.window.cb_tables.currentText()
        if name_tab=="":
            return
        table=axipy.app.mainwindow.catalog.find(name_tab)
        path_out=table.properties['tabFile']
        if self.window.rb_oneObjFile.isChecked():
            new_catatalog_path=getPathOutFolder(path_out)
            self.window.ln_pathOut.setText(new_catatalog_path)
        else:

            new_catatalog_path=getPathOutTable(path_out,self.window.cb_outFormat.currentText())
            self.window.ln_pathOut.setText(new_catatalog_path)
    def __changeTypeOut(self):
        if not self.window.rb_oneObjFile.isChecked():
            name_tab=self.window.cb_tables.currentText()
            if name_tab=="":
                return
            table=axipy.app.mainwindow.catalog.find(name_tab)
            try:
                path_out=table.properties['tabFile']
            except:
                path_out=str(Path.home())+"/"+table.name+".tab"
            new_catatalog_path=getPathOutTable(path_out,self.window.cb_outFormat.currentText())
            self.window.ln_pathOut.setText(new_catatalog_path)


