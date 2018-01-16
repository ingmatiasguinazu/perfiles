""" Implementa la Entidad Persistente de la Aplicación

CLASES
======
- EntityField: Campo de la entidad
- Entity: Entidad persistente

EXCEPCIONES
===========
- EntityFieldNameNotInformedError: Nombre de campo no informado al instanciar
una Entity
- KeyAlreadyExistsError: Primary Key ya existente.  Imposible instanciar Entity
- CorruptDataBaseError: La entidad hace uan referencia a elemento persistente
no encontrado en DB
- NotFileSelectedError: La operacion requiere estar tener un archivo abierto

FUNCIONES
=========
- get_text_key(p_pk):  Genera la cadena de Primary Key asociada a la lista
Fileds solicitada

CONSTANTES
==========
- G_LOCAL_ATTR:  Indica los atributos de la entidad que no son tenidos en
cuenta al momento de ejecutar la grabación.  (Atributos no presentes en el
diseño de la DB)
- G_NOT_PERMANENT:  Indica las Clases que no son persistentes (No se graban en
la DB)

"""
# -*- coding: utf-8 -*-

from .exc import *
import operator


G_LOCAL_ATTR = ('objid', 'recid', 'version', 'deleted', 'schema', 'pk')
G_NOT_PERMANENT = ('Schema', )


def get_text_key(p_pk):

    l_key = ''
    for l_field in p_pk:
        if isinstance(l_field, Entity):
            l_field_key = l_field.objid
        elif l_field is not None:
            l_field_key = l_field
        else:
            l_field_key = 'null'
        l_key = '{}[{}]'.format(l_key, l_field_key)
    return l_key


class EntityField():
    """Field utilizado para crear atributos al instanciar un Entity.

    Atributos:
        name:  Nombre del Field
        value:  Valor del Field
        pk: Indicador de indice unico
        otm:  Indicador de campo oneToMeny

    Métodos:
        Ninguno

    Información adicional:
        Al instanciar un Entity, se recibe una lista EntityFields.  Por
        cada EntityField en la lista, se creará un atributo en el Entity
        que se está instanciando.
    """

    def __init__(self, p_name, p_value=None, p_pk=False, p_otm=False):
        """ Instancia el objeto.

        Parametros:
            p_name: Obligatorio. Se espera string.
                    Cuando no es OneToMany (p_opt == False) -> Se espera cadena
                        no vacia que se utilizara como nombre del atributo
                    Cuando es OneToMany (p_opt == True) -> Se espera cadena,
                        puede ser vacia, y se utilizara como prefijo de
                        diccionario (ver __init__ de Entity)
            p_value: Opcional. Valor del atributo.
                     Cuando no es OneToMany ->  Se espera un tipo básico
                        (cadena, numero, lógico) o un objeto Entity.
                     Cuando es OneToMany -> se espera una cadena con el nombre
                        de la clase Entity relacionada.
                     Si ausente => None
            p_pk: Opcional. Indicador de indice unico. Se espera lógico.
                     Si ausente => False
            p_otm: Opcional:  Indicador de campo oneToMeny. Se espera lógico
                     Si ausente => False
        """
        self.name = p_name
        self.value = p_value
        self.pk = p_pk
        self.otm = p_otm


