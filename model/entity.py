
# -*- coding: utf-8 -*-

from . import * 
import importlib as il

G_LOCAL_ATTR = ('objid', 'recid', 'version', 'deleted', 'schema','pk')
G_NOT_PERMANENT = ('Schema',)

def get_text_key(p_pk):

    l_key = ''
    for l_field in p_pk:
        if isinstance(l_field, Entity):
            l_field_key = l_field.objid
        elif l_field != None:
            l_field_key = l_field
        else:
            l_field_key = 'null'
        l_key = '{}[{}]'.format(l_key, l_field_key)
    return l_key


class EntityField():
    '''
        Field utilizado para crear dinamicamente atributos de una Entity

        Atributos:
        --> p_name:  Nombre logico del field
        --> p_value:  Valor del atr--> p_pk: Indicador de indice unico 
        --> p_otm:  Indicador de campo oneToMeny


        Regla de creacion y nombrado de atributos para fields con otm:
        --> En <name> se debe recibir prefijo modificador
        --> En <value> se debe recibir el nombre de la clase Entity relacionada
        --> Por cada field otm se creara un atributo diccionario llamado
            [<name>_]<value>s
        --> Ejemplo:
                Al instanciar un objeto x de clase Application, 
                conteniendo un field con <name>=from & <value>=Right
                se creara un atributo
                    x.from_rights = {}
        
        Regla de creacion y nombrado de atributos Entity:
        -->  Los atributos tipo entity se consideran como relaciones MenyToOne
        -->  En <name> se debe recibir el nombre desdeado para el atributo
        -->  En <value> el objeto entity relaciona
        -->  Por cada field que sea una instanacia de Entity, se accedera
             a ese objeto para autoagregarse en el diccionario correspondiente
        -->  Ejemplo:
                Si se instancia un objeto x Right, conteniendo un field 
                <name>=from, <value>=y (Application)
                se creara un atributo x.application_from
                x se autoagregara al diccionario y.from_rights
    '''

    def __init__(self, p_name, p_value=None, p_pk=False, p_otm=False, 
            p_mto_pref=''):
        self.name = p_name
        self.value = p_value
        self.pk = p_pk
        self.otm = p_otm
        self.mto_pref = p_mto_pref


