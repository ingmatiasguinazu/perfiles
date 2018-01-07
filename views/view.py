
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font

class View(tk.Frame):
    
   
    def __init__(self, p_parent_wds, p_icon_lib, p_parent):
        ''' Constructor '''
        
        # Definición de marco
        tk.Frame.__init__(self, p_parent)
        self.icon_lib=p_icon_lib
        
        # Cargo widgets globales
        self.wds={}
        for l_wds_key in p_parent_wds.keys():
            if l_wds_key[:3] == 'gl_':
                self.wds[l_wds_key] = p_parent_wds[l_wds_key]

        # Configuro widgets propios
        self.setup()


    def setup(self):
        ''' A re-escribir por cada view '''
        pass

    def refresh_model(self, model_object=None):
        '''  Refresca los widgets propios '''

        # Guardo foco
        pass

        # Actualizo mis atributos del modelo
        pass

        # reposiciono foco
        pass

    def prounp(self, p_view_mode):
        '''  Protejo y desprotejo mis widgets segun view_mode '''
        pass








