#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel
from com.obs.models.object_version_head import ObjectVersionHead

class ObjectVersions(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'head': ObjectVersionHead, 'versions': list, 'markers': list, 'commonPrefixs': list}

    
    
    
    
    
    