
# -*- coding: utf-8 -*-

import os.path
import datetime

from . import *

class Schema:
    """ Administrador general de aplicaciones
    
    """
    def __init__(self, p_vrs):
        self.__objid
        self.version = p_vrs
        self.applications = {}
        self.objects = {}

        l_db_cnx = self.version.app_file.db_cnx
        l_seq = self.version.seq
        if l_db_cnx == None:
            return
        
        #Cargo aplicaciones
        l_SQL = (           'SELECT app.* '
                +            ' FROM Application AS app'
                +      ' INNER JOIN Version AS vrs_from' 
                +                   ' ON vrs_from.recid ='  
                +                                     ' app.version_from_recid'
                + ' LEFT OUTER JOIN Version vrs_to' 
                +                   ' ON vrs_to.recid = app.version_to_recid' 
                +           ' WHERE vrs_from.seq <= ?'
                +             ' AND ( vrs_to.seq > ? OR vrs_to.seq is NULL )')
        l_params = (l_seq, l_seq)
        l_rows = l_db_cnx.execute(l_SQL, l_params) 
        for l_row in l_rows:
            l_app = Application(self, l_row['code'], 
                    l_row['name'], l_row['recid'])

    def get_objid():
        g_objid = g_objid + 1
        return g_obj_id
            
    def save(self):
        "Grabo modificaciones permanentemente"
        if self.version.app_file.db_cnx==None:
            raise exc.NotFileSelectedError() 
        
        for l_app in self.applications.values():
            l_app.save()

    def reset_as_new(self):
        ''' Elementos del modelo se setean a nuevos '''
        for l_app in self.applications.values():
            l_app.reset_as_new()

 
    def undo(self):
        "Deshace cambios no grabados"
        self.applications = self.version.get_schema().applications


    def has_unsaved_changes(self):
        "  Indica si existen cambios sin grabar"
        
        # Lo de memoria es diferente a lo del archivo
        for l_app in self.applications.values():
            if l_app.has_unsaved_changes():
                return True
        return False
         
    def __str__(self):
        l_text = '"Schema" ' 
        l_text = l_text + 'vrs (cur): ' + (self.version.__str__())
        for l_app in self.applications.values():
            l_text = l_text + ('\n app -> ' + l_app.__str__())
        return l_text


