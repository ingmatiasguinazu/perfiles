

# -*- coding: utf-8 -*-


from . import *


G_ENTITIES = ['RightRow', 'Right',
              'ApplicationRow', 'Application'
              ]


def get_select_SQL(p_entity):
    """ Calcula y devuelve SQL Select que permite acceder a Entidades vigentes.

    Parametros:
        -> p_entity:  Nombre de la entidad para la cual se desea la SQL Select
    """
    return (            'SELECT mst.*, row.*, mst.recid as recid_a, '
            +                  'row.recid as recid_b'
            +            ' FROM {} AS mst'.format(p_entity)
            +      ' INNER JOIN {}Row AS row'.format(p_entity)
            +                   ' ON row.{} = '.format(p_entity.lower())
            +                                     ' mst.recid'
            +      ' INNER JOIN Version AS vrs_mst_from'
            +                   ' ON vrs_mst_from.recid ='
            +                                     ' mst.version_from'
            +      ' INNER JOIN Version AS vrs_row_from'
            +                   ' ON vrs_row_from.recid ='
            +                                     ' row.version_from'
            + ' LEFT OUTER JOIN Version vrs_mst_to'
            +                   ' ON vrs_mst_to.recid = mst.version_to'
            + ' LEFT OUTER JOIN Version vrs_row_to'
            +                   ' ON vrs_row_to.recid = row.version_to'
            +           ' WHERE vrs_mst_from.seq <= ?'
            +             ' AND ( vrs_mst_to.seq > ? OR '
            +                                   'vrs_mst_to.seq is NULL )'
            +             ' AND vrs_row_from.seq <= ?'
            +             ' AND ( vrs_row_to.seq > ? OR '
            +                                   'vrs_row_to.seq is NULL )')


class Version():
    """ Versions

    Atributos:
        __applications
    """

    def __init__(self, p_app_file, p_seq, p_summary, p_recid=None):
        """ Instancia un nuevo objeto.

        Parametros:
            p_app_file: Obligatorio. Referencia a objeto AppFile.
            p_seq: Obligatorio.  Secuencia de la version.  Se espera entero
            p_summary:  Obligatorio.  Texto descriptivo de la version.
            p_recid: Opcionial.  Identificador unico en la DB de persistencia.
                     Se espera entero.  Si ausente => None
        """

        # Validaciones a la creacion
        if p_seq in p_app_file.versions:
            raise exc.KeyAlreadyExistsError()

        # Inicializo propiedades
        self.app_file = p_app_file
        self.seq = p_seq
        self.summary = p_summary
        self.effective_date = None
        self.recid = p_recid

        # Me inicializo en componentes con relaciones OneToMenuMe
        self.app_file.versions[p_seq] = self

    def delete(self):
        """Elimina en Archivo DB a la Version y sus modificaciones.
        """

        l_db_cnx = self.app_file.db_cnx
        if l_db_cnx is None:
            raise NotFileSelectedError()

        self.undo_changes()

        if self.recid is not None:
            l_SQL = ('DELETE FROM Version'
                     + ' WHERE recid = ?')
            l_params = (self.recid,)
            l_db_cnx.execute(l_SQL, l_params)
            l_db_cnx.commit()

        del self.app_file.versions[self.seq]

    def get_schema(self):
        """Devuelve el esquema vigente a esta version.
        """
        l_schema = Schema(self)

        l_db_cnx = self.app_file.db_cnx
        l_seq = self.seq
        if l_db_cnx == None:
            return l_schema

        l_entities = dict()
        ##############################################
        #           CARGO APLICACIONES
        ##############################################
        l_entity = 'Application'
        l_entities[l_entity] = dict()
        l_SQL = get_select_SQL(l_entity)
        l_params = (l_seq, l_seq, l_seq, l_seq)
        l_rows = l_db_cnx.execute(l_SQL, l_params)
        for l_row in l_rows:
            l_entities[l_entity][l_row['recid']] = (
                Application(self, l_schema, l_row['code'],
                            l_row['name'], l_row['recid_a'], l_row['recid_b']))
            print(l_entities[l_entity][l_row['recid']])

        ##############################################
        #           CARGO RIGHTS
        ##############################################
        l_entity = 'Right'
        l_entities[l_entity] = dict()
        l_SQL = get_select_SQL(l_entity)
        l_params = (l_seq, l_seq, l_seq, l_seq)
        l_rows = l_db_cnx.execute(l_SQL, l_params)
        for l_row in l_rows:
            l_app = l_entities['Application'][l_row['application']]
            l_entities[l_entity][l_row['recid']] = (
                Right(self, l_app, l_row['code'], l_row['granted_value'],
                      l_row['protected_value'], l_row['recid_a'],
                      l_row['recid_b']))
            print(l_entities[l_entity][l_row['recid']])

        return l_schema

    def reset_as_new(self):
        """ Setea la version como version de trabajo
        """
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

    def has_unsaved_changes(self):
        """Indica si existen cambios sin grabar.
        """
        if self.recid == None:
            return True

        l_db_cnx = self.app_file.db_cnx
        if l_db_cnx == None:
            raise NotFileSelectedError()

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

        return False  # No hay cambios

    def has_changes(self):
        """ Indica si la version registra cambios en el Archivo DB
        """

        l_db_cnx = self.app_file.db_cnx
        if l_db_cnx is None:
            raise NotFileSelectedError()

        if self.recid is None:
            return False

        for l_entity in G_ENTITIES:
            #  Elimino registros creados con la version
            l_SQL = ('SELECT * FROM {}'.format(l_entity)
                        + ' WHERE version_from = ?'
                        +    ' OR version_to = ?')
            l_params = (self.recid,self.recid)
            l_rows = l_db_cnx.execute(l_SQL, l_params)
            for l_row in l_rows:
                return True

        return False

    def undo_changes(self):
        """Elimina en Archivo DB los cambios asociados a la version.
        """

        l_db_cnx = self.app_file.db_cnx
        if l_db_cnx is None:
            raise NotFileSelectedError()

        for l_entity in G_ENTITIES:
            #  Elimino registros creados con la version
            l_SQL = ('DELETE FROM {}'.format(l_entity)
                        + ' WHERE version_from = ?')
            l_params = (self.recid,)
            l_db_cnx.execute(l_SQL, l_params)

            #  Activo registros suprimidos con la version
            l_SQL = ('UPDATE {}'.format(l_entity)
                    +'   SET version_to = null'
                    +' WHERE version_to = ?')
            l_params = (self.recid,)
            l_db_cnx.execute(l_SQL, l_params)

        l_db_cnx.commit()

    def __str__(self):
        l_text = '"Version" '
        l_text = l_text + ' [seq]=%i' % (self.seq,)
        l_text = l_text + ' [summaty]=%s' % (self.summary,)
        l_text = l_text + ' [effective_date]=%s' % (self.effective_date,)
        return l_text


