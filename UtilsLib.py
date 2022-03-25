import os
import pathlib
import sys

import pip


def GetHomeAxiomaFolder():
    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming/ESTI/Axioma.GIS"
    elif sys.platform == "linux":
        return home / ".local/share/ESTI/Axioma.GIS"
    elif sys.platform == "darwin":
        return home / "Library/Application Support/ESTI/Axioma.GIS"
def createFolder(name_folder):
    base_folder_axi=GetHomeAxiomaFolder()
    folder_new =base_folder_axi / name_folder
    if not folder_new.exists():
        #folder_new.mkdir()
        os.makedirs(str(folder_new))
    return str(folder_new)
def createPythonLib(name_folder_lib='pylib'):
    pathPyLib = createFolder(name_folder_lib)
    return pathPyLib
def installTool(name_pack,name_folder_lib='pylib'):
    '''
    установка требуемого пакета
    :param name_pack:
    :return:
    '''
    pathPyLib = createFolder(name_folder_lib)
    pip.main(['install', '-t', pathPyLib, name_pack])
    return
def addPathEnv(folder):
    '''
    Добавить директорию в python
    :param folder:
    :return:
    '''
    if folder in sys.path:
        return
    sys.path.append(folder)
def loadModules(list_modules):
    python_lib_path=createPythonLib()
    for mod_name in list_modules:
        installTool(mod_name)
    addPathEnv(python_lib_path)
def setEnvAddLib():
    python_lib_path=createPythonLib()
    addPathEnv(python_lib_path)

