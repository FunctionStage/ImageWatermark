#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class Options(BaseModel):
    '''
    classdocs
    '''
    allowedAttr = {'origin': BASESTRING, 'accessControlRequestMethods': list, 'accessControlRequestHeaders': list}

    def __init__(self, origin=None, accessControlRequestMethods = None, accessControlRequestHeaders = None):
        '''
        Constructor
        '''
        self.origin = origin
        self.accessControlRequestMethods = accessControlRequestMethods
        self.accessControlRequestHeaders = accessControlRequestHeaders