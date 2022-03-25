import math
import os
import time
from pathlib import Path

import axipy
from PySide2 import QtCore
from PySide2.QtWidgets import QProgressDialog
from axipy import Geometry, CoordTransformer, Point, Pnt, Line, LineString, Polygon, Feature, MultiPolygon
from pandas import ExcelWriter

from .Utils import createCatalogSchema, createTab, CartesianObjectDistance, getAttributeField, SphericalObjectDistance
import pandas as pd
def dd_to_dms(degs):
    neg = degs < 0
    degs = (-1) ** neg * degs
    degs, d_int = math.modf(degs)
    mins, m_int = math.modf(60 * degs)
    secs        =           60 * mins
    return neg, d_int, m_int, secs
def dd_to_dmsToString(degs):
    my_formatter = "{0:.3f}"
    neg, d_int, m_int, secs=dd_to_dms(degs)
    s_val=str(int(d_int))+"°"+str(int(m_int))+str("'")+my_formatter.format(secs)+'"'
    return s_val
def initProgressBar(head,message,count):
    cls_progressbar = QProgressDialog(axipy.app.mainwindow.qt_object())
    cls_progressbar.setWindowModality(QtCore.Qt.ApplicationModal)
    cls_progressbar.setWindowFlags(
        cls_progressbar.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint & ~QtCore.Qt.WindowContextHelpButtonHint)
    cls_progressbar.setWindowTitle(head)
    cls_progressbar.setLabelText(message)
    #  progdialog.canceled.connect(self.close)
    cls_progressbar.setRange(0, count)
    return cls_progressbar
class SpatialTab:
    def __init__(self,axi_tab,out_coordSys=None):
        self.__out_tab=axi_tab
        self.__list_out_features=[]
        if out_coordSys is None:
            self.__coordsys=axi_tab.coordsystem
        else:
            self.__coordsys    =out_coordSys
    @property
    def coordsystem(self):
        return self.__coordsys
    def addFeature(self,ft:Feature):
        if isinstance(ft,list):
            self.__list_out_features.extend(ft)
        else:
            self.__list_out_features.append(ft)
    def Save(self,close=False):
        self.__out_tab.insert(self.__list_out_features)
        if close:
            self.__out_tab.commit()
            self.__out_tab.close()
class PandasTable:
    def __init__(self,path_out,tab_schema):
        self.__schema=tab_schema
        self.__out_tab=path_out
        self.__coordsys=tab_schema.coordsystem
        self.__allData=[]
        self.__liastAttOut=None
        self.__prepareOutStruct()
    def __prepareOutStruct(self):
        self.__liastAttOut=[]
        for att in self.__schema:
            name=att.name
            self.__liastAttOut.append(name)
    @property
    def coordsystem(self):
        return self.__coordsys
    def addFeature(self,ft:Feature):
        if isinstance(ft,list):
            for feature in ft:
                self.__insertFeature(feature)
        else:
            self.__insertFeature(ft)
    def Save(self,close=False):
        df = pd.DataFrame(self.__allData)
        writer = ExcelWriter(self.__out_tab)
        df.to_excel(writer, 'Points',index=False)
        writer.save()
        writer.close()

    def __insertFeature(self,ft:Feature):
        if self.__liastAttOut is None:
            self.__liastAttOut=[]
            for key in ft.keys():
                if not (key=='geometry' or key=="+geometry"):
                    self.__liastAttOut.append(key)
        row={}
        '''
        for key, value in ft.items():
            if not (key=='geometry' or key=="+geometry"):
                row[key]=value
        '''
        for key in self.__liastAttOut:
            value=ft.get(key)
            if value is None:
                value=0
            row[key]=value
        self.__allData.append(row)
def pointToFt(point:Pnt,id):
    ft={}
    ft['id_point']=id
    ft['x']=point.x
    ft['y']=point.y
    return ft
def psevdoFtToFeature(psft):
    ft=Feature()
    for key in psft.keys():
        ft[key]=psft[key]
    ft.geometry=Point(psft['x'],psft['y'])
    return ft
def listPsevDoFtToFeatures(listFt):
    fts=[]
    for psft in listFt:
        fts.append(psevdoFtToFeature(psft))
    return fts
