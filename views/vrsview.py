
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
import operator

import perfiles.model as mm
from . import View

class VersionView(View):
    ''' Vista Versiones

    '''

    def __init__(self, p_parent_wds, p_icon_lib, p_parent):
        '''Constructor'''

        # Definición de marco
        View.__init__(self, p_parent_wds, p_icon_lib, p_parent)
        self.__versions = None

    def setup(self):
        ''' Configuro widgets '''

        #Titulo Tamaño Icono
        self['height'] = 200
        self['width'] = 300
        self['relief']='raised'
        self['borderwidth']=2
        self['padx']=2
        self['pady']=2

        # Menues
        self.wds['vrsmenu'] = tk.Menu(self.wds['gl_menubar'],tearoff=0)
        self.wds['view_act_menu'] = 0
        self.wds['vrsmenu'].add_command(label='Ver Esquema')
        self.wds['diff_act_menu'] = 1
        self.wds['vrsmenu'].add_command(label='Diferencias')
        self.wds['val_act_menu'] = 2
        self.wds['vrsmenu'].add_command(label='Reumen Validacion')
        self.wds['gl_menubar'].add_cascade(menu=self.wds['vrsmenu'],
                label='Version')

        # widgets propios
        self.wds['vrs_list'] = ttk.Treeview(self, columns =
                ('summary_col','e_date_col'), selectmode='browse')
        self.wds['vrs_list'].heading('#0', text = 'Vrs')
        self.wds['vrs_list'].column('#0', minwidth = 80, width = 80)
        self.wds['vrs_list'].heading('summary_col', text = 'Resumen')
        self.wds['vrs_list'].column('summary_col', minwidth = 170, width = 170)
        self.wds['vrs_list'].heading('e_date_col', text = 'Vigencia')
        self.wds['vrs_list'].column('e_date_col', minwidth = 80, width = 80)
        self.wds['vrs_list']['height']=5
        l_font = tkf.Font(size=8)
        self.wds['vrs_list'].tag_configure('version', font=l_font,
                image=self.icon_lib['version16.png'])

        self.wds['view_act_bt'] = tk.Button(self)
        self.wds['view_act_bt']['text'] = u'Ver Esquema'
        self.wds['view_act_bt']['underline'] = 0

        self.wds['diff_act_bt'] = tk.Button(self)
        self.wds['diff_act_bt']['text'] = u'Diferencias'
        self.wds['diff_act_bt']['underline'] = 0

        self.wds['val_act_bt'] = tk.Button(self)
        self.wds['val_act_bt']['text'] = u'Validacion'
        self.wds['val_act_bt']['underline'] = 0

        self.wds['vrs_list'].grid(column=0, row=4, columnspan=6, rowspan=2,
                sticky=tk.N+tk.E+tk.S+tk.W)
        self.wds['view_act_bt'].grid(column=0, row=8, columnspan=2,
                sticky=tk.E+tk.W)
        self.wds['diff_act_bt'].grid(column=2, row=8, columnspan=2,
                sticky=tk.E+tk.W)
        self.wds['val_act_bt'].grid(column=4, row=8, columnspan=2,
                sticky=tk.E+tk.W)

    def refresh_model(self, p_versions):
        ''' Refresco widget desde modelo '''

        # Vacio la lista
        l_rows = self.wds['vrs_list'].get_children()
        if len(l_rows) > 0:
            self.wds['vrs_list'].delete(*l_rows)

        #Cargo nueva lista
        self.__versions = p_versions
        l_vrs_list = sorted(p_versions.items(), key=operator.itemgetter(0))
        l_vrs_list.reverse()

        for x, l_vrs in l_vrs_list:
            print ('Estoy cargando version {}'.format(l_vrs.seq))
            l_ed = l_vrs.effective_date
            if l_ed == None:
                l_ed = '-working-'
            self.wds['vrs_list'].insert("", tk.END, l_vrs.seq,
                    text=l_vrs.seq, values=(
                    l_vrs.summary.splitlines()[0], l_ed),
                    tags='version')

    def prounp(self, p_view_mode):
        '''  Protejo y desprotejo mis widgets segun view_mode '''

        if p_view_mode[:6] != 'trans.':
            for l_index in range(self.wds['vrsmenu'].index(tk.END)+1):
                self.wds['vrsmenu'].entryconfigure(l_index,
                    state=tk.ACTIVE)
            self.wds['vrs_list'].config(selectmode='browse')
            self.wds['view_act_bt'].config(state=tk.ACTIVE)
            self.wds['diff_act_bt'].config(state=tk.ACTIVE)
            self.wds['val_act_bt'].config(state=tk.ACTIVE)
        else:
            for l_index in range(self.wds['vrsmenu'].index(tk.END)+1):
                self.wds['vrsmenu'].entryconfigure(l_index,
                    state=tk.DISABLED)
            self.wds['vrs_list'].config(selectmode='none')
            self.wds['view_act_bt'].config(state=tk.DISABLED)
            self.wds['diff_act_bt'].config(state=tk.DISABLED)
            self.wds['val_act_bt'].config(state=tk.DISABLED)

    def get_selection(self):
        ''' En función del widget, determina el modelo seleccionado '''
        l_selection = self.wds['vrs_list'].selection()
        if len(l_selection) == 0:
            return None
        l_seq = int(l_selection[0])
        print('No encuentra secuencia {}'.format(l_seq))
        l_vrs = self.__versions[l_seq]

        return l_vrs


