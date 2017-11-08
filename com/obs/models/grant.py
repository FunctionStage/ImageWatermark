#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING
from com.obs.models.grantee import Grantee


class Permission(object):
    READ = 'READ'
    WRITE = 'WRITE'
    READ_ACP = 'READ_ACP'
    WRITE_ACP = 'WRITE_ACP'
    FULL_CONTROL = 'FULL_CONTROL'

class Grant(BaseModel):
    
    #===========================================================================
    # 初始化
    # @grantee    被授权者
    # @permission 权限
    #===========================================================================
    allowedAttr = {'grantee': Grantee, 'permission': BASESTRING}
        

    def __init__(self, grantee = None, permission = None):
        self.grantee = grantee
        self.permission = permission
        


