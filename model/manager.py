
# -*- coding: utf-8 -*-

import model.exc as exc  # Excepciones de la aplicación


class Right:
    """ Permiso.

    Atributos
        p_app -- Referencia a la aplicacion a la cual pertenece
        p_code -- Identificador (cadena) unico
        p_granted_value -- cadena que representa "habilitacion"
        p_protected_value -- cadena que representa "restriccion"
        p_recid -- None -> No grabado en la DB
                   <> None -> Recid con el que se registra en la DB
    Ejemplo1:
        code=RESTRCTED
        granted_value='NO'
        protected_value='YES'

        es un elemento de permiso identificado con RESTRICTED.
        la cadena que representa "habilitacion" es 'NO'
        la cadena que representa "proteccion" es 'YES'

     Ejemplo2:
        code=RIGHT_ADD
        granted_value=''
        protected_value='add'

        es un elemento de permiso identificado con RIGHT_ADD.
        la cadena que representa "habilitacion" es ''
        la cadena que representa "proteccion" es 'add'
   """

# Constructor

    def __init__(self, p_app, p_code, p_granted_value='GRANTED',
            p_protected_value='PROTECTED', p_recid=None):

        # Validaciones a la creacion
        if p_code in p_app._Application__rights:
            raise exc.AlreadyExistsError(self.__class__, p_code)

        # Inicializo propiedades
        self.code = p_code
        self.granted_value = p_granted_value
        self.protected_value = p_protected_value
        self.__app = p_app
        self.recid = p_recid

        # Inicializo relacion con componentes yo_hacia_muchos
        self.__rights_elemenet_type = {}
        self.__allocations = {}

        # Me inicializo en componentes con relaciones el_hacia_muchosYo
        self.__app._Application__rights[p_code] = self

# Metodos Manipulacion

    def delete(self):
        "Elimina el objeto de la aplicacion."

        #  Elimino relacion con componentes YoHaciaMuchos
        for l_rights_ele_type in self.__rights_ele_type:
            l_rights_ele_type.delete()
        for l_allocations in self.__allocations:
            l_allocations.delete()
        #  Me elimino
        if self.recid != None:
            l_del_keys = [self.__class__ , self.recid]
            self.__app._Application_deleted_keys__[
                    l_del_key] = l_del_key
            del self.__app.Application__rights[self.code]

# Metodos Acceso a relaciones

    def get_element_types(self):
        "Recupera en una lista todos los security_element_type."
        return self.__element_types.values()

    def get_allocations(self):
        "Recupera en una lista todas las alocaciones."
        return self.__allocations.values()

# Metodos de persistencia

    def save(self, p_db_cnx, p_vrs_recid):

        "Registra las modificaciones permanentemente"
        if self.recid != None:
            l_SQL = 'SELECT * FROM rights WHERE recid = ?'
            l_params = (self.recid, )
            l_cursor = p_db_cnx.execute(l_SQL, l_params)
            l_row = l_cursor.fetchone()
            if l_row is None:
                raise exc.CorruptDataBaseError(self.__class__, self.code, self.recid)

            l_object_fields = (self.code, self.granted_value, self.protected_value)
            l_db_fields = (l_row['code'], l_row['granted_value'], l_row['protected_value'])
            if l_object_fields == l_db_fields:
                print('Nada que hacer')
                return None     #Nada para hacer.  No hay cambios

            #Hay cambios
            if l_row['version_from_recid'] != p_vrs_recid:
                l_SQL = ('UPDATE rights'
                        +'   SET version_to_recid = ?'
                        +' WHERE recid = ?')
                l_params = (p_vrs_recid, self.recid) #Desactivo valores anteriores
                p_db_cnx.execute(l_SQL, l_params)
                print('fin antiguo valor: ' + l_SQL)
                self.recid = None #Seteo a None para forzar insert mas abajo
            else:
                l_SQL = ( 'UPDATE rights '
                        + '   SET code = ? ,'
                        +       ' granted_value = ? ,'
                        +       ' protected_value = ? ,'
                        +       ' application_recid = ? ,'
                        +       'version_from_recid = ?'
                        + 'WHERE recid = ?' )
                l_params = (self.code, self.granted_value
                        , self.protected_value, self.__app._Applicationrecid
                        , p_vrs_recid, self.recid)
                p_db_cnx.execute(l_SQL, l_params)
                print('modifico sobre valor actual %s %s' % (self.granted_value, self.protected_value))

        #Repregunta sin usar ELSE.  recid pudo cambiar
        if self.recid == None:
            l_SQL = ( 'INSERT INTO rights'
                    +           ' (code, granted_value, protected_value,'
                    +            ' application_recid, version_from_recid)'
                    +     ' VALUES (?,?,?,?,?)' )
            l_params = (self.code, self.granted_value,
                    self.protected_value, self.__app._Applicationrecid,
                    p_vrs_recid)
            p_db_cnx.execute(l_SQL, l_params) #inserto el nuevo registro
            print('Creo nuevo valor')

            l_SQL = ( ' SELECT recid '
                    + '    FROM rights '
                    + '   WHERE code = ? '
                    + '     AND version_from_recid = ?' )
            l_params = (self.code, p_vrs_recid)
            l_cursor = p_db_cnx.execute(l_SQL, l_params) #recupero el nuevo reid
            l_row = l_cursor.fetchone()
            if l_row == None:
                raise exc.CorruptDataBaseError(self.__class__, self.code, self.recid)
            self.recid = l_row["recid"]
            print (l_row[0])

        p_db_cnx.commit()

    def __str__(self):
        l_obj = (' Objeto %s: Code=[%s] - granted_value=[%s] - '
                + 'protected_value=[%s]'
                + 'recid=[%d]') % (self.__class__,
                    self.code, self.granted_value, self.protected_value,
                    self.recid)
        return l_obj


