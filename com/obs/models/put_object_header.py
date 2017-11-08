#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING
from com.obs.models.server_side_encryption import SseHeader

class PutObjectHeader(BaseModel):
    #===========================================================================
    #  描述上传对象的请求消息头
    #===========================================================================

    # ===========================================================================
    # 初始化请求参数
    # @md5         对象数据的128位MD5摘要以Base64编码的方式表示。
    # @acl         创建对象时，可以加上此消息头设置对象的权限控制策略，使用的策略为预定义的常用策略，包括：private；public-read；public-read-write；authenticated-read；bucket-owner-read；bucket-owner-full-control。
    # @location    当桶设置了Website配置，可以将获取这个对象的请求重定向到桶内另一个对象或一个外部的URL，MOS将这个值从头域中取出，保存在对象的元数据中。
    # @contentType 对象的类型
    # @sseHeader   服务端加密头信息，用于加密对象
    # ===========================================================================
    allowedAttr = {'md5': BASESTRING, 'acl': BASESTRING, 'location': BASESTRING,
                   'contentType': BASESTRING, 'sseHeader': SseHeader}

 
    def __init__(self, md5=None, acl=None, location=None, contentType=None, sseHeader=None):
        self.md5 = md5
        self.acl = acl
        self.location = location
        self.contentType = contentType
        self.sseHeader = sseHeader