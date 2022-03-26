import sys

import axipy



class Plugin:
    def __init__(self, iface):
        self.iface = iface
        sys.path.append(iface.local_file('dependencies'))

        menubar = iface.menubar
        tr = iface.tr
        local_file=iface.local_file
        self.__action = menubar.create_button(iface.tr('Каталог точек'),
                                              icon=local_file('toolprocessing', 'catalog_points.png'), on_click=self.run_tools)
        #position = menubar.get_position(tr('Таблица'), tr('Действие Операции'))
        position = menubar.get_position(tr('Таблица'), tr('Действие'))
        position.add(self.__action, size=2)
        #print("Get catalog")
        self.__catalog=axipy.app.mainwindow.catalog
        if self.__catalog is None:
            print("axipy.app.mainwindow.catalog is None")
        self.__selection=axipy.gui.selection_manager
        #print("Get catalog 1")
        self.__catalog.updated.connect(self.__tryInReady)
        #print("Get catalog 2")
        self.__tryInReady()
        #self.__selection.changed.connect(self.__changeSelection)
    def unload(self):
        self.__catalog.updated.disconnect(self.__tryInReady)
        #self.__viewService.countChanged.disconnect(self.__tyrIsReadyForMapAndSelection)
        self.iface.menubar.remove(self.__action)
    def run_tools(self):

        from .toolprocessing.DlgCatalogPoints import DlgCatalog
        dlg=DlgCatalog()
        dlg.show()
        if dlg.isOk:
            propertyRun=dlg.PropertyRun
            from .toolprocessing.SimpleGeometryCatalog import BuildCatalog
            BuildCatalog(propertyRun)
    def __changeSelection(self):
        print("run select")
    def __tryInReady(self):
        '''
        Проверяем условия для готовности инструмента к работе
        Должна быть открыта хотя бы одна пространственная таблица
        :return:
        '''
        tables=self.__catalog.tables
        for table in tables:
            if table.is_spatial and table.count()>0:
                self.__action.action.setEnabled(True)
                return

        self.__action.action.setEnabled(False)