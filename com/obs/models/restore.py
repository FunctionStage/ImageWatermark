#-*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class Restore(BaseModel):

    allowedAttr = {'days': int, 'tier': BASESTRING}

class TierType(object):

    EXPEDITED = 'Expedited'
    STANDARD = 'Standard'
    BULK = 'Bluk'