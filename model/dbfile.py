
# -*- coding: utf-8 -*-

import sqlite3


class DBFile:
    def __init__(self,p_file):

        l_db_cnx = sqlite3.connect(p_file)

        l_SQL = ('CREATE TABLE Version ('
                +             'recid INTEGER PRIMARY KEY,'
                +             'summary CHAR,'
                +             'effective_date DATE,'
                +             'seq INTEGER UNIQUE )')
        l_db_cnx.execute(l_SQL)

        l_SQL = ('CREATE TABLE Application ('
                +             'recid INTEGER PRIMARY KEY,'
                +             'code TEXT,'
                +             'version_from INTEGER REFERENCES '
                +                                            'Version (recid),'
                +             'version_to INTEGER REFERENCES '
                +                                            'Version (recid),'
                +             'UNIQUE ('
                +                      'code,'
                +                      'version_from ) )' )
        l_db_cnx.execute(l_SQL)
        l_SQL = ('CREATE TABLE ApplicationRow ('
                +             'version_from INTEGER REFERENCES '
                +                                            'Version (recid),'
                +             'version_to INTEGER REFERENCES '
                +                                            'Version (recid),'
                +             'recid INTEGER PRIMARY KEY,'
                +             'application INTEGER REFERENCES '
                +                                            'Application (recid),'
                +             'name TEXT)' )
        l_db_cnx.execute(l_SQL)

        l_SQL = ('CREATE TABLE [Right] ('
                +   ' recid        INTEGER PRIMARY KEY,'
                +   ' application  INTEGER REFERENCES Application (recid),'
                +   ' code         TEXT,'
                +   ' version_from INTEGER REFERENCES Version (recid),'
                +   ' version_to   INTEGER REFERENCES Version (recid),'
                +   ' UNIQUE ('
                +           ' application,'
                +           ' code,'
                +   ' version_from) )')
        l_db_cnx.execute(l_SQL)

        l_SQL = ( 'CREATE TABLE RightRow ('
                +      ' version_from    INTEGER REFERENCES Version (recid),'
                +      ' version_to      INTEGER REFERENCES Version (recid),'
                +      ' recid           INTEGER PRIMARY KEY,'
                +      ' [right]         INTEGER REFERENCES [Right] (recid),'
                +      ' granted_value   TEXT,'
                +      ' protected_value TEXT)' )
        l_db_cnx.execute(l_SQL)

        #TO COMPLETE:  crear todo el modelo de tablas


        l_db_cnx.commit()
        l_db_cnx.close()





