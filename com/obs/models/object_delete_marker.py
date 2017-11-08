#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

from com.obs.models.owner import Owner

class ObjectDeleteMarker(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'key': BASESTRING, 'versionId': BASESTRING, 'isLatest': bool, 'lastModified': BASESTRING,
                    'owner': Owner}