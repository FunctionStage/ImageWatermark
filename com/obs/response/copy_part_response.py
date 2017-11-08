#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING
class CopyPartResponse(BaseModel):
    #===========================================================================
    # 复制段返回信息
    #===========================================================================
    allowedAttr = {'modifiedDate': BASESTRING,'etagValue': BASESTRING}