class Entity():
    """ Entidad que compone el Model de la aplicación

    Atributos:
        objid:  Identificar unico de la entidad
        version:  Version a partir de la cual se instancia
        recid:  Identificador unico en la DB de persistencia
        deleted: Indicador de entidad eliminada
        pk:  Valor texto de la clave primaria (Clave única)

    Métodos:
        reset_as_new: Restablece la entidad a estado nueva
        has_unsaved_changes: Indica si existen modificaciones no grabadas
        save: Graba las modificaciones en el archivo DB de persistencia
        delete:  Elimina la entidad (Eliminación a gragar en archivo DB)
        destroy:  Elimina la entidad (Eliminación a no grabar en archivo DB)
        is_gui_visible:  Indica si la entidad es visible en la GUI
    """

    # Atributos de clase
    __objid = 0
    __entities = {}
    __unique_indexes = {}
    __sangria = ''

    def __init__(self, p_vrs, p_row, p_recid=None, p_reinit=False):
        """ Instancia el objeto.

        Parametros:
            p_vrs: Obligatorio. Version utilizada para crear la Entidad.
            p_row: Obligatorio. Lista de EntityFields que describen la Entidad
            p_recid: Opcionial.  Identificador unico en la DB de persistencia.
                     Se espera entero.  Si ausente => None
            p_reinit: Opcional.  Indicador de reunicio completo de Entidades.
                      Se espera lógico.  Si ausente => False

        Reglas de nombres para atributos dinámicos
        ------------------------------------------

        Por cada EntityField recibido en p_row, se crea dinamicamente un
        atributo de instancia en la Entidad.

        Atributos para EntityField OneToMany (EntityField.otm == True)
            Crea un diccionatio en la Entidad
            El nombre del diccionario es [name]_[class]s donde
                [name] es el valor indicado en EntityField.name
                [class] es el nombre de la Clase Entity informada
                        en EntityField.value
                Ejemplo:  Un EntityField OneToMany con name='from' y
                          value='Rigth' creara un atributo from_rights

        Atributos para EntityField no OneToMany (EntityField.otm == False)
            Crea un atributo con el nombre indicado en EntityField.name

        Reglas de consistencia
        ----------------------

        Primary Key:
            Para cada EntityField recibido en p_row con marca de pk se verifica
            que no exista previamente una entidad con la misma clave.  En caso
            de existencia se genera la excepción KeyAlreadyExistsError

        MenyToOne:
            Para cada EntityField recibido en p_row donde el valor sea un
            objeto Entity, la entidad instanciada se auto agrega en el
            diccionario de asociado de dicho EntityField.

        """

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
            if l_field.pk:
                l_pk.append(l_field.value)

        # Verifico clave unica
        self.pk = None
        if len(l_pk) > 0:
            self.pk = get_text_key(l_pk)

        if self.pk is not None:
            l_dict = self.__class__.__name__.lower()
            if l_dict not in Entity.__unique_indexes:
                Entity.__unique_indexes[l_dict] = {}
            if self.pk in Entity.__unique_indexes[l_dict]:
                raise KeyAlreadyExistsError(self)
            Entity.__unique_indexes[l_dict][self.pk] = self

        # Me anexo a colección general
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
        """ Restablece la entidad a estado nueva.

        """
        # one_to_many: reseteo a todos como nuevos
        self.__do_for_otm((lambda x: x.reset_as_new()))

        self.recid = None
        if self.deleted:
            self.delete()

    def has_unsaved_changes(self):
        """Verifica si existen cambios en la Entidad no grabadas aun en la BD.

        Retorno TRUE:  Existen cambios no guardados aun
        Retorno FALSE:  No existen cambios pendientes de grabar

        """
        if self.__class__.__name__ not in G_NOT_PERMANENT:

            # Creado del esquema
            if self.recid is None:
                return True

            l_db_cnx = self.version.app_file.db_cnx

            # Objeto diferente a DB
            if self.__class__.__name__ not in G_NOT_PERMANENT:
                l_SQL = 'SELECT * FROM {} WHERE recid = ?'.format(
                        self.__class__.__name__)
                l_params = (self.recid, )
                l_row = l_db_cnx.execute(l_SQL, l_params).fetchone()
                if l_row is None:
                    raise CorruptDataBaseError()

                if self.deleted and l_row['version_to'] is None:
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

        return False  # No hay cambios

    def __do_for_otm(self, p_func, p_class=None):
        """ Aplica metodo solicitado a entidades OneToMenu relacionadas

        Parametros:
            p_fun -> Funcion lambda que indica el metodo a aplicar
            p_class -> Filtra entidades otm que sean de esta clase.  Si None
            no aplica filtro y elejuta el metodo a toda las Entities otm
        """
        for l_field in self.__dict__.keys():
            if (l_field not in G_LOCAL_ATTR
                    and isinstance(self.__dict__[l_field], dict)):
                l_dict = dict()
                l_dict.update(self.__dict__[l_field])
                for l_otm in l_dict.values():
                    if isinstance(l_otm, Entity):
                        if (p_class is None
                            or Entity.__class__.__name__ == p_class):
                            p_func(l_otm)

    def save(self):
        """Registra las modificaciones permanentemente
        """

        # Recupero valores de la DB
        l_row = None
        if self.recid is not None:

            l_db_cnx = self.version.app_file.db_cnx
            if l_db_cnx is None:
                raise NotFileSelectedError()

            l_SQL = 'SELECT * FROM {} WHERE recid = ?'.format(
                    self.__class__.__name__)
            l_params = (self.recid, )
            l_row = l_db_cnx.execute(l_SQL, l_params).fetchone()

            if l_row is None:
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
                    # Creo campos UPDATE_SQL
                    if l_row is None:
                        l_changed = True
                    elif l_value != l_row[l_field]:
                        l_changed = True
                        if l_upd_fields != 'SET ':
                            l_upd_fields = l_upd_fields + ','
                        l_upd_fields = l_upd_fields + l_field + ' = ?'
                        l_upd_values.append(l_value)
                elif l_row is not None:
                    if l_row['version_to'] is None:
                        l_changed = True

        # debug
        print('==> Save {}({})'.format(self.__class__.__name__, self.objid))
        print('==-->         l_changed = {}'.format(l_changed))
        print('==-->      l_ins_fields = {}'.format(l_ins_fields))
        print('==--> l_ins_values_text = {}'.format(l_ins_values_text))
        print('==-->      l_ins_values = {}'.format(l_ins_values))
        print('==-->      l_upd_fields = {}'.format(l_upd_fields))
        print('==-->      l_upd_values = {}'.format(l_upd_values))

        # Grabo los OTM antes de grabarme en caso de delete
        if self.deleted:
            self.__do_for_otm((lambda x: x.save()))

        # Grabo los OTM antes de grabarme a mi mismo, en caso de delete
        if l_changed and self.__class__.__name__ not in G_NOT_PERMANENT:

            l_db_cnx = self.version.app_file.db_cnx
            if l_db_cnx is None:
                raise NotFileSelectedError()

            self.version.save()

            if l_ins_fields != '(':
                l_ins_fields = l_ins_fields + ', '
                l_ins_values_text = l_ins_values_text + ', '
            l_ins_fields = l_ins_fields + 'version_from)'
            l_ins_values_text = l_ins_values_text + '?)'
            l_ins_values.append(self.version.recid)

            if l_row is not None:

                if (self.deleted and
                        l_row['version_from'] == self.version.recid):
                    l_SQL = ('DELETE FROM {} WHERE recid = ?'.format(
                                self.__class__.__name__))
                    l_params = (self.recid, )  # Desactivo valores
                    # debug
                    print('Ejecuta SQL: {} con parametros {}'.format(
                        l_SQL, l_params))
                    l_db_cnx.execute(l_SQL, l_params)
                    self.recid = None
                elif l_row['version_from'] != self.version.recid:
                    l_SQL = ('UPDATE {} '.format(self.__class__.__name__)
                             + '   SET version_to = ?'
                             + ' WHERE recid = ?')
                    # Desactivo valores
                    l_params = (self.version.recid, self.recid)
                    # debug
                    print('Ejecuta SQL: {} con parametros {}'.format(
                        l_SQL, l_params))
                    l_db_cnx.execute(l_SQL, l_params)
                    self.recid = None
                else:
                    l_SQL = ('UPDATE {} {} WHERE recid = ?'.format(
                                self.__class__.__name__, l_upd_fields))
                    l_params = l_upd_values
                    l_params.append(self.recid)
                    # debug
                    print('Ejecuta SQL: {} con parametros {}'.format(
                        l_SQL, l_params))
                    l_db_cnx.execute(l_SQL, l_params)

            if self.recid is None and not self.deleted:
                l_SQL = ('INSERT INTO {} {} VALUES {}'.format(
                    self.__class__.__name__, l_ins_fields, l_ins_values_text))
                l_params = l_ins_values
                l_cursor = l_db_cnx.cursor()
                # debug
                print('Ejecuta SQL: {} con parametros {}'.format(
                    l_SQL, l_params))
                l_cursor.execute(l_SQL, l_params)  # Inserto el nuevo registro
                self.recid = l_cursor.lastrowid

            l_db_cnx.commit()

        if self.deleted:
            # Me eliminto del esquema
            self.delete()
        else:
            # Grabo los OTM despues de grabarme, en que no sea delete
            self.__do_for_otm((lambda x: x.save()))

    def delete(self):
        """ Se elimina (Eliminación a grabar en archivo DB de persistencia)
        """

        # one_to_many: Elimino los oneToMeny
        self.__do_for_otm((lambda x: x.delete()))

        self.deleted = True

        if self.recid is None:

            # Me elimino de la colección General
            del Entity.__entities[self.objid]

            # Me elimino de los indices primarios
            if self.pk is not None:
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

    def destroy(self):
        """ Se elimina (Eliminación a no grabar en archivo DB de persistencia)
        """

        self.reset_as_new()
        self.delete()

    def is_gui_visible(self):
        """Indica si es visible en la GUI
        """
        return False

    def get_entities(self):
        """ Devuelve lista con todas las entidades
        """
        return ([l_value for l_key, l_value in sorted(
            Entity.__entities.items(), key=operator.itemgetter(0))])

    def get_entity(self, p_key):
        """ Devuelve una entidad.

        Parametros:
            p_key -> Puede ser un objid o una lista de valores que forman la pk
        """
        if isinstance(p_key, list):
            l_pk = get_text_key(p_key)
            l_index = self.__class__.__name__.lower()
            if l_pk in Entity.__unique_indexes[l_index]:
                return Entity.__unique_indexes[l_index][l_pk]
        else:
            if p_key in Entity.__entities:
                return Entity.__entities[p_key]
        return None

    def get_entities_statistic(self):
        """ Entrega estadisticas del modelo

        Parametros:  Ninguno
        """
        l_ret = ''
        l_ac = 0
        l_first_objid = 999999
        l_last_objid = 0
        for l_entity in Entity.__entities.values():
            if l_entity.objid < l_first_objid:
                l_first_objid = l_entity.objid
            if l_entity.objid > l_last_objid:
                l_last_objid = l_entity.objid
            l_ac += 1
        l_ret = ('ESTADISTICAS ENTITIES:  [Total Entidades: {}] '
                 + '[Primer objid: {}] [Ultimo objid: {}]')
        return l_ret.format(l_ac, l_first_objid, l_last_objid)

    def __str__(self):
        """ Devuelve cadena con la información de la Entidad
        """
        l_sangria = Entity.__sangria
        Entity.__sangria = Entity.__sangria + '  '
        l_ret = '\n{}==> {}({}) <=='.format(
            Entity.__sangria, self.__class__.__name__, self.objid)
        for l_attr in self.__dict__.keys():
            if (not isinstance(self.__dict__[l_attr], dict)
                    and not isinstance(self.__dict__[l_attr], Entity)):
                l_ret = l_ret + '\n' + '{}{} = {}'.format(
                    Entity.__sangria, l_attr, self.__dict__[l_attr])
            elif isinstance(self.__dict__[l_attr], Entity):
                l_ret = l_ret + '\n{}{}({}) \n {}'.format(
                        Entity.__sangria,
                        self.__dict__[l_attr].__class__.__name__,
                        self.__dict__[l_attr].objid,
                        self.__dict__[l_attr]
                        )
        Entity.__sangria = l_sangria
        return l_ret
