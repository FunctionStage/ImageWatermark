#!/usr/bin/python
# -*- coding:utf-8 -*-


from com.obs.models.base_model import BaseModel,BASESTRING

class Redirect(BaseModel):
    '''
    classdocs
    '''
    allowedAttr = {'protocol': BASESTRING, 'hostName':BASESTRING, 'replaceKeyPrefixWith':BASESTRING,
                   'replaceKeyWith':BASESTRING, 'httpRedirectCode':int}

    def __init__(self, protocol = None,
                 hostName = None,
                 replaceKeyPrefixWith = None,
                 replaceKeyWith = None,
                 httpRedirectCode = None):
        '''
        Constructor
        '''
        self.protocol = protocol
        self.hostName = hostName
        self.replaceKeyPrefixWith = replaceKeyPrefixWith
        self.replaceKeyWith = replaceKeyWith
        self.httpRedirectCode = httpRedirectCode


