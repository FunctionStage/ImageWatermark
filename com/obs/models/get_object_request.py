#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class GetObjectRequest(BaseModel):
    #===========================================================================
    #  描述获取对象的请求
    #===========================================================================

    #===========================================================================
    # 初始化请求参数
    # @content_type                     重写响应中的Content-Type头
    # @contecontent_languagent_type     重写响应中的Content-Language头
    # @expires                          重写响应中的Expires头
    # @cache_control                    重写响应中的Cache-Control头
    # @content_disposition              重写响应中的Content-Disposition头
    # @content_encoding                 重写响应中的Content-Encoding头
    # @versionId                        指定获取对象的版本号
    #===========================================================================
    allowedAttr = {'content_type': BASESTRING, 'content_language': BASESTRING,
                   'expires': BASESTRING, 'cache_control': BASESTRING, 'content_disposition': BASESTRING,
                   'content_encoding': BASESTRING, 'versionId': BASESTRING}

    def __init__(self, content_type=None, content_language=None, expires=None, cache_control=None, content_disposition=None, content_encoding=None, versionId=None):
        self.content_type = content_type
        self.content_language = content_language
        self.expires = expires
        self.cache_control = cache_control
        self.content_disposition = content_disposition
        self.content_encoding = content_encoding
        self.versionId = versionId