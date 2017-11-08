#!/usr/bin/python
# -*- coding:utf-8 -*-


from com.obs.models.base_model import BaseModel,BASESTRING

class Versions(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'prefix': BASESTRING, 'key_marker': BASESTRING, 'max_keys': int,
                   'delimiter' : BASESTRING, 'version_id_marker': BASESTRING}

    def __init__(self,
                prefix = None,
                key_marker = None,
                max_keys = None,
                delimiter = None,
                version_id_marker = None):
        '''
        Constructor
        '''
        self.prefix = prefix
        self.key_marker = key_marker
        self.max_keys = max_keys
        self.delimiter = delimiter
        self.version_id_marker = version_id_marker