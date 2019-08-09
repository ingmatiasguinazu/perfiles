"""
Paquete Model de la applicación Perfiles
----------------------------------------

PRINCIPALES MODULOS Y SUS CLASES
    appfile (Clase AppFile): controlador general del Model
    exc (Clases Excepciones):  excepciones de la aplicación
    entity (Clase Entity):  objetos del modelo, adminsitrables y persistentes

REFERENCIA ESQUEMA UML ENTITIES
    https://github.com/perfiles/wiki/UML-de-Entidades-para-Perfiles
"""

# -*- coding: utf-8 -*-

import sqlite3

from .exc import *
from .entity import *
from .application import *
from .right import *
from .schema import *
from .version import *
from .appfile import *



