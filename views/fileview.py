
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf

from . import View


class FileView(View):
    ''' Vista File 

    '''
    
   
    def __init__(self, p_parent_wds, p_icon_lib, p_parent):        
        '''Constructor'''

        # Definición de marco
        View.__init__(self, p_parent_wds, p_icon_lib, p_parent)
        self.__versions = None

    def setup(self):
        ''' Configuro widgets '''

        #Titulo Tamaño Icono        

        # Menues
        self.wds['filemenu'] = tk.Menu(self.wds['gl_menubar'],tearoff=0)
        self.wds['new_act_menu'] = 0
        self.wds['filemenu'].add_command(label='Nuevo') 
        self.wds['open_act_menu'] = 1
        self.wds['filemenu'].add_command(label='Abrir') 
        self.wds['save_act_menu'] = 2
        self.wds['filemenu'].add_command(label='Grabar') 
        self.wds['saveas_act_menu'] = 3
        self.wds['filemenu'].add_command(label='Grabar como')
        self.wds['discare_changes_act_menu'] = 4
        self.wds['filemenu'].add_command(label='Descartar Cambios')
        self.wds['gl_menubar'].add_cascade(menu=self.wds['filemenu'], 
                label='Archivo')
 
        # widgets piropios
        self.wds['save_act_bt'] = tk.Button(self.wds['gl_toolbar'])
        self.wds['save_act_bt']['image'] = self.icon_lib['save32.png']
        self.wds['save_act_bt'].pack(side = tk.LEFT)

    
    def refresh_model(self, p_db_file):
        ''' Refresco widget desde modelo '''

        if p_db_file == None:
            p_db_file = '--- Nuevo Archivo ---'
        self.wds['gl_root'].title('Perfiles [%s]' % p_db_file)

    def prounp(self, p_view_mode):
        '''  Protejo y desprotejo mis widgets segun view_mode '''

        if p_view_mode[:6] != 'trans.':
            for l_index in range(self.wds['filemenu'].index(tk.END)+1):
                self.wds['filemenu'].entryconfigure(l_index,
                    state=tk.ACTIVE)
            self.wds['save_act_bt'].config(state=tk.ACTIVE)
        else:
            for l_index in range(self.wds['filemenu'].index(tk.END)+1):
                self.wds['filemenu'].entryconfigure(l_index,
                    state=tk.DISABLED)
            self.wds['save_act_bt'].config(state=tk.DISABLED)

    def get_selection(self):
        ''' En función del widget, determina el modelo seleccionado '''
            
        return None


