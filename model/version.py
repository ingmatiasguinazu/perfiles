
# -*- coding: utf-8 -*-

import os.path
import datetime

from . import *

class Version():
    """ Versions

    Atributos:
        __applications
    """

    def __init__(self, p_app_file, p_seq, p_summary, p_recid=None):
        " Creaidor"

        # Validaciones a la creacion
        if p_seq in p_app_file.versions:
            raise exc.KeyAlreadyExistsError()

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
 

    def has_unsaved_changes(self):
        "Indica si existen cambios sin grabar."
        
        if self.recid == None:
            return True 

        l_db_cnx = self.app_file.db_cnx

        # Objeto diferente a DB
        l_SQL = 'SELECT * FROM {} WHERE recid = ?'.format(
                self.__class__.__name__)
        l_params = (self.recid, )
        l_row = l_db_cnx.execute(l_SQL, l_params).fetchone()
        if l_row == None:
            raise exc.CorruptDataBaseError()

        for l_field in self.__dict__.keys():
            if l_field not in ('app_file',):
                if self.__dict__[l_field] != l_row[l_field]:
                    return True
 
        return False #No hay cambios

   

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
        l_SQL = (           'SELECT app.*, app_row.*, app.recid as recid_a, app_row.recid as recid_b'
                +            ' FROM Application AS app'
                +      ' INNER JOIN ApplicationRow AS app_row' 
                +                   ' ON app_row.application ='  
                +                                     ' app.recid'
                +      ' INNER JOIN Version AS vrs_app_from' 
                +                   ' ON vrs_app_from.recid ='  
                +                                     ' app.version_from'
                +      ' INNER JOIN Version AS vrs_row_from' 
                +                   ' ON vrs_row_from.recid ='  
                +                                     ' app_row.version_from'
                + ' LEFT OUTER JOIN Version vrs_app_to' 
                +                   ' ON vrs_app_to.recid = app.version_to' 
                + ' LEFT OUTER JOIN Version vrs_row_to' 
                +                   ' ON vrs_row_to.recid = app_row.version_to' 
                +           ' WHERE vrs_app_from.seq <= ?'
                +             ' AND ( vrs_app_to.seq > ? OR '
                +                                   'vrs_app_to.seq is NULL )'
                +             ' AND vrs_row_from.seq <= ?'
                +             ' AND ( vrs_row_to.seq > ? OR '
                +                                   'vrs_row_to.seq is NULL )')
        l_params = (l_seq, l_seq, l_seq, l_seq)
        l_rows = l_db_cnx.execute(l_SQL, l_params) 
        for l_row in l_rows:
            l_app = Application(self, l_schema, l_row['code'], 
                    l_row['name'], l_row['recid_a'], l_row['recid_b'])
            a=Right(self, l_app, 'RESTRINCT', 'NO', 'YES')
            Right(self, l_app, 'ADD', '', 'add')
            Right(self, l_app, 'MODITY', '', 'modify')
            Right(self, l_app, 'DELETE', '', 'delete')
            print(l_app)

        return l_schema

    def reset_as_new(self):
        '''  Setea la version como version de trabajo '''
        self.recid = None
        self.effective_date = None
        self.seq = 1
        self.summary = '-- Nueva Version --'


    def save(self):
        "Registra las modificaciones permanentemente"

        if not self.has_unsaved_changes():
            return

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

    

