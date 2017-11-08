#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class InitiateMultipartUploadResponse(BaseModel):
    #===========================================================================
    # 初始化上传段任务响应
    #===========================================================================
    allowedAttr = {'bucketName': BASESTRING, 'objectKey': BASESTRING, 'uploadId': BASESTRING}

