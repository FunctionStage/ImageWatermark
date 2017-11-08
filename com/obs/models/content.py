#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING, LONG
from com.obs.models.owner import Owner
#===============================================================================
# 代表S3 逻辑对象（不包含其真实内容,只包含属性），在ListObjectResponse中使用
#===============================================================================
class Content(BaseModel):

    #===========================================================================
    # 初始化
    # @key          对象的名称
    # @lastmodified 对象最后修改的时间
    # @etag         对象的eTag属性
    # @size         对象大小（单位byte）
    # @owner        对象的拥有者
    # @storageClass 对象存储类型
    #===========================================================================
    allowedAttr = {'key': BASESTRING, 'lastmodified': BASESTRING, 'etag': BASESTRING,
                   'size': LONG, 'owner': Owner, 'storageClass': BASESTRING}
    def __str__(self):
        return self.key
    
    
    
    
    