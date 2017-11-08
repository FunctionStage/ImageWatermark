#!/usr/bin/python
# -*- coding:utf-8 -*-


from com.obs.models.base_model import BaseModel,BASESTRING
from com.obs.models.redirect_all_request_to import RedirectAllRequestTo
from com.obs.models.index_document import IndexDocument
from com.obs.models.error_document import ErrorDocument

class WebsiteConfiguration(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'redirectAllRequestTo': RedirectAllRequestTo, 'indexDocument': IndexDocument, 'errorDocument': ErrorDocument, 'routingRules': list}
    def __init__(self, redirectAllRequestTo=None,
                 indexDocument=None,
                 errorDocument=None,
                 routingRules=None
                 ):
        '''
        Constructor
        '''
        self.redirectAllRequestTo = redirectAllRequestTo
        self.indexDocument = indexDocument
        self.errorDocument = errorDocument
        self.routingRules = routingRules  # RoutingRule的链表