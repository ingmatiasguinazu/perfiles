
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf

import perfiles.model as mm

from . import View

class SchemaView(View):
    ''' Vista Versiones

    '''


    def __init__(self, p_parent_wds, p_icon_lib, p_parent):
        '''Constructor'''

        # Definición de marco
        View.__init__(self, p_parent_wds, p_icon_lib, p_parent)
        self.__schema = None


    def setup(self):
        ''' Configuro widgets '''

        #Titulo Tamaño Icono
        self['relief']='raised'
        self['borderwidth']=2
        self['padx']=2
        self['pady']=2

        # Menues
        #self.wds['vrsmenu'] = tk.Menu(self.wds['gl_menubar'],tearoff=0)
        #self.wds['view_act_menu'] = 0
        #self.wds['vrsmenu'].add_command(label='Ver Esquema')
        #self.wds['diff_act_menu'] = 1
        #diff_act_menuself.wds['vrsmenu'].add_command(label='Diferencias')
        #self.wds['val_act_menu'] = 2
        #self.wds['vrsmenu'].add_command(label='Reumen Validacion')
        #self.wds['gl_menubar'].add_cascade(menu=self.wds['vrsmenu'],
        #        label='Version')

        # widgets propios
        self.wds['schema_tree'] = ttk.Treeview(self, selectmode='browse')
        l_font = tkf.Font(size=8)
        self.wds['schema_tree'].tag_configure('schema', font=l_font,
                image=self.icon_lib['version16.png'])
        self.wds['schema_tree'].tag_configure('application', font=l_font,
                image=self.icon_lib['application16.png'])
        self.wds['schema_tree'].tag_configure('version', font=l_font,
                image=self.icon_lib['version16.png'])
        self.wds['schema_tree'].tag_configure('elementtype', font=l_font,
                image=self.icon_lib['eletype16.png'])
        self.wds['schema_tree'].tag_configure('element', font=l_font,
                image=self.icon_lib['element16.png'])
        self.wds['schema_tree'].tag_configure('rol', font=l_font,
                image=self.icon_lib['perfiles16.png'])
        self.wds['schema_tree'].tag_configure('right', font=l_font,
                image=self.icon_lib['right16.png'])

        #self.wds['view_act_bt'] = tk.Button(self)
        #self.wds['view_act_bt']['text'] = u'Ver Esquema'
        #self.wds['view_act_bt']['underline'] = 0

        #self.wds['diff_act_bt'] = tk.Button(self)
        #self.wds['diff_act_bt']['text'] = u'Diferencias'
        #self.wds['diff_act_bt']['underline'] = 0

        #self.wds['val_act_bt'] = tk.Button(self)
        #self.wds['val_act_bt']['text'] = u'Validacion'
        #self.wds['val_act_bt']['underline'] = 0

        self.wds['schema_tree'].pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        #self.wds['view_act_bt'].grid(column=0, row=8, columnspan=2,
        #        sticky=tk.E+tk.W)
        #self.wds['diff_act_bt'].grid(column=2, row=8, columnspan=2,
        #        sticky=tk.E+tk.W)
        #self.wds['val_act_bt'].grid(column=4, row=8, columnspan=2,
        #        sticky=tk.E+tk.W)

    def clean_tree_node(self, p_node_iid=None):
        ''' Elimina los nodos que no existen en schema '''
        if p_node_iid != None:
            if p_node_iid[:10] != 'separator.':
                l_entity = self.__schema.get_entity(int(p_node_iid))
                if l_entity == None:
                    self.wds['schema_tree'].delete(p_node_iid)
                    return
                elif l_entity.deleted:
                    self.wds['schema_tree'].delete(p_node_iid)
                    print('Entidad {} no existe'.format(p_node_iid))
                    return
            l_childs_iids = self.wds['schema_tree'].get_children(p_node_iid)
        else:
            l_childs_iids = self.wds['schema_tree'].get_children()

        for l_child in l_childs_iids:
            self.clean_tree_node(l_child)


    def refresh_model(self, p_schema):
        ''' Refresco widget desde modelo '''

        #Cargo nueva lista
        self.__schema = p_schema

        self.clean_tree_node()

        for l_entity in self.__schema.get_entities():

            if not l_entity.is_gui_visible() or l_entity.deleted:
                continue

            l_tag = l_entity.__class__.__name__.lower()
            l_parent_entity = l_entity.get_gui_parent()
            if l_parent_entity == None:
                l_separator_iid = ''
            else:
                l_separator_iid = 'separator.{}.{}'.format(l_tag,
                        l_parent_entity.objid)

            # Me agrego al arbol
            l_iid = l_entity.objid
            if not self.wds['schema_tree'].exists(l_iid):
                self.wds['schema_tree'].insert(l_separator_iid,
                    tk.END, l_iid, text='--new--', tags=l_tag)

                # Creo los separadores
                l_separators = l_entity.get_gui_separators()
                for l_separator in l_separators.keys():
                    l_separator_iid = 'separator.{}.{}'.format(l_separator,
                            l_iid)
                    l_text = l_separators[l_separator]
                    self.wds['schema_tree'].insert(l_iid,
                            tk.END, l_separator_iid, text=l_text,
                            tags=l_separator)

            # Actualizo el label
            l_text = l_entity.get_gui_label()
            self.wds['schema_tree'].item(l_iid, text=l_text)

    def prounp(self, p_view_mode):
        '''  Protejo y desprotejo mis widgets segun view_mode '''

        #if p_view_mode[:6] != 'trans.':
        #    for l_index in range(self.wds['vrsmenu'].index(tk.END)+1):
        #        self.wds['vrsmenu'].entryconfigure(l_index,
        #            state=tk.ACTIVE)
        #    self.wds['schema_tree'].config(selectmode='browse')
        #    self.wds['view_act_bt'].config(state=tk.ACTIVE)
        #    self.wds['diff_act_bt'].config(state=tk.ACTIVE)
        #    self.wds['val_act_bt'].config(state=tk.ACTIVE)
        #else:
        #    for l_index in range(self.wds['vrsmenu'].index(tk.END)+1):
        #        self.wds['vrsmenu'].entryconfigure(l_index,
        #            state=tk.DISABLED)
        #    self.wds['schema_tree'].config(selectmode='none')
        #    self.wds['view_act_bt'].config(state=tk.DISABLED)
        #    self.wds['diff_act_bt'].config(state=tk.DISABLED)
        #    self.wds['val_act_bt'].config(state=tk.DISABLED)
        pass

    def get_selection(self):
        ''' En función del widget, determina el modelo seleccionado '''
        #l_selection = self.wds['schema_tree'].selection()
        #if len(l_selection) == 0:
        #    return None
        #l_seq = int(l_selection[0])
        #l_vrs = self.__versions[l_seq]
        #
        #return l_vrs
        pass



