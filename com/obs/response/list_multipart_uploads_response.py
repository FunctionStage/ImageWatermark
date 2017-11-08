#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class ListMultipartUploadsResponse(BaseModel):
    '''
    classdocs
    '''
    allowedAttr = {'bucket': BASESTRING, 'keyMarker': BASESTRING, 'uploadIdMarker':BASESTRING,
                   'nextKeyMarker':BASESTRING, 'nextUploadIdMarker':BASESTRING, 'maxUploads': int,
                   'isTruncated':bool, 'prefix':BASESTRING, 'delimiter':BASESTRING, 'upload': list, 'commonPrefixs': list}

