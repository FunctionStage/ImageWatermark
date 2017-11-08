#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING


class Group(object):
    ALL_USERE = 'AllUsers'
    AUTHENTICATED_USERS = 'AuthenticatedUsers'
    LOG_DELIVERY = 'LogDelivery'

class Grantee(BaseModel):
    
    allowedAttr = {'grantee_id': BASESTRING, 'grantee_name': BASESTRING, 'group': BASESTRING}
 

    def __init__(self, grantee_id = None, grantee_name = None, group = None):
        self.grantee_id = grantee_id
        self.grantee_name = grantee_name
        self.group = group


     
    
    
    
    