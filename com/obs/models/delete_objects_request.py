#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING



class DeleteObjectsRequest(BaseModel):



    #===========================================================================
    # 初始化
    # @quiet   用于指定使用quiet模式，只返回删除失败的对象结果；如果有此字段，则必被置为True，如果为False则被系统忽略掉
    # @objects 待删除的对象列表
    #===========================================================================
    allowedAttr = {'quiet': bool, 'objects': list}

    def __init__(self, quiet=None, objects=None):
        self.quiet = quiet
        self.objects = objects


    def add_object(self, object):
        if self.objects is None:
            self.objects = []
        if isinstance(object, Object):
            self.objects.append(object)

DeleteObjectsRequset = DeleteObjectsRequest

class Object(BaseModel):
    #===========================================================================
    # 初始化
    # @key       待删除的对象Key
    # @versionId 待删除的对象版本号
    #===========================================================================
    allowedAttr = {'key' : BASESTRING, 'versionId' : BASESTRING}

    def __init__(self, key=None, versionId=None):
        self.key = key
        self.versionId = versionId
