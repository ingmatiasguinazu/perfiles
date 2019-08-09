''' Modulo Principal de la Aplicacion '''

# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.filedialog as fdlg
import tkinter.messagebox as mbox
import datetime as dt


import perfiles.model as mm
import perfiles.views as vv


class Controler():
    """ Controlador Principal de la Aplicación

        Atributos:
            - app_file --> modelo completo de la aplicación
        - trans --> se trata de la tranacción en curso

    """

    def __init__(self):
        ''' Constructor '''

        # Inicializo Objeto
        self.app_file = mm.AppFile()
        self.trans = None
        self.views = {}

        # VISTA DESKTOP

        # Creo vista
        self.views['desktop'] = vv.Desktop()

        # Mapeo comandos
        self.views['desktop'].wds['transOK_act_bt']['command'] = self.conf_act
        self.views['desktop'].wds['transmenu'].entryconfigure(
            self.views['desktop'].wds['transOK_act_menu'],
            command=self.conf_act)

        self.views['desktop'].wds['transCancel_act_bt']['command'] = (
            self.cancel_act)
        self.views['desktop'].wds['transmenu'].entryconfigure(
            self.views['desktop'].wds['transCancel_act_menu'],
            command=self.cancel_act)

        # VISTA FILE

        # Creo vista
        self.views['file'] = (
            vv.FileView(self.views['desktop'].wds,
                        self.views['desktop'].icon_lib,
                        self.views['desktop'].wds['lateralframe']))
        # Mapeo comandos
        self.views['file'].wds['filemenu'].entryconfigure(
                self.views['file'].wds['new_act_menu'],
                command=self.file_new_act)
        self.views['file'].wds['filemenu'].entryconfigure(
                self.views['file'].wds['open_act_menu'],
                command=self.file_open_act)
        self.views['file'].wds['save_act_bt']['command'] = self.file_save_act
        self.views['file'].wds['filemenu'].entryconfigure(
                self.views['file'].wds['save_act_menu'],
                command=self.file_save_act)
        self.views['file'].wds['filemenu'].entryconfigure(
                self.views['file'].wds['saveas_act_menu'],
                command=self.file_saveas_act)
        self.views['file'].wds['filemenu'].entryconfigure(
                self.views['file'].wds['discare_changes_act_menu'],
                command=self.file_discare_changes_act)

        # VISTA VERSIONS

        # Creo vista
        self.views['versions'] = (
            vv.VersionView(self.views['desktop'].wds,
                           self.views['desktop'].icon_lib,
                           self.views['desktop'].wds['lateralframe']))
        self.views['versions'].pack(side=tk.BOTTOM, fill=tk.X)
        # Mapeo comandos
        self.views['versions'].wds['view_act_bt']['command'] = (
                self.versions_view_act)
        self.views['versions'].wds['vrsmenu'].entryconfigure(
                self.views['versions'].wds['view_act_menu'],
                command=self.versions_view_act)
        self.views['versions'].wds['diff_act_bt']['command'] = (
                self.versions_diff_act)
        self.views['versions'].wds['vrsmenu'].entryconfigure(
                self.views['versions'].wds['diff_act_menu'],
                command=self.versions_diff_act)
        self.views['versions'].wds['val_act_bt']['command'] = (
                self.versions_val_act)
        self.views['versions'].wds['vrsmenu'].entryconfigure(
                self.views['versions'].wds['val_act_menu'],
                command=self.versions_val_act)

        # VISTA SCHEMA

        # Creo vista
        self.views['schema'] = (
                vv.SchemaView(self.views['desktop'].wds,
                              self.views['desktop'].icon_lib,
                              self.views['desktop'].wds['lateralframe']))
        self.views['schema'].pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # Mapeo comandos
        self.views['versions'].wds['view_act_bt']['command'] = (
                self.versions_view_act)
        self.views['versions'].wds['vrsmenu'].entryconfigure(
                self.views['versions'].wds['view_act_menu'],
                command=self.versions_view_act)
        self.views['versions'].wds['diff_act_bt']['command'] = (
                self.versions_diff_act)
        self.views['versions'].wds['vrsmenu'].entryconfigure(
                self.views['versions'].wds['diff_act_menu'],
                command=self.versions_diff_act)
        self.views['versions'].wds['val_act_bt']['command'] = (
                self.versions_val_act)
        self.views['versions'].wds['vrsmenu'].entryconfigure(
                self.views['versions'].wds['val_act_menu'],
                command=self.versions_val_act)

        self.refresh_model()

    def refresh_model(self):
        ''' Refresco las vistas
        '''
        self.views['file'].refresh_model(self.app_file.db_file)
        self.views['versions'].refresh_model(self.app_file.versions)
        self.views['schema'].refresh_model(self.app_file.wrk_schema)

