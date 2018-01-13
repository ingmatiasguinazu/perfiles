
# -*- coding: utf-8 -*-

import os.path
import datetime

from . import *

class Schema(Entity):
    """ Entidad Root de la aplicación

    """
    def __init__(self, p_vrs, p_recid=None):
        l_row = list()
        l_row.append(EntityField('', 'Application', False, True))
        Entity.__init__(self, p_vrs, l_row, p_recid)

    def get_gui_label(self):
        return '[{}] {}'.format(self.version.seq,
                self.version.summary.splitlines()[0])

    def get_gui_parent(self):
        return None

    def get_gui_separators(self):
        l_ret = dict()
        l_ret['application'] = 'APLICACIONES'
        return l_ret

    def is_gui_visible(self):
        return True


