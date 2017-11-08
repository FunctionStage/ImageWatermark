#!/usr/bin/python
# -*- coding:utf-8 -*-


from com.obs.models.base_model import BaseModel,BASESTRING
class IndexDocument(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'suffix': BASESTRING}

    def __init__(self, suffix=None):
        '''
        Constructor
        '''
        self.suffix = suffix