########################################################
#              USER ACTIONS
########################################################

    def conf_act(self):
        if self.trans is not None:
            self.trans.do()

    def cancel_act(self):
        if self.trans is not None:
            self.views['desktop'].set_message(0, u'Trasaccion %s cancelada' %
                                              self.trans.__class__.__name__)
            self.trans.end()

    def versions_view_act(self):
        self.trans = VersionView(self)

    def versions_diff_act(self):
        self.trans = VersionDiff(self)

    def versions_val_act(self):
        self.trans = VersionVal(self)

    def file_new_act(self):
        self.trans = FileNew(self)

    def file_open_act(self):
        self.trans = FileOpen(self)

    def file_save_act(self):
        if self.app_file.db_cnx is None:
            self.trans = FileSaveas(self)
        else:
            self.trans = FileSave(self)

    def file_saveas_act(self):
        self.trans = FileSaveas(self)

    def file_discare_changes_act(self):
        self.trans = FileDiscareChanges(self)


class Transaction():
    ''' Interfase de transaccion'''

    def __init__(self, p_controler, p_conf_needed,
                 p_continue_on_error):
        self.controler = p_controler
        self.conf_needed = p_conf_needed
        self.continue_on_error = p_continue_on_error
        self.ini()

    def ini(self):
        ''' Inicializo transaccion
        '''
        self.controler.trans = self

        # Protejo / desprotejo views
        for l_view_key in self.controler.views.keys():
            self.controler.views[l_view_key].prounp(
                    'trans.' + self.__class__.__name__)

        # Validaciones pre-Transacción
        l_ret = self.pretrans_validation()
        self.controler.views['desktop'].set_message(
                    l_ret[0], l_ret[1])
        if l_ret[0] > 2:  # Pretransaction Error
            self.end()
            return

        if self.conf_needed or l_ret[0] > 0:   # Requiere confirmación
            return

        self.do()  # Realizo la transacción

    def do(self):
        ''' Realizo transacción
        '''
        l_ret = list()
        try:
            self.execute()
        except mm.AppError as l_err:
            l_ret.append(3)
            l_ret.append(l_err.msg)
            raise l_err
        except Exception as l_err:
            l_ret.append(3)
            l_ret.append('Error no aplicativo: {}'.format(l_err.__str__()))
            raise l_err
        else:
            l_ret.append(1)
            l_ret.append('GENIAL!:  {} se ejecutó exitosamente'.format(
                    self.__class__.__name__))

        self.controler.views['desktop'].set_message(
                    l_ret[0], l_ret[1])

        if l_ret[0] > 2 and self.continue_on_error:  # Error
            return

        self.end()

    def end(self):
        ''' Finalizo transacción '''

        self.trans = None

        # Desprotejo views
        for l_view_key in self.controler.views.keys():
            self.controler.views[l_view_key].prounp('normal')

    def pretrans_validation(self):
        pass

    def execute(self):
        pass


########################################################
#              TRANSACCIONES DE FILE
########################################################

