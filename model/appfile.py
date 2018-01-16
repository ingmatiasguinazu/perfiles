""" Implementa el Archivo de la Applicación

CLASES
======
- AppFile: Archivo de la aplicación

"""
# -*- coding: utf-8 -*-

import os.path
import datetime as dt

from .dbfile import DBFile
from . import *


class AppFile:
    """Archivo de la applicación.

    Atributos
        db_cnx:  Conexion al archivo DB
        db_file:  Nombre completo del archivo DB
        versions:  diccionario de versiones (clave version.seq)

    Métodos:
        open: Abre un archivo DB carga sus versiones y esquema de trabajo
        saveas: Graba el esquema de trabajo en un nuevo archivo
        discare_unsaved_changes:  descarta cambios no guardados del esquema
        upgrade_version:  finaliza la version de trabajo e inicializa una nueva
        undo_version_changes:  deshace en esquema de trabajo los cambios de
                               la version
        downgrade_version: elimina version de trabajo y reabre version anterior

    """

    def __init__(self):
        """Instancia objeto y/o inicializa propiedades.

        Parametros:  Ninguno
        """
        self.db_cnx = None
        self.db_file = None
        self.versions = {}
        l_vrs = Version(self, 1, '-- Nueva Version --')
        self.wrk_schema = l_vrs.get_schema()

    def open(self, p_file):
        """ Abre archivo existente

        Parametros:
            p_file:  ruta completa del archivo DB a abrir

        """

        # Verifico si archivo pre-existente
        if not os.path.isfile(p_file):
            raise NotFileSelectedError(p_file)

        # Destruyo esquema y versiones actuales
        self.wrk_schema.destroy()
        self.versions.clear()

        # Abro el archivo mediante conexion
        if self.db_cnx is not None:
            self.db_cnx.close()
        self.db_cnx = sqlite3.connect(p_file,
                                      detect_types=sqlite3.PARSE_DECLTYPES)
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
            if l_wrk_vrs is None and l_row['effective_date'] is not None:
                l_wrk_vrs = Version(self, l_row['seq'] + 1,
                        '-- Nueva Version --')
            l_vrs = Version(self, l_row['seq'], l_row['summary'],
                  l_row['recid'])
            l_vrs.effective_date = l_row['effective_date']
            if l_vrs.effective_date is None:
                l_wrk_vrs = l_vrs

        self.wrk_schema = l_wrk_vrs.get_schema()
        # debug
        print('Hice Open.  Estadistica: {}'.format(
            self.wrk_schema.get_entities_statistic()))

    def saveas(self, p_file):
        """Grabo en nuevo archivo

        Parametros:
            p_file:  ruta completa del archivo DB a abrir

        """
        # Verifico si archivo pre-existente
        if os.path.isfile(p_file):
            os.remove(p_file)

        # Abro el archivo mediante conexion
        if self.db_cnx is not None:
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

    def discare_unsaved_changes(self):
        """ Descarta cambios no guardados.

        Paramtros: Ninguno
        """

        if self.db_file is not None:
            self.open(self.db_file)
        else:
            self.wrk_schema.destroy()
            self.__init__()

    def upgrade_version(self, p_eff_date):
        """Cierra la version de trabajo e inicializa una nuevai.

        Parametros:
            p_eff_date: Obligatorio. Vigencia de los cambios de la
            version.  Se espera fecha no anterior a vigencia de version
            precedente

        """

        if (not self.wrk_schema.has_unsaved_changes()
                and not self.wrk_schema.version.has_changes()):
            raise NoChangesForVersionError()

        if p_eff_date is None:
            raise VersionDateNotPermited()

        l_date_min = dt.datetime(2000,1,1).date()
        if p_eff_date < l_date_min:
            raise DateTooOldError()

        l_prev_date = l_date_min - dt.timedelta(days=1)
        l_seq = self.wrk_schema.version.seq
        if ( l_seq - 1 ) in self.versions:
            l_prev_date = self.versions[l_seq-1].effective_date
        if p_eff_date < l_prev_date:
            raise VersionDateNotPermited()

        self.wrk_schema.version.effective_date = p_eff_date
        self.wrk_schema.version.save()
        self.wrk_schema.save()
        self.discare_unsaved_changes()

    def undo_version_changes(self):
        """Elimina modificaciones realizadas con la version.

        Parametros: Ninguno
        """

        if self.db_file is not None:
            self.wrk_schema.version.undo_changes()
        self.discare_unsaved_changes()

    def downgrade_version(self):
        """Elimina modificaciones realizadas con la version.

        Parametros: Ninguno
        """

        l_prev_seq = self.wrk_schema.version.seq - 1
        if l_prev_seq not in self.versions:
            raise NotPreviousVersionExistsError()

        self.wrk_schema.version.delete()
        self.versions[l_prev_seq].effective_date = None
        self.versions[l_prev_seq].save()
        self.discare_unsaved_changes()
