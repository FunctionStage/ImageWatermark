#!/usr/bin/python
# -*- coding:utf-8 -*-


from com.obs.models.base_model import BaseModel,BASESTRING

class ErrorDocument(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'key': BASESTRING}

    def __init__(self, key=None):
        self.key = key