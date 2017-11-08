#!/usr/bin/python  
# -*- coding:utf-8 -*- 

from com.obs.models.base_model import BaseModel,BASESTRING

class Tag(BaseModel):
    allowedAttr = {'key': BASESTRING, 'value': BASESTRING}

class TagInfo(BaseModel):

    allowedAttr = {'tagSet': list}

    def addTag(self, key, value):
        if self.tagSet is None:
            self.tagSet = []
        self.tagSet.append(Tag(key=key, value=value))
        return self