class FileSave(Transaction):
    ''' Crea un nuevo archivo '''

    def __init__(self, p_controler):
        # Inicializo transacción.  No requiere confirmación.
        # En caso de error termina transacción
        Transaction.__init__(self, p_controler, False, False)

    def pretrans_validation(self):

        l_ret = list()

        l_ret.append(0)
        l_ret.append('')
        return l_ret

    def execute(self):
        '''  Ejecuta FileNew
        '''

        self.controler.app_file.wrk_schema.save()


class FileSaveas(Transaction):
    ''' Crea un nuevo archivo '''

    def __init__(self, p_controler):
        # Inicializo transacción.  No requiere confirmación.
        # En caso de error termina transacción
        Transaction.__init__(self, p_controler, False, False)

    def pretrans_validation(self):

        l_ret = list()
        if len(self.controler.app_file.versions) > 1:
            l_ret.append(2)
            l_ret.append('IMPORTANTE! Este archivo contine historico de '
                         + 'versiones que no seran guardados en el nuevo '
                         + 'archivo.  OK para continuar')
            return l_ret

        l_ret.append(0)
        l_ret.append('')
        return l_ret

    def execute(self):
        '''  Ejecuta FileNew
        '''

        l_file_name = fdlg.asksaveasfilename(
            initialdir="c:\\", title="[Guardar Como]",
            filetypes=(('Archivos Perfil', '*.per'), ('Todos', '*.*')))

        if l_file_name == '' or l_file_name is None:
            raise mm.FileNotSelectedError()

        self.controler.app_file.saveas(l_file_name)
        self.controler.refresh_model()


class FileDiscareChanges(Transaction):
    ''' Descarto Cambios '''

    def __init__(self, p_controler):
        # Inicializo transacción.  No requiere confirmación.
        # En caso de error termina transacción
        Transaction.__init__(self, p_controler, False, False)

    def pretrans_validation(self):
        l_ret = list()
        if self.controler.app_file.wrk_schema.has_unsaved_changes():
            l_ret.append(2)
            l_ret.append('CUIDADO!:  Tenes cambios no guardados.'
                         + ' Si continuas los perderas.  OK para continuar')
            return l_ret

        if not self.controler.app_file.wrk_schema.has_unsaved_changes():
            l_ret.append(3)
            l_ret.append('UPS!  No hay cambios para descartar')
            return l_ret

        l_ret.append(0)
        l_ret.append('')
        return l_ret

    def execute(self):
        '''  Ejecuta FileNew
        '''

        # Obtiene objeto seleccionado
        self.controler.app_file.discare_changes()
        self.controler.refresh_model()


class FileNew(Transaction):
    ''' Crea un nuevo archivo '''

    def __init__(self, p_controler):
        # Inicializo transacción.  No requiere confirmación.
        # En caso de error termina transacción
        Transaction.__init__(self, p_controler, False, False)

    def pretrans_validation(self):
        l_ret = list()
        if self.controler.app_file.wrk_schema.has_unsaved_changes():
            l_ret.append(2)
            l_ret.append('CUIDADO!:  Tenes cambios no guardados.'
                         + ' Si continuas los perderas.  OK para continuar')
            return l_ret

        l_ret.append(0)
        l_ret.append('')
        return l_ret

    def execute(self):
        '''  Ejecuta FileNew
        '''

        # Obtiene objeto seleccionado
        if self.controler.app_file.db_cnx is not None:
            self.controler.app_file.db_cnx.close()
        self.controler.app_file.wrk_schema.reset_as_new()
        self.controler.app_file.wrk_schema.delete()
        self.controler.app_file = mm.AppFile()
        self.controler.refresh_model()


