
# -*- coding: utf-8 -*-

import os.path
import datetime

from . import *

class Right(Entity):
    """ Right. 
    
    Atributos:
        p_recid --  = None -> No grabado en la DB
                   <> None -> Recid con el que se registra en la DB
    """

    def __init__(self, p_vrs, p_app, p_code, p_granted_value, 
            p_protected_value, p_recid=None, p_fields_recid=None):
        ''' Constructor '''
        
        # Inicializo propiedades
        l_row = list()
        l_row.append(EntityField('', p_app, True, False))
        l_row.append(EntityField('code', p_code, True, False))
        l_row.append(EntityField('', 'Allocation', False, True))
        l_row.append(EntityField('', 'RightElementType', False, True))
        l_row.append(EntityField('', 'RightRow', False, True))
        Entity.__init__(self, p_vrs, l_row, p_recid)

        RightRow(p_vrs, self, p_granted_value, p_protected_value, 
                p_fields_recid)

    def get_gui_label(self):
        return '{}'.format(self.code, self.code)

    def get_gui_parent(self):
        return self.application

    def get_gui_separators(self):
        l_ret = dict()
        return l_ret

    def get_rowfield(self, p_field_name):
        ''' Obtengo el field'''
        l_rowfields = list(self.rightrows.values())[0]
        if p_field_name not in l_rowfields.__dict__:
            raise EntityFieldNotExists(l_rowfields, p_field_name)
        return getattr(l_rowfields, p_field_name)

    def set_rowfield(self, p_field_name, p_field_value):
        '''cambia el valor de un field'''
        l_rowfields = list(self.rightrows.values())[0]
        if p_field_name not in l_rowfields.__dict__:
            raise EntityFieldNotExists(l_rowfields, p_field_name)
        l_rowfields.__dict__[p_field_name] = p_field_value

    def is_gui_visible(self):
        return True


class RightRow(Entity):
    """ Atributos simples de Application """

    def __init__(self, p_vrs, p_right, p_granted_value, p_protected_value, 
            p_recid):

        # Inicializo propiedades
        l_row = list()
        l_row.append(EntityField('', p_right, True, False))
        l_row.append(EntityField('granted_value', p_granted_value, 
            False, False))
        l_row.append(EntityField('protected_value', p_protected_value, 
            False, False))
        Entity.__init__(self, p_vrs, l_row, p_recid)


