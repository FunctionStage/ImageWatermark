#!/usr/bin/python
# -*- coding:utf-8 -*-


from com.obs.models.base_model import BaseModel,BASESTRING

from com.obs.models.condition import Condition
from com.obs.models.redirect import Redirect

class RoutingRule(BaseModel):
    '''
    classdocs
    '''
    allowedAttr = {'condition': Condition, 'redirect': Redirect}

    def __init__(self, condition = None,redirect = None):
        '''
        Constructor
        '''
        self.condition = condition
        self.redirect = redirect