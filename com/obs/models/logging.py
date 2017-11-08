#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING
class Logging(BaseModel):
    '''
    classdocs
    '''
    allowedAttr = {'targetBucket': BASESTRING, 'targetPrefix': BASESTRING, 'targetGrants': list}

    def __init__(self,targetBucket=None,targetPrefix=None,targetGrants= None):
        '''
        Constructor
        '''
        self.targetBucket = targetBucket
        self.targetPrefix = targetPrefix
        self.targetGrants = targetGrants