#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class CompletePart(BaseModel):
    allowedAttr = {'partNum': int, 'etag': BASESTRING}

    def __init__(self, partNum=None, etag=None):
        self.partNum = partNum
        self.etag = etag

class CompleteMultipartUploadRequest(BaseModel):
    #===============================================================================
    # 合并段请求。
    #===============================================================================

    #===============================================================================
    #@parts 段列表
    #===============================================================================
    allowedAttr = {'parts': list}

    def __init__(self, parts=None):
        self.parts = parts

    def add_part(self, part):
        if self.parts is None:
            self.parts = []
        if isinstance(part, CompletePart):
            self.parts.append(part)
        


