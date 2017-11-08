#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING
#===============================================================================
# 对象拥有者, 在ListEntry中使用
#===============================================================================
class Owner(BaseModel):
    
    #===========================================================================
    # 初始化
    # @owner_id   拥有者ID
    # @owner_name 拥有者用户名
    #===========================================================================
    allowedAttr = {'owner_id': BASESTRING, 'owner_name': BASESTRING}
        
    def __init__(self, owner_id = None, owner_name = None):
        self.owner_id = owner_id
        self.owner_name = owner_name