
# -*- coding: utf-8 -*-

import os.path
import datetime

from .dbfile import DBFile
from . import *

class AppFile:
    """ Archivo de la aplicación
    """

    def __init__(self):
        self.db_cnx = None
        self.db_file = None
        self.versions = {}
        l_vrs = Version(self, 1, '-- Nueva Version --')
        self.wrk_schema = l_vrs.get_schema()


    def open(self, p_file):
        " Abre archivo existente"

        # Verifico si archivo pre-existente
        if not os.path.isfile(p_file):
            raise exc.NotFileSelectedError(p_file)
        
        # Destruyo esquema y versiones actuales
        self.wrk_schema.reset_as_new()
        self.wrk_schema.delete()
        self.versions.clear()

        # Abro el archivo mediante conexion
        if self.db_cnx != None:
            self.db_cnx.close()
        self.db_cnx = sqlite3.connect(p_file)
        self.db_file = p_file
        self.db_cnx.row_factory = sqlite3.Row

        # TO COMPLETE:  Validar coherencia Estructura Archivo
        
        #Cargo las Versions
        l_SQL = (   'SELECT * ' 
                +     'FROM Version '
                + 'ORDER BY seq DESC')
        l_rows = self.db_cnx.execute(l_SQL) 
        l_vrs = None
        l_wrk_vrs = None
        for l_row in l_rows:
            if l_wrk_vrs == None and l_row['effective_date'] != None:
                l_wrk_vrs = Version(self, l_row['seq'] + 1, 
                        '-- Nueva Version --')
            l_vrs = Version(self, l_row['seq'], l_row['summary'], 
                  l_row['recid'])
            l_vrs.effective_date = l_row['effective_date']
            if l_vrs.effective_date == None:
                l_wrk_vrs = l_vrs

        self.wrk_schema = l_wrk_vrs.get_schema()


    def saveas(self, p_file):
        "Grabo en nuevo archivo"

        # Verifico si archivo pre-existente
        if os.path.isfile(p_file):
            os.remove(p_file)

        # Abro el archivo mediante conexion
        if self.db_cnx != None:
            self.db_cnx.close()
        self.db_cnx = sqlite3.connect(p_file)
        self.db_file = p_file
        self.db_cnx.row_factory = sqlite3.Row
        DBFile(p_file)

        self.wrk_schema.reset_as_new()
        self.wrk_schema.version.reset_as_new()
        self.versions.clear()
        self.versions[self.wrk_schema.version.seq] = self.wrk_schema.version

        self.wrk_schema.save()


    def apply_version(self, p_eff_date):
        " Graba modificaciones y aplica version."
        #TO COMPLETE:  
        if (not self.has_unsaved_changes() 
                and not self.version.has_change()):
            raise exc.NoChagesForVersionError()

        if p_eff_date < date(2000,1,1): #Fecha minima admitida
            raise exc.DateTooOldError()

        p_prev_date =date(1999, 12, 31) #Coloco fecha mínima
        l_seq = self.version.seq
        if ( l_seq - 1 ) in self.version.app_file.versions:
            p_prev_date = self.version.app_file.versions[
                    l_seq - 1].effective_date
        if p_eff_date < p_prev_date:
            raise exc.VersionDateNotPermited()

        self.version.effective_date = p_eff_date
        self.version.save()
        self.save()
        l_vrs = Version(self, self.wrk_schema.version.seq + 1, 
                '-- Nueva Version --')

    def discare_changes(self):
        ''' Descarta cambios no guardados '''
        l_vrs = self.wrk_schema.version
        self.wrk_schema.reset_as_new()
        self.wrk_schema.delete()
        self.wrk_schema = l_vrs.get_schema()
   

    def undo_version(self):
        "Deshace las modificaciones de una version."
        
        self.discare_changes() #Elimino cambios no grabados
        self.wrk_schema.version.undo_changes() #Elimino version y sus cambios
        l_seq = self.wrk_schema.version.seq
        del self.version.app_file.versions[l_seq] #Elimino version del app_file
        
        #Determino nueva version de trabajo
        if ( l_seq - 1 ) in self.versions:
            l_vrs = self.versions[l_seq - 1]
            l_vrs.effective_date = None
            l_vrs.save()
        else:
            l_vrs = Version(self.version.app_file, 1, '-- Nueva Version --')

        self.wrk_schema = l_vrs.get_schema()


