#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class CompleteMultipartUploadResponse(BaseModel):
    
    #===============================================================================
    # 合并段返回信息。
    #===============================================================================
    allowedAttr = {'location': BASESTRING, 'bucket': BASESTRING,
                   'key': BASESTRING, 'eTag': BASESTRING}
    


