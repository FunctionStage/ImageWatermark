#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING
from com.obs.models.date_time import DateTime

class Expiration(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'date': [BASESTRING, DateTime], 'days': int}

    def __init__(self, date=None, days=None):
        self.date = date
        self.days = days

class NoncurrentVersionExpiration(BaseModel):

    allowedAttr = {'noncurrentDays': int}

    def __init__(self, noncurrentDays):
        self.noncurrentDays = noncurrentDays