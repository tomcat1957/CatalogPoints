class Plugin:
    def __init__(self, iface):
        self.iface = iface
        menubar = iface.menubar
        tr = iface.tr
        local_file=iface.local_file
        self.__action = menubar.create_button(iface.tr('Проверка полигонов'),
                                              icon=local_file('ui', 'checkregions_32x32.png'), on_click=self.run_tools)