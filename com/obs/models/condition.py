#!/usr/bin/python
# -*- coding:utf-8 -*-


from com.obs.models.base_model import BaseModel,BASESTRING

class Condition(BaseModel):
    '''
    classdocs
    '''
    allowedAttr = {'keyPrefixEquals': BASESTRING, 'httpErrorCodeReturnedEquals':int}

    def __init__(self, keyPrefixEquals=None,httpErrorCodeReturnedEquals=None):
        '''
        Constructor
        '''
        self.keyPrefixEquals = keyPrefixEquals
        self.httpErrorCodeReturnedEquals = httpErrorCodeReturnedEquals