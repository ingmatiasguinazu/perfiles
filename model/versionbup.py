
# -*- coding: utf-8 -*-

import os.path
import datetime

from . import *

class Version:
    """ Versions

    Atributos:
        __applications
    """

    def __init__(self, p_app_file, p_seq, p_summary, p_recid=None):
        " Creador"
        
        # Validaciones a la creacion
        if p_seq in p_app_file.versions:
            raise exc.AlreadyExistsError()

        # Inicializo propiedades
        self.seq = p_seq
        self.summary = p_summary
        self.effective_date = None
        self.app_file = p_app_file
        self.recid = p_recid

        # Me inicializo en componentes con relaciones OneToMenuMe
        self.app_file.versions[p_seq] = self


    def undo_changes(self): 
        "Deshace cambios y elimina version en DB."
        pass #TO COMPLETE
    

    def get_schema(self):
        "Devuelve el esquema vigente a esta version."

        l_schema = Schema(self)

        l_db_cnx = self.app_file.db_cnx
        l_seq = self.seq
        if l_db_cnx == None:
            return l_schema

        ##############################################
        ##          CREO APLICACIONES     
        ##############################################
        #Cargo aplicaciones
        l_SQL = (           'SELECT app.* '
                +            ' FROM Application AS app'
                +      ' INNER JOIN Version AS vrs_from' 
                +                   ' ON vrs_from.recid ='  
                +                                     ' app.version_from'
                + ' LEFT OUTER JOIN Version vrs_to' 
                +                   ' ON vrs_to.recid = app.version_to' 
                +           ' WHERE vrs_from.seq <= ?'
                +             ' AND ( vrs_to.seq > ? OR vrs_to.seq is NULL )')
        l_params = (l_seq, l_seq)
        l_rows = l_db_cnx.execute(l_SQL, l_params) 
        for l_row in l_rows:
            l_app = Application(self, l_schema, l_row['code'], 
                    l_row['name'], l_row['recid'])
            
        return l_schema

    def reset_as_new(self):
        '''  Setea la version como version de trabajo '''
        self.recid = None
        self.effective_date = None
        self.seq = 1


    def save(self):
        "Registra las modificaciones permanentemente"

        l_db_cnx = self.app_file.db_cnx
        if l_db_cnx == None:
            raise NotFileSelectedError()

        if self.recid != None:
            l_SQL = ('UPDATE Version' 
                    +'   SET summary = ?'
                    +     ', effective_date = ?'
                    +     ', seq = ?'
                    +' WHERE recid = ?')
            l_params = (self.summary, self.effective_date, self.seq, 
                    self.recid)  
            l_db_cnx.execute(l_SQL, l_params)
        else:
            l_SQL = ( 'INSERT INTO Version' 
                    +           ' (summary, effective_date, seq)'
                    +     ' VALUES (?,?,?)' )
            l_params = (self.summary, self.effective_date, self.seq)
            l_cursor = l_db_cnx.cursor()
            l_cursor.execute(l_SQL, l_params) #inserto el nuevo registro
            self.recid = l_cursor.lastrowid
        print('Grabo version son SQL {} y parametros {}'.format(l_SQL, l_params))
        l_db_cnx.commit()
            

    def __str__(self):
        l_text = '"Version" ' 
        l_text = l_text + ' [seq]=%i' % (self.seq,)
        l_text = l_text + ' [summaty]=%s' % (self.summary,)
        l_text = l_text + ' [effective_date]=%s' % (self.effective_date,)
        return l_text

    

