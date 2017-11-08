#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING
from com.obs.models.date_time import DateTime
from com.obs.models.server_side_encryption import SseHeader

class CopyObjectHeader(BaseModel):
    #===========================================================================
    #  描述复制对象的请求消息头
    #===========================================================================
    # ===========================================================================
    # 初始化请求参数
    # @acl                 复制对象时，可以加上此消息头设置对象的权限控制策略，使用的策略为预定义的常用策略，包括：private；public-read；public-read-write；authenticated-read；bucket-owner-read；bucket-owner-full-control。
    # @directive           此参数用来指定新对象的元数据是从源对象中复制，还是用请求中的元数据替换。有效取值：COPY或REPLACE。
    # @if_match            如果对象的ETag和请求中指定的ETag相同，则返回对象内容，否则的话返回412（precondition failed）。
    # @if_none_match       如果对象的ETag和请求中指定的ETag不相同，则返回对象内容，否则的话返回412（not modified）。
    # @if_modified_since   DateTime对象， 如果对象在请求中指定的时间之后有修改，则返回对象内容；否则的话返回412（not modified）。
    # @if_unmodified_since DateTime对象 ，如果对象在请求中指定的时间之后没有修改，则返回对象内容；否则的话返回412（precondition failed）。
    # @location            当桶设置了Website配置，可以将获取这个对象的请求重定向到桶内另一个对象或一个外部的URL，UDS将这个值从头域中取出，保存在对象的元数据中。
    # @destSseHeader       目标对象服务端加密算法
    # @sourceSseHeader     源对象服务端解密算法，用于解密源对象，当源对象使用SSE-C方式加密时必选
    # ===========================================================================
    allowedAttr = {'acl': BASESTRING, 'directive': BASESTRING, 'if_match': BASESTRING,
                   'if_none_match': BASESTRING, 'if_modified_since': [BASESTRING,DateTime], 'if_unmodified_since': [BASESTRING,DateTime], 'location': BASESTRING,
                   'destSseHeader': SseHeader, 'sourceSseHeader': SseHeader}


    def __init__(self, acl=None, directive=None, if_match=None, if_none_match=None, if_modified_since=None, if_unmodified_since=None, location=None,destSseHeader=None, sourceSseHeader=None):
        self.acl = acl
        self.directive = directive
        self.if_match = if_match
        self.if_none_match = if_none_match
        self.if_modified_since = if_modified_since
        self.if_unmodified_since = if_unmodified_since
        self.location = location
        self.destSseHeader = destSseHeader
        self.sourceSseHeader = sourceSseHeader