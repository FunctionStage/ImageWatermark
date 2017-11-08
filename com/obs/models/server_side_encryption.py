#!/usr/bin/python  
# -*- coding:utf-8 -*- 

from com.obs.models.base_model import BaseModel,BASESTRING


#===============================================================================
# 该头域表示进行服务端加密，目前支持SSE-KMS和SSE-C两种方式
#===============================================================================
class SseHeader(BaseModel):
    # ===============================================================================
    # @encryption 加密算法类型，SSE-KMS使用aws:kms, SSE-C使用AES-256
    # @key        加密密钥，SSE-KMS方式下表示使用的主密钥，如果用户没有提供该头域，那么默认的主密钥将会被使用;
    #             SSE-C方式下是由AES算法256-bit或者512-bit的密钥经过base64-encoded的值
    # ===============================================================================
    allowedAttr = {'encryption': BASESTRING, 'key': BASESTRING}


# ===============================================================================
# 该头域表示服务端加密是SSE-C方式,目前仅支持AES256
# ===============================================================================
class SseCHeader(SseHeader):
    @staticmethod
    def getInstance(key,encryption='AES256'):
        return SseCHeader(encryption=encryption, key=key)

#===============================================================================
# 该头域表示服务端加密是SSE-KMS方式,目前仅支持aws:kms
#===============================================================================
class SseKmsHeader(SseHeader):
    @staticmethod
    def getInstance(key=None,encryption='aws:kms'):
        return SseKmsHeader(encryption=encryption, key=key)