def buildPsevdoFeatures(points_info,cs_out,cls_distance,cls_angle=None):
    list_fts=[]
    if points_info is None:
        return None
    list_points=points_info['points']
    count_points=len(points_info['points'])
    ft={}
    if count_points==1:

        ft['id_point']=0
        ft['type']=points_info['type']
        ft['x']=list_points[0].x
        ft['y']=list_points[0].y
        if cs_out.lat_lon:

            ft['slon']=dd_to_dmsToString(ft['x'])

            ft['slat']=dd_to_dmsToString(ft['y'])
        return list_fts.append(ft)
    '''
    ft=pointToFt(list_points[0],0)
    ft['type']=points_info['type']
    list_fts.append(ft)
    
    if points_info['type']=='Polyline':
        count_points=count_points+1
    '''
    point_0=Point(list_points[0].x,list_points[0].y,cs_out)
    for i in range(0,count_points-1):
        #point_0=Point(list_points[i].x,list_points[i].y,cs_out)
        point_1=Point(list_points[i+1].x,list_points[i+1].y,cs_out)
        distance=cls_distance.distance(point_0,point_1)
        ft=pointToFt(list_points[i],i)
        ft['distance']=distance
        if cs_out.lat_lon:
            ft['slon']=dd_to_dmsToString(ft['x'])

            ft['slat']=dd_to_dmsToString(ft['y'])
        list_fts.append(ft)
        point_0=point_1
    if points_info['type']=='Polyline':
        ft=pointToFt(list_points[i+1],count_points-1)
        if cs_out.lat_lon:
            ft['slon']=dd_to_dmsToString(ft['x'])

            ft['slat']=dd_to_dmsToString(ft['y'])
    else:

        ft=pointToFt(list_points[i],count_points-1)
        if cs_out.lat_lon:
            ft['slon']=dd_to_dmsToString(ft['x'])

            ft['slat']=dd_to_dmsToString(ft['y'])

    ft['distance']=0
    list_fts.append(ft)
    list_fts[0]['type']=points_info['type']
    return list_fts

def geoObjToPoints(geo_obj):
    points_info={}
    if isinstance(geo_obj,Point):
        points_info['type']="Point"
        list_points=[]
        list_points.append(Pnt(geo_obj.x,geo_obj.y))
        points_info['points']=list_points
        return [points_info]
    if isinstance(geo_obj,Line):
        points_info['type']="Line"
        list_points=[]
        list_points.append(geo_obj.begin)
        list_points.append(geo_obj.end)
        points_info['points']=list_points
        return [points_info]
    if isinstance(geo_obj,LineString):
        points_info['type']="Polyline"
        points_info['points']=geo_obj.points
        return [points_info]
    if isinstance(geo_obj,Polygon):
        points_info['type']="Polygon"
        points_info['points']=geo_obj.points
        out_objects=[]
        out_objects.append(points_info)
        holes=geo_obj.holes
        for hole in holes:
            points_info={}
            points_info['type']="Polygon"
            points_info['points']=hole
            out_objects.append(points_info)
        return out_objects
    if isinstance(geo_obj,MultiPolygon):
        list_multi_object=[]
        for item_geo in geo_obj:

            list_multi_object.extend(geoObjToPoints(item_geo))
        return list_multi_object
    return None


