#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

from com.obs.models.date_time import DateTime
from com.obs.models.server_side_encryption import SseHeader

class GetObjectHeader(BaseModel):
    #===========================================================================
    #  描述获取对象的请求消息头
    #===========================================================================
    #===========================================================================
    # 初始化请求参数
    # @range                      获取对象时获取在Range范围内的对象内容；如果Range不合法则忽略此字段下载整个对象;Range是一个范围，它的起始值最小为0，最大为对象长度减1
    # @if_modified_since          DateTime对象，如果对象在请求中指定的时间之后有修改，则返回对象内容；否则的话返回304（not modified）
    # @if_unmodified_since        DateTime对象，如果对象在请求中指定的时间之后没有修改，则返回对象内容；否则的话返回412（precondition failed）
    # @if_match                   如果对象的ETag和请求中指定的ETag相同，则返回对象内容，否则的话返回412（precondition failed）
    # @if_none_match              如果对象的ETag和请求中指定的ETag不相同，则返回对象内容，否则的话返回304（not modified）
    # @origin                     预请求指定的跨域请求origin
    # @accessControlRequestHeader 实际请求可以带的HTTP头域
    # @sseHeader                  服务端加密头信息,用于解密对象
    #===========================================================================
    allowedAttr = {'range': BASESTRING, 'if_modified_since': [BASESTRING,DateTime],
                   'if_unmodified_since': [BASESTRING,DateTime], 'if_match': BASESTRING, 'if_none_match': BASESTRING,
                   'origin': BASESTRING, 'accessControlRequestHeader': BASESTRING,'sseHeader': SseHeader}


    def __init__(self, range=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, origin=None,
                 accessControlRequestHeader=None, sseHeader=None):
        self.range = range
        self.if_modified_since = if_modified_since
        self.if_unmodified_since = if_unmodified_since
        self.if_match = if_match
        self.if_none_match = if_none_match
        self.origin = origin
        self.accessControlRequestHeader = accessControlRequestHeader
        self.sseHeader = sseHeader