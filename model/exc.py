
# -*- coding: utf-8 -*-

class AppError(Exception):
    def __str__(self):
        return 'Application error not specified'


class NotFileSelectedError(AppError):
    def __init__(self):
        self.msg = u'Archivo no seleccionado'
    def __str__(self):
        return self.msg


class FileNotSelectedError(AppError):
    def __init__(self):
        self.msg = u'UPS! No seleccionaste archivo'
    def __str__(self):
        return self.msg


class FileAreadyExistsError(AppError):
    def __init__(self, p_file):
        self.msg = u'Archivo %s ya existe' % p_file
    def __str__(self):
        return self.msg


class UnsavedChangesExistsError(AppError):
    def __init__(self):
        self.msg = u'Existen cambios no grabados en el Esquema'
    def __str__(self):
        return self.msg


class VersionDateNotPermitedError(AppError):
    def __init__(self):
        self.msg = u'Fecha de aplicación menor a version precedente'
    def __str__(self):
        return self.msg


class DateTooOldError(AppError):
    def __init__(self):
        self.msg = u'Fecha muy antigua.  Solo se admite desde 01.01.2000'
    def __str__(self):
        return self.msg


class CorruptDataBaseError(AppError):
    def __init__(self):
        self.msg = u'Corrupcién an base de datoCorrupcién an base de datos'
    def __str__(self):
        return self.msg


class KeyAlreadyExistsError(AppError):
    def __init__(self, p_entity):
        self.msg = u'Infranción de clave unica.  {}({})'.format(
                p_entity.__class__.__name__, p_entity.pk)
    def __str__(self):
        return self.msg


class NotPreviousVersionExistsError(AppError):
    def __init__(self):
        self.msg = u'Ups! No existe una version anterior para comparar'
    def __str__(self):
        return self.msg


class NotSelectedObjectError(AppError):
    def __init__(self, p_object):
        self.msg = u'Ups! No as selecccionado {}'.format(p_object)
    def __str__(self):
        return self.msg


class SchemaAlreadyVisibleError(AppError):
    def __init__(self):
        self.msg = u'Ups!  Este es el esquema que estas viendo'
    def __str__(self):
        return self.msg


class EntityFieldNameNotInformedError(AppError):
    def __init__(self):
        self.msg = u'Infranción Nombre Campo No Informado'
    def __str__(self):
        return self.msg

class EntityFieldNotExistsError(AppError):
    def __init__(self, p_object=None, p_field=''):
        self.msg = u'Campo {} inexistente en entidad {}'.format(
                p_object.__class__.__name__, p_field)
    def __str__(self):
        return self.msg

class EntityFieldNewValueTypeError(AppError):
    def __init__(self, p_field='', p_class='', p_expected_class=''):
        self.msg = (u'Nuevo valor para campo ' 
                + '{} es de tipo {}.  Se espera tipo {}'.format(p_field, 
                    p_class, p_expected_class))
    def __str__(self):
        return self.msg