class Entity():

    __objid = 0
    __entities = {}
    __unique_indexes = {}
    __sangria = ''

    def __init__(self, p_vrs, p_row, p_recid = None, p_reinit=False):
        ''' Contructor 
        -> p_vrs = vesrion con la que se instancia la entidad
        -> p_row = coleccion de EntityFields
        '''


        if p_reinit:
            Entity.__objid = 0
            Entity.__entities.clear()
            Entity.__unique_indexes.clear()
        

        # Me identifico
        Entity.__objid = Entity.__objid + 1
        self.objid = Entity.__objid
        self.version = p_vrs
        self.recid = p_recid
        self.deleted = False

        # Creo mis atributos de entidad
        l_pk = list()
        for l_field in p_row:
            if isinstance(l_field.value, Entity):
                l_name = (l_field.value.__class__.__name__.lower())
            else:
                l_name = l_field.name.lower()
            l_value = l_field.value
            if len(l_name) > 0 and l_field.otm:
                l_name = l_name + '_' 
            if l_field.otm:
                l_name = l_name + l_field.value.lower() + 's'
                l_value = dict()
            if len(l_name) == 0:
                raise EntityFieldNameNotInformedError()
            setattr(self, l_name, l_value)
            if l_field.pk == True:
                l_pk.append(l_field.value)

        # Verifico clave unica
        self.pk = None
        if len(l_pk) > 0:
            self.pk = get_text_key(l_pk)

        if self.pk != None:
            l_dict = self.__class__.__name__.lower()
            if l_dict not in Entity.__unique_indexes:
                Entity.__unique_indexes[l_dict] = {}
            if self.pk in Entity.__unique_indexes[l_dict]:
                raise KeyAlreadyExistsError(self)
            Entity.__unique_indexes[l_dict][self.pk] = self

        # Me anexo a colección general
        if self.objid == 2:
            print('Creo el objid=2 en entities')
        Entity.__entities[self.objid] = self

        for l_field in p_row:
            # Me inicializo en entidades parentes MenyToOne 
            if isinstance(l_field.value, Entity):
                l_dict_name = ''
                if len(l_field.name) > 0:
                    l_dict_name = '{}_'.format(l_field.name)
                l_dict_name = (l_dict_name + self.__class__.__name__.lower() 
                        + 's')
                getattr(l_field.value, l_dict_name)[self.objid] = self
                
    def reset_as_new(self):
        ''' Se resetea como nuevo.  Blanquea recid propio y oneToMeny '''

        #one_to_many: reseteo a todos como nuevos
        for l_self_attr in self.__dict__.values():
            if isinstance(l_self_attr, dict):
                l_dict = dict()
                l_dict.update(l_self_attr)
                for l_otm in l_dict.values():
                    if isinstance(l_otm, Entity):
                        l_otm.reset_as_new()
        self.recid = None
        if self.deleted:
            self.delete()


    def has_unsaved_changes(self):
        "Indica si existen cambios sin grabar."
        
        if self.__class__.__name__ not in G_NOT_PERMANENT:

            # Creado del esquema
            if self.recid == None:
                return True 

            l_db_cnx = self.version.app_file.db_cnx

            # Objeto diferente a DB
            if self.__class__.__name__ not in G_NOT_PERMANENT:
                l_SQL = 'SELECT * FROM {} WHERE recid = ?'.format(
                        self.__class__.__name__)
                l_params = (self.recid, )
                l_row = l_db_cnx.execute(l_SQL, l_params).fetchone()
                if l_row == None:
                    raise CorruptDataBaseError()

                if self.deleted and l_row['version_to'] == None:
                    return True

                for l_field in self.__dict__.keys():
                    if (l_field not in G_LOCAL_ATTR 
                            and not isinstance(self.__dict__[l_field], dict)):
                        if isinstance(self.__dict__[l_field], Entity):
                            l_value = self.__dict__[l_field].recid
                        else:
                            l_value = self.__dict__[l_field]
                        if l_value != l_row[l_field]:
                            return True

        # Aglun OneToMany diferente
        for l_field in self.__dict__.keys():
            if (l_field not in G_LOCAL_ATTR
                    and isinstance(self.__dict__[l_field], dict)):
                for l_otm in self.__dict__[l_field].values():
                    if isinstance(l_otm, Entity):
                        if l_otm.has_unsaved_changes():
                            return True
 
        return False #No hay cambios


    def save(self):
        '''Registra las modificaciones permanentemente'''

        # Recupero valores de la DB
        l_row = None
        if self.recid != None:

            l_db_cnx = self.version.app_file.db_cnx
            if l_db_cnx == None:
                raise NotFileSelectedError()

            l_SQL = 'SELECT * FROM {} WHERE recid = ?'.format(
                    self.__class__.__name__)
            l_params = (self.recid, )
            l_row = l_db_cnx.execute(l_SQL, l_params).fetchone()

            if l_row == None:
                raise CorruptDataBaseError()

        # Recorro atributos
        l_ins_fields = '('
        l_ins_values_text = '('
        l_ins_values = list()
        l_upd_fields = 'SET '
        l_upd_values = list()
        l_changed = False
        for l_field in self.__dict__.keys():
            if (l_field not in G_LOCAL_ATTR 
                    and not isinstance(self.__dict__[l_field], dict)):
                if isinstance(self.__dict__[l_field], Entity):
                    l_value = self.__dict__[l_field].recid
                else:
                    l_value = self.__dict__[l_field]

                # Creo campos INSERT_SQL
                if l_ins_fields != '(':
                    l_ins_fields = l_ins_fields + ', '
                    l_ins_values_text = l_ins_values_text + ', '
                l_ins_fields = l_ins_fields + l_field
                l_ins_values_text = l_ins_values_text + '?'
                l_ins_values.append(l_value)

                if not self.deleted:
                    if l_row == None:
                        l_changed = True
                    elif l_value != l_row[l_field]:
                        l_changed = True
                        if l_upd_fields != 'SET ':
                            l_upd_fields = l_upd_fields + ','
                        l_upd_fields = l_upd_fields + l_field + ' = ?'
                        l_upd_values.append(l_value)
                elif l_row != None:
                    if l_row['version_to'] == None:
                        l_changed = True


        print('==> Hago save {}({})'.format(self.__class__.__name__, self.objid))
        print('==> Termino comparación l_changed = {}'.format(l_changed))
        print('==>                  l_ins_fields = {}'.format(l_ins_fields))
        print('==>             l_ins_values_text = {}'.format(l_ins_values_text))
        print('==>                  l_ins_values = {}'.format(l_ins_values))
        print('==>                  l_upd_fields = {}'.format(l_upd_fields))
        print('==>                  l_upd_values = {}'.format(l_upd_values))

        if l_changed and self.__class__.__name__ not in G_NOT_PERMANENT:

            l_db_cnx = self.version.app_file.db_cnx
            if l_db_cnx == None:
                raise NotFileSelectedError()

            self.version.save()

            if l_ins_fields != '(':
                l_ins_fields = l_ins_fields + ', '
                l_ins_values_text = l_ins_values_text + ', '
            l_ins_fields = l_ins_fields + 'version_from)'
            l_ins_values_text = l_ins_values_text + '?)'
            l_ins_values.append(self.version.recid)

            if l_row != None:

                if (self.deleted and  
                        l_row['version_from'] == self.version.recid):
                    l_SQL = ('DELETE FROM {} WHERE recid = ?'.format(
                                self.__class__.__name__))
                    l_params = (self.recid, ) #Desactivo valores 
                    print ('Ejecuta SQL: {} con parametros {}'.format(l_SQL, l_params))
                    l_db_cnx.execute(l_SQL, l_params)
                    self.recid = None


                elif l_row['version_from'] != self.version.recid:
                    l_SQL = ('UPDATE {} '.format(self.__class__.__name__) 
                            +'   SET version_to = ?'
                            +' WHERE recid = ?')
                    # Desactivo valores
                    l_params = (self.version.recid, self.recid)
                    print ('Ejecuta SQL: {} con parametros {}'.format(l_SQL, l_params))
                    l_db_cnx.execute(l_SQL, l_params)
                    self.recid = None

                else:
                    l_SQL = ( 'UPDATE {} {} WHERE recid = ?'.format(
                                self.__class__.__name__,l_upd_fields))
                    l_params = l_upd_values
                    l_params.append(self.recid)
                    print ('Ejecuta SQL: {} con parametros {}'.format(l_SQL, l_params))
                    l_db_cnx.execute(l_SQL, l_params)

            if self.recid == None and not self.deleted:
                l_SQL = ( 'INSERT INTO {} {} VALUES {}'.format(
                    self.__class__.__name__, l_ins_fields, l_ins_values_text) )
                l_params = l_ins_values
                l_cursor = l_db_cnx.cursor()
                print ('Ejecuta SQL: {} con parametros {}'.format(l_SQL, l_params))
                l_cursor.execute(l_SQL, l_params) #inserto el nuevo registro
                self.recid = l_cursor.lastrowid

            l_db_cnx.commit()

        # Me eliminto del esquema y de las entidades menyToOne
        if self.deleted:
            print ('Me elimino de la colección de Entidades.  Tengo RECID {}'.format(self.recid))
            self.delete()


        # Grabo todos los oneToMeny
        for l_field in self.__dict__.keys():
            if (l_field not in G_LOCAL_ATTR
                    and isinstance(self.__dict__[l_field], dict)):
                l_dict = dict()
                l_dict.update(self.__dict__[l_field])
                for l_otm in l_dict.values():
                    if isinstance(l_otm, Entity):
                        l_otm.save()


    def delete(self):
        ''' Me elimino del esquema '''

        #one_to_many: Elimino los oneToMeny
        for l_self_attr in self.__dict__.values():
            if isinstance(l_self_attr, dict):
                l_dict = dict()
                l_dict.update(l_self_attr)
                for l_otm in l_dict.values():
                    if isinstance(l_otm, Entity):
                        l_otm.delete()
        
        self.deleted = True


        if self.recid == None:

            # Me elimino de la colección General
            del Entity.__entities[self.objid]

            # Me elimino de los indices primarios
            if self.pk != None:
                l_dict = self.__class__.__name__.lower()
                if l_dict in Entity.__unique_indexes:
                    if self.pk in Entity.__unique_indexes[l_dict]:
                        del Entity.__unique_indexes[l_dict][self.pk]

            # Me elimino de los menyToOne
            for l_parent_attr in self.__dict__.values():
                if isinstance(l_parent_attr, Entity):
                    for l_mto_dict in l_parent_attr.__dict__.values():
                        if isinstance(l_mto_dict, dict):
                            if self.objid in l_mto_dict:
                                del l_mto_dict[self.objid]

    def is_gui_visible(self):
        return False

    def get_entities(self):
        ''' devuelve la colección de entidades '''
        return Entity.__entities.values()

    def get_entity(self, p_key):
        ''' devuelve una entidad '''
        if isinstance(p_key, list):
            l_pk = get_text_key(p_key)
            l_index = self.__class__.__name__.lower()
            if l_pk in Entity.__unique_indexes[l_dict]:
                return Entity.__unique_indexes[l_dict][l_pk]
        else:
            if p_key in Entity.__entities:
                return Entity.__entities[p_key]
        return None
    
    def __str__(self):
        l_sangria = Entity.__sangria
        Entity.__sangria = Entity.__sangria + '  '
        l_ret = '\n{}==> {}({}) <=='.format(Entity.__sangria,
                self.__class__.__name__, self.objid)
        for l_attr in self.__dict__.keys():
            if ( not isinstance(self.__dict__[l_attr], dict)
                    and not isinstance(self.__dict__[l_attr], Entity)):
                l_ret = l_ret + '\n' + '{}{} = {}'.format(Entity.__sangria,
                        l_attr, self.__dict__[l_attr])
            elif isinstance(self.__dict__[l_attr], Entity):
                l_ret = l_ret + '\n{}{}({}) \n {}'.format(
                        Entity.__sangria,
                        self.__dict__[l_attr].__class__.__name__, 
                        self.__dict__[l_attr].objid, 
                        self.__dict__[l_attr] 
                        )
        Entity.__sangria = l_sangria
        return l_ret






