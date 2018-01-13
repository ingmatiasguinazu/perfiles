''' Ese es el doucmento de base de destop.py '''

# -*- coding: utf-8 -*-

import os
import sys
import os.path as osp
import tkinter as tk
import tkinter.font as tkf


class Desktop(tk.Tk):
    ''' Escritorio sobre el cual se posicionan las vistas

    Componentes
    -->  Ventana principal:  tk()
    -->  Toolbar:  tk.Frame accesible via .wds['toolbar']
    -->  Marco Lateral:  tk.Frame accesible via .wds['lateralframe']
    -->  Marco Central:  tk.Frame accesible via .wds['centralframe']
    -->  Message Bar: tk.Label() accesible via .wds['usr_msg']
    -->  Icon Lib:  diccionario de iconos accesble via .icon_lib[]
    '''


    def __init__(self):
        tk.Tk.__init__(self)
        self.icon_lib={}
        self.load_icons()
        self.wds={}
        self.setup()
        self.prounp('normal')


    def setup(self):
        ''' Creo y configuro widgets '''

        #Titulo Tamaño Icono
        self.iconphoto(self, self.icon_lib['perfiles128.png'])
        self.geometry("1024x680+1+1")
        self.wds['gl_root'] = self


        #Menues
        self.wds['gl_menubar'] = tk.Menu(self)
        self['menu'] = self.wds['gl_menubar']

        self.wds['transmenu'] = tk.Menu(self.wds['gl_menubar'], tearoff=0)

        self.wds['transOK_act_menu'] = 0
        self.wds['transmenu'].add_command(label='OK')
        self.wds['transCancel_act_menu'] = 1
        self.wds['transmenu'].add_command(label='Cancelar')
        self.wds['gl_menubar'].add_cascade(menu=self.wds['transmenu'],
                label='Transaction')

        #Widgets
        self.wds['gl_toolbar'] = tk.Frame(self.master,
                relief=tk.RAISED, bd=2, bg="#E5E5E5")
        self.wds['gl_toolbar'].pack(side=tk.TOP, fill=tk.X)
        self.wds['transOK_act_bt'] = tk.Button(self.wds['gl_toolbar'],
                image = self.icon_lib['ok32.png'])
        self.wds['transOK_act_bt'].pack(side=tk.LEFT)
        self.wds['transCancel_act_bt'] = tk.Button(self.wds['gl_toolbar'],
                image = self.icon_lib['cancel32.png'])
        self.wds['transCancel_act_bt'].pack(side=tk.LEFT)

        #Barra de mensaje
        l_font = tkf.Font(size=10, weight='bold')
        self.wds['usr_msg']= tk.Label(self, padx=10,pady=2,
                relief=tk.RIDGE, font=l_font, anchor=tk.W,
                fg='black', bg='gray')
        self.wds['usr_msg'].pack(side=tk.BOTTOM, fill=tk.X)

        #Marco lateral
        self.wds['lateralframe'] = tk.Frame(self.master,
                relief=tk.RAISED, bd=2, bg="yellow")
        self.wds['lateralframe'].pack(side=tk.LEFT, fill=tk.Y),

        #Marico Central
        self.wds['centralframe'] = tk.Frame(self.master,
                relief=tk.RAISED, bd=2, bg="red")
        self.wds['centralframe'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True),

    def load_icons(self):
        '''Inicializo diccionario de iconos'''
        self.icon_lib={}
        l_my_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        l_image_path = l_my_path + '/image'
        for l_fname in os.listdir(l_image_path):
            if osp.isfile(osp.join(l_image_path, l_fname)):
                try:
                    key = os.path.basename(l_fname)
                    self.icon_lib[key] = tk.PhotoImage(file =
                            osp.join(l_image_path, l_fname))
                except: pass

    def prounp(self, p_view_mode):
        '''  Protejo y desprotejo mis widgets segun view_mode '''
        if p_view_mode[:6] == 'trans.':
            for l_index in range(self.wds['transmenu'].index(tk.END)+1):
                self.wds['transmenu'].entryconfigure(l_index,
                    state=tk.ACTIVE)
            self.wds['transOK_act_bt'].config(state=tk.ACTIVE)
            self.wds['transCancel_act_bt'].config(state=tk.ACTIVE)
        else:
            for l_index in range(self.wds['transmenu'].index(tk.END)+1):
                self.wds['transmenu'].entryconfigure(l_index,
                    state=tk.DISABLED)
            self.wds['transOK_act_bt'].config(state=tk.DISABLED)
            self.wds['transCancel_act_bt'].config(state=tk.DISABLED)

    def set_message(self, p_msg_type=0, p_msg_text=''):
        ''' Muestra un mensaje formateado
        --> p_msg_type:  0-Normal, 1-Exito, 2-Alerta, 3-Error
        '''
        if p_msg_text == None or p_msg_text == '':
            p_msg_type = 0

        if p_msg_type == 1:
            l_bg = 'white'
            l_fg = 'green'
        elif p_msg_type == 2:
            l_bg = 'yellow'
            l_fg = 'red'
        elif p_msg_type == 3:
            l_bg = 'red'
            l_fg = 'white'
        else:
            l_bg = 'gray'
            l_fg = 'black'

        self.wds['usr_msg'].config(fg=l_fg, bg=l_bg, text=p_msg_text)

    def refresh_model(self):
        ''' Refresca modelo '''
        pass





