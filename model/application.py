
# -*- coding: utf-8 -*-

import os.path
import datetime

from . import *

class Application(Entity):
    """ Applicacion. 
    
    Atributos:
        p_recid --  = None -> No grabado en la DB
                   <> None -> Recid con el que se registra en la DB
    """

    def __init__(self, p_vrs, p_schema, p_code, p_name, 
            p_recid=None, p_fields_recid=None):
        ''' Constructor '''
        
        # Inicializo propiedades
        l_row = list()
        l_row.append(EntityField('', p_schema, True, False))
        l_row.append(EntityField('code', p_code, True, False))
        l_row.append(EntityField('', 'Right', False, True))
        l_row.append(EntityField('', 'ElementType', False, True))
        l_row.append(EntityField('', 'Rol', False, True))
        l_row.append(EntityField('', 'ApplicationRow', False, True))
        Entity.__init__(self, p_vrs, l_row, p_recid)

        ApplicationRow(p_vrs, self, p_name, p_fields_recid)

    def get_gui_label(self):
        return '[{}] {}'.format(self.code, self.get_rowfield('name'))

    def get_gui_parent(self):
        return self.schema

    def get_gui_separators(self):
        l_ret = dict()
        l_ret['right'] = 'DERECHOS'
        l_ret['elementtype'] = 'ELEMENTOS (Tipos)'
        l_ret['rol'] = 'ROLES'
        return l_ret

    def get_rowfield(self, p_field_name):
        ''' Obtengo el field'''
        l_rowfields = list(self.applicationrows.values())[0]
        if p_field_name not in l_rowfields.__dict__:
            raise EntityFieldNotExists(l_rowfields, p_field_name)
        return getattr(l_rowfields, p_field_name)

    def set_rowfield(self, p_field_name, p_field_value):
        '''cambia el valor de un field'''
        l_rowfields = list(self.applicationrows.values())[0]
        if p_field_name not in l_rowfields.__dict__:
            raise EntityFieldNotExists(l_rowfields, p_field_name)
        l_rowfields.__dict__[p_field_name] = p_field_value

    def is_gui_visible(self):
        return True


class ApplicationRow(Entity):
    """ Atributos simples de Application """

    def __init__(self, p_vrs, p_application, p_name, p_recid):

        # Inicializo propiedades
        l_row = list()
        l_row.append(EntityField('', p_application, True, False))
        l_row.append(EntityField('name', p_name, False, False))
        Entity.__init__(self, p_vrs, l_row, p_recid)



