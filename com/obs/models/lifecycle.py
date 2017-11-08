#!/usr/bin/python
# -*- coding:utf-8 -*-
from com.obs.models.base_model import BaseModel,BASESTRING

class Lifecycle(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'rule': list}

    def __init__(self, rule=None):
        '''
        Constructor
        '''
        self.rule = rule