class PointCatalog:
    def __init__(self,table_source,id_att_key_source,table_out,cls_distance):
        self.__tab_source=table_source
        self.__tab_out=table_out
        self.__id_key_source=id_att_key_source
        self.__transform_coordsys=None
        self.__distance_cls=cls_distance
        self.__prepare()
    def __prepare(self):
        if self.__tab_out is not None:
            if not(self.__tab_source.coordsystem==self.__tab_out.coordsystem):
                self.__transform_coordsys= CoordTransformer(self.__tab_source.coordsystem, self.__tab_out.coordsystem)
        #self.__att_key=self.__get_atta_key(self.__id_key_source)
        self.__att_key=self.__id_key_source
    def run(self):
        id_obj=0
        cls_progressbar=initProgressBar("Создание каталога точек","Процесс ..",self.__tab_source.count())
        cls_progressbar.show()
        cls_progressbar.setValue(0)
        index_object=-1
        for ft in self.__tab_source.items():
            index_object=index_object+1
            if cls_progressbar is not None:
                time.sleep(0.001)
            if cls_progressbar.wasCanceled():
                break
            cls_progressbar.setValue(index_object)
            geo_obj=ft.geometry
            geo_obj=self.__transform(geo_obj)
            value_key=ft[self.__id_key_source]

            points_infos=geoObjToPoints(geo_obj)
            index_sub_obj=0

            for pt_info in points_infos:
                if pt_info is None:
                    continue
                ps_ft=buildPsevdoFeatures(pt_info,self.__tab_out.coordsystem,self.__distance_cls)
                if ps_ft is None:
                    continue
                ps_ft[0]['id_object']=id_obj
                ps_ft[0][self.__att_key]=value_key
                ps_ft[0]['id_sub_object']=index_sub_obj
                for ps in ps_ft:
                    ps[self.__att_key]=value_key
                    ps['id_sub_object']=index_sub_obj
                index_sub_obj=index_sub_obj+1
                id_obj=id_obj+1
                featurs=listPsevDoFtToFeatures(ps_ft)
                self.__tab_out.addFeature(featurs)
        if cls_progressbar is not None:
            cls_progressbar.close()
        cls_progressbar=None
        self.__tab_out.Save()
    def runMulti(self,propery_catalog):
        out_coord_sys=propery_catalog['out_coordSys']
        #tab_source=axipy.app.mainwindow.catalog.find(propery_catalog['source_table'])
        tab_out_schema=createCatalogSchema(None,out_coord_sys,True,False)
        format_out=propery_catalog['out_format']
        out_path=propery_catalog['out_path']
        for ft in self.__tab_source.items():
            value_key=ft[self.__id_key_source]
            geo_obj=ft.geometry
            geo_obj=self.__transform(geo_obj)
            if isMapInfoTab(format_out):
                #tab_out_schema=createCatalogSchema(att_key_field,out_coord_sys,True,False)
                path_table_out=os.path.join(out_path,str(value_key)+".tab")
                tab_out=createTab(path_table_out,tab_out_schema)
                virtual_tab=SpatialTab(tab_out)
            else:
                path_table_out=os.path.join(out_path,str(value_key)+".xlsx")
                virtual_tab=PandasTable(path_table_out,tab_out_schema)
            self.__tab_out=virtual_tab
            points_infos=geoObjToPoints(geo_obj)
            index_sub_obj=0

            for pt_info in points_infos:
                if pt_info is None:
                    continue
                ps_ft=buildPsevdoFeatures(pt_info,self.__tab_out.coordsystem,self.__distance_cls)

                #ps_ft[0]['id_object']=id_obj
                ps_ft[0][self.__att_key]=value_key
                ps_ft[0]['id_sub_object']=index_sub_obj
                for ps in ps_ft:
                    ps[self.__att_key]=value_key
                index_sub_obj=index_sub_obj+1
                #id_obj=id_obj+1
                featurs=listPsevDoFtToFeatures(ps_ft)
                self.__tab_out.addFeature(featurs)
            self.__tab_out.Save(True)

    def __calc_dop_param(self,point_cat):
        if(len(point_cat)==1):
            return point_cat

    def __transform(self,geo_obj):
        if self.__transform_coordsys is None:
            return geo_obj
        return geo_obj.reproject(self.__tab_out.coordsystem)
    def __get_atta_key(self,id_att):
        att_key=self.__tab_source.schema[id_att]
        return att_key
def isMapInfoTab(type_out):
    if type_out=='MapInfo':
        return True
    return False
def createOutClsDistanceCalc(out_coord_sys):
    dist_unit_m=  axipy.cs.Unit.m

    if out_coord_sys.non_earth :
        return CartesianObjectDistance(dist_unit_m)
    else:
        return SphericalObjectDistance(dist_unit_m)
def BuildCatalog(propery_catalog):
    tab_source=axipy.app.mainwindow.catalog.find(propery_catalog['source_table'])
    key_field=propery_catalog['key_field']
    att_key_field=getAttributeField(tab_source.schema,key_field)
    out_coord_sys=propery_catalog['out_coordSys']
    out_path=propery_catalog['out_path']
    typeCatalog=propery_catalog['all_one_files']
    format_out=propery_catalog['out_format']
    #dist_unit_m= axipy.cs.unit.m
    #cls_distance=CartesianObjectDistance(dist_unit_m)
    cls_distance=createOutClsDistanceCalc(out_coord_sys)
    if typeCatalog:
        ''' Все точки в один файл'''

        tab_out_schema=createCatalogSchema(att_key_field,out_coord_sys,True,False)
        if isMapInfoTab(format_out):
            #tab_out_schema=createCatalogSchema(att_key_field,out_coord_sys,True,False)
            path_table_out=out_path
            tab_out=createTab(path_table_out,tab_out_schema)
            virtual_tab=SpatialTab(tab_out)
        else:
            virtual_tab=PandasTable(out_path,tab_out_schema)
        cls_catalog=PointCatalog(tab_source,key_field,virtual_tab,cls_distance)
        cls_catalog.run()
    else:
        path_to_folder = Path(out_path)
        path_to_folder.mkdir(exist_ok=True)
        cls_catalog=PointCatalog(tab_source,key_field,None,cls_distance)
        cls_catalog.runMulti(propery_catalog)









