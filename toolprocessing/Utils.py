import os
import pathlib
import sys
from math import sqrt
from pathlib import Path

import axipy
import pip
from axipy import Schema, io, Attribute, CoordSystem, attr, Point, Table


class SphericalObjectDistance:
    def __init__(self, unit: axipy.LinearUnit):
        self.__unit=unit
    def distance(self,p1:Point,p2:Point):
        return p1.get_distance(p2,self.__unit)
class CartesianObjectDistance:
    def __init__(self, unit: axipy.LinearUnit):
        self.__unit=unit
    def distance(self,p1:Point,p2:Point):
        unit_geo=p1.coordsystem.unit
        dx=p2.x-p1.x
        dy=p2.y-p1.y
        d=sqrt(dx*dx+dy*dy)
        dist=unit_geo.to_unit(self.__unit,d)
        return dist

def createCatalogSchema(atr_key:Attribute,cs_out:CoordSystem,addDistance=True,addAngle=True):
    attrs=[]
    if atr_key is not None:
        attrs.append(atr_key)
        attrs.append( attr.integer('id_object'))
    attrs.append( attr.integer('id_sub_object'))
    attrs.append( attr.string('type',10))
    attrs.append( attr.integer('id_point'))
    attrs.append( attr.double('x'))
    attrs.append( attr.double('y'))
    if addDistance :
        attrs.append( attr.double('distance'))
    if addAngle:
        attrs.append( attr.double('angle'))
    if cs_out.lat_lon:
        ''' Добавлеям представление координат в ггммсек'''
        attrs.append( attr.string('slon',12))
        attrs.append( attr.string('slat',12))
    return Schema(attrs,coordsystem=cs_out)
def createTab(path_tab:str,schema_tab:Schema):
    '''
    Создание таблицы
    :param path_tab: путь для файла tab
    :param schema_tab: схема таблицы
    :return: table
    '''
    name_tab=Path(path_tab).stem
    definition={
        'src':path_tab,
        'schema':schema_tab,
        'dataobject':name_tab
    }
    #definition['src']=path_tab
    #definition['schema']=schema_tab
    try:
        table= io.create(definition)
        return table
    except Exception as ex:
        print(ex)
        return None

def isUnicalField(table,name_field):
    isUnical=False
    sql="Select Count(*) From "+table.name+" group by "+name_field
    try:
        query_table = axipy.io.query(sql, table)
    except Exception as ex:
        print(ex)
        return False
    if query_table.count()==table.count():
        isUnical=True
    query_table.close()
    return isUnical
def getListTabUnicalFields(table:Table):
    scheme=table.schema
    list_fields=[]
    for att in scheme:
        isUnical=isUnicalField(table,att.name)
        if isUnical:
            list_fields.append(att.name)
    return list_fields
def getListTabFields(table:Table):
    scheme=table.schema
    list_fields=[]
    for att in scheme:
       list_fields.append(att.name)
    return list_fields
def getAttributeField(shema_source,name_field):
    for att in shema_source:
        if att.name==name_field:
            return att
    return None


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