class FileOpen(Transaction):
    ''' Abre un nuevo archivo '''

    def __init__(self, p_controler):
        # Inicializo transacción.  No requiere confirmación.
        # En caso de error termina transacción
        Transaction.__init__(self, p_controler, False, False)

    def pretrans_validation(self):
        l_ret = list()
        if self.controler.app_file.wrk_schema.has_unsaved_changes():
            l_ret.append(2)
            l_ret.append('CUIDADO!:  Tenes cambios no guardados.'
                         + ' Si continuas los perderas.  OK para continuar')
            return l_ret

        l_ret.append(0)
        l_ret.append('')
        return l_ret

    def execute(self):
        '''  Ejecuta FileOpen
        '''

        # Obtiene objeto seleccionado
        l_file_name = fdlg.askopenfilename(
            initialdir="c:\\", title="[Abrir Archivo]",
            filetypes=(('Archivos Perfil', '*.per'), ('Todos', '*.*')))

        if l_file_name == '' or l_file_name is None:
            raise mm.FileNotSelectedError()

        self.controler.app_file.open(l_file_name)
        self.controler.refresh_model()


########################################################
#              TRANSACCIONES DE VERSION
########################################################

class VersionVal(Transaction):
    ''' Emite Documento Validación '''
    def __init__(self, p_controler):
        # Inicializo transacción.  No requiere confirmación.
        # En caso de error termina transacción
        Transaction.__init__(self, p_controler, False, False)

    def pretrans_validation(self):
        l_ret = list()

        l_ret.append(0)
        l_ret.append('')
        return l_ret

    def execute(self):
        '''  Ejecuta FileNew
        '''

        # Obtiene objeto seleccionado
        l_vrs = self.controler.views['versions'].get_selection()

        # Validaciones previas
        if l_vrs is None:
            raise mm.NotSelectedObjectError('Version')

        # Ejecuta transacción en modelo
        mbox.showinfo('Implementacion Pendiente',
                      '{} Schema trans aun no implementada'.format(
                          self.__class__.__name__))

        self.controler.app_file.clean_versions(
            self.controler.app_file.versions[5])


class VersionView(Transaction):
    ''' Visualiza una Version '''

    def __init__(self, p_controler):
        # Inicializo transacción.  No requiere confirmación.
        # En caso de error termina transacción
        Transaction.__init__(self, p_controler, False, False)

    def pretrans_validation(self):
        l_ret = list()
        l_ret.append(0)
        l_ret.append('')
        return l_ret

    def execute(self):
        '''  Ejecuta FileNew
        '''

        # Obtiene objeto seleccionado
        l_vrs = self.controler.views['versions'].get_selection()

        # Validaciones previas
        if l_vrs is None:
            raise mm.NotSelectedObjectError('Version')

        if l_vrs.effective_date is None:
            raise mm.SchemaAlreadyVisibleError()

        # Ejecuta transacción en modelo
        mbox.showinfo('Implementacion Pendiente',
                      '{} Schema trans aun no implementada'.format(
                          self.__class__.__name__))
        # debug
        l_app = mm.Application(self.controler.app_file.wrk_schema.version,  self.controler.app_file.wrk_schema,"XXX", "YYYYYY")
        self.controler.refresh_model()

class VersionDiff(Transaction):

    def __init__(self, p_controler):
        # Inicializo transacción.  No requiere confirmación.
        # En caso de error termina transacción
        Transaction.__init__(self, p_controler, False, False)

    def pretrans_validation(self):
        l_ret = list()

        l_ret.append(0)
        l_ret.append('')
        return l_ret

    def execute(self):

        # Obtiene objeto seleccionado
        l_vrs = self.controler.views['versions'].get_selection()

        # Validaciones previas
        if l_vrs is None:
            raise mm.NotSelectedObjectError('Version')

        if (l_vrs.seq - 1) not in self.controler.app_file.versions:
            raise mm.NotPreviousVersionExistsError()

        # Ejecuta transacción en modelo
        mbox.showinfo('Implementacion Pendiente',
                      '{} Schema trans aun no implementada'.format(
                          self.__class__.__name__))

        # debug
#        self.controler.app_file.upgrade_version(dt.datetime(2019,1,1).date())
#        self.controler.app_file.downgrade_version()
        self.controler.app_file.undo_version_changes()
        self.controler.refresh_model()
        print('hizo upgrade version')


################################################################################
#                           CICLO PRINCIPAL
################################################################################
if __name__ == "__main__":
    Controler().views['desktop'].mainloop()
