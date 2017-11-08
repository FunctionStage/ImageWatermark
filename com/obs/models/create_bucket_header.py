#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class CreateBucketHeader(BaseModel):
    allowedAttr = {'aclControl' : BASESTRING, 'storageClass' : BASESTRING}


    def __init__(self, aclControl=None,storageClass= None):
        '''
        Constructor
        '''
        self.aclControl = aclControl
        self.storageClass = storageClass