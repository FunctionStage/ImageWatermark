#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class CopyObjectResponse(BaseModel):
    #===========================================================================
    # 复制对象返回信息。
    #===========================================================================
    allowedAttr = {'lastModified': BASESTRING, 'eTag': BASESTRING}


