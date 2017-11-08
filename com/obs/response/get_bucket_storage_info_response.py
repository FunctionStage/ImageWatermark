#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,LONG

class GetBucketStorageInfoResponse(BaseModel):
    #===========================================================================
    # 获取桶存量返回信息
    #===========================================================================
    allowedAttr = {'size': LONG, 'objectNumber': int}

