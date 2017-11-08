#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel
from com.obs.models.redirect_all_request_to import RedirectAllRequestTo
from com.obs.models.index_document import IndexDocument
from com.obs.models.error_document import ErrorDocument

class BucketWebsite(BaseModel):
    '''
    classdocs
    '''

    allowedAttr = {'redirectAllRequestTo': RedirectAllRequestTo, 'indexDocument': IndexDocument,
                   'errorDocument': ErrorDocument, 'routingRules': list}



        