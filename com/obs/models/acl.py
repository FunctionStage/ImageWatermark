#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel
from com.obs.models.grant import Grant
from com.obs.models.owner import Owner

#===============================================================================
# 访问控制列表
#===============================================================================
class ACL(BaseModel):

    #===========================================================================
    # 初始化
    # @owner  资源拥有者
    # @grants 访问控制列表
    #===========================================================================
    allowedAttr = {'owner': Owner, 'grants': list}

    def __init__(self, owner=None, grants=None):
        self.owner = owner  # 资源拥有者
        self.grants = grants  # 访问控制列表
    #===========================================================================
    # 添加授权对象    
    #===========================================================================
    def add_grant(self, grant):
        if self.grants is not None and isinstance(grant, Grant):
            self.grants.append(grant)




