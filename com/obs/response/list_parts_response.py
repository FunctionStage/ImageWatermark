#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING,LONG
from com.obs.models.initiator import Initiator 
from com.obs.models.owner import Owner

class Part(BaseModel):

    allowedAttr = {'partNumber': int, 'lastModified': BASESTRING, 'etag': BASESTRING,'size':LONG}

class ListPartsResponse(BaseModel):
    #===========================================================================
    # 列出段返回信息
    #===========================================================================

    allowedAttr = {'bucketName': BASESTRING, 'objectKey': BASESTRING, 'uploadId': BASESTRING, 'initiator': Initiator,
                   'owner': Owner, 'storageClass': BASESTRING, 'partNumberMarker': int, 'nextPartNumberMarker': int, 'maxParts': int,
                   'isTruncated': bool, 'parts': list}



