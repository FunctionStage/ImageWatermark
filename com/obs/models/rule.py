#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING
from com.obs.models.expiration import Expiration,NoncurrentVersionExpiration

class Rule(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'id': BASESTRING, 'prefix': BASESTRING, 'status': BASESTRING, 'expiration':Expiration, 'noncurrentVersionExpiration' : NoncurrentVersionExpiration}

    def __init__(self,id = None,prefix = None,status = None, expiration =None, noncurrentVersionExpiration=None):
        '''
        Constructor
        '''
        self.id = id
        self.prefix = prefix
        self.status = status
        self.expiration = expiration
        self.noncurrentVersionExpiration = noncurrentVersionExpiration