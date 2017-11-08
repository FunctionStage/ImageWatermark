#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel

class GetBucketQuotaResponse(BaseModel):
    #===========================================================================
    # 获取桶配额返回信息
    #===========================================================================
    allowedAttr = {'quota': int}
    

