#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel
from com.obs.models.lifecycle import Lifecycle

class LifecycleResponse(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'lifecycleConfig': Lifecycle}
    

     
         
