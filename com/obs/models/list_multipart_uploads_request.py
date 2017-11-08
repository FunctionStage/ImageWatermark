#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class ListMultipartUploadsRequest(BaseModel):
    '''
    classdocs
    '''
    allowedAttr = {'delimiter': BASESTRING, 'prefix': BASESTRING, 'max_uploads': int, 'key_marker':BASESTRING, 'upload_id_marker': BASESTRING}

    def __init__(self, delimiter = None,prefix = None,max_uploads = None,key_marker = None,upload_id_marker = None):
        '''
        Constructor
        '''
        self.delimiter = delimiter
        self.prefix = prefix
        self.max_uploads = max_uploads
        self.key_marker = key_marker
        self.upload_id_marker = upload_id_marker

    def params_multipart_for_dict_options(self):
        
        args = {}
        args['uploads'] = None
        if self.delimiter:
            args['delimiter'] = self.delimiter
        if self.prefix:
            args['prefix'] = self.prefix
        if self.max_uploads:
            args['max-uploads'] = self.max_uploads
        if self.key_marker:
            args['key-marker'] = self.key_marker
        if self.upload_id_marker:
            args['upload-id-marker'] = self.upload_id_marker
        
        return args 