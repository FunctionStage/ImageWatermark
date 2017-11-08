#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class ListObjectsResponse(BaseModel):

    allowedAttr = {'name': BASESTRING, 'prefix': BASESTRING, 'marker': BASESTRING,'delimiter':BASESTRING,
                   'max_keys': int, 'is_truncated': bool, 'next_marker': BASESTRING, 'contents': list, 'commonprefixs': list}





      
