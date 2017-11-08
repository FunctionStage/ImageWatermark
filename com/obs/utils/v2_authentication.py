#!/usr/bin/python  
# -*- coding:utf-8 -*- 

import hashlib
import hmac
import binascii
from com.obs.utils import common_util
from com.obs.log.Log import *
from com.obs.models.base_model import IS_PYTHON2

class V2Authentication(object):
    # ==========================================================================
    # 构造待签名的串，如果过期时间（expires）为空，则使用HTTP头中的Date字段
    # ==========================================================================

    def __init__(self, sk, ak, path_style):
        self.sk = sk
        self.ak = ak
        self.path_style = path_style


    def v2Auth(self, method, bucket, object, path_args, headers, expires=None):
        canonical_string = self.__make_canonicalstring(method, bucket, object, path_args, headers, expires)
        LOG(DEBUG, 'v2 canonical_string: %s' % canonical_string)
        return self.__v2Auth_python2(canonical_string) if IS_PYTHON2 else self.__v2Auth_python3(canonical_string)

    def __v2Auth_python2(self,canonical_string):
        hashed = hmac.new(self.sk, canonical_string, hashlib.sha1)  # 使用sha1算法创建hmac的对象
        encode_canonical = binascii.b2a_base64(hashed.digest())[:-1]  # 获得加密后的字符串，即hash值
        return 'AWS ' + self.ak + ':' + encode_canonical  # 字符串连接

    def __v2Auth_python3(self, canonical_string):
        hashed = hmac.new(self.sk.encode('UTF-8'), canonical_string.encode('UTF-8'), hashlib.sha1)  # 使用sha1算法创建hmac的对象
        encode_canonical = binascii.b2a_base64(hashed.digest())[:-1]  # 获得加密后的字符串，即hash值
        return 'AWS ' + self.ak + ':' + encode_canonical.decode('UTF-8')  # 字符串连接

    def __make_canonicalstring(self, method, bucket_name, key, path_args, headers, expires=None):

        str_list = []
        str_list.append(method + '\n')

        # 添加所有相关的头部字段（Content-MD5, Content-Type, Date和以x-amz开头的），并排序
        interesting_headers = {}  # 使用字典表示
        content_list = ['content-type', 'content-md5', 'date']
        if isinstance(headers, dict):
            for hash_key in headers.keys():
                lk = hash_key.lower()  # headers的key值的小写

                # 忽略不相关的HTTP头字段
                if lk in content_list or lk.startswith(common_util.AMAZON_HEADER_PREFIX):
                    s = headers.get(hash_key)  # 获得headers中的值列表
                    interesting_headers[lk] = ''.join(s)

        keylist = interesting_headers.keys()
        # 如果有amz的时间标记就无需加入原有的date标记
        if common_util.ALTERNATIVE_DATE_HEADER in keylist:
            interesting_headers.setdefault('date', '')

        # 如果过期时间不为空，则将过期时间填入date字段中
        if expires:
            interesting_headers['date'] = expires

        # 这些字段必须要加入，故即使没有设置也要加入
        if not 'content-type' in keylist:
            interesting_headers['content-type'] = ''

        if not 'content-md5' in keylist:
            interesting_headers['content-md5'] = ''

        # 取出字典中的key并进行排序
        keylist = sorted(interesting_headers.keys())


        # 最后加入所有相关的HTTP头部字段 (例如: 所有以x-amz-开头的)
        for k in keylist:
            header_key = str(k)
            if header_key.startswith(common_util.AMAZON_HEADER_PREFIX):
                str_list.append(header_key + ':' + interesting_headers[header_key])
            else:
                str_list.append(interesting_headers[header_key])
            str_list.append('\n')

        URI = ''
        # 使用存储空间名和对象名构建路径
        if bucket_name is not None and bucket_name != '':
            URI += '/'
            URI += bucket_name
            if not self.path_style:
                URI += '/'

        # 对象名不为空，则添加对象名到待签名的字符串中
        if key is not None:
            # 再加入一个反斜杠
            if not URI.endswith('/'):
                URI += '/'
            URI += common_util.encode_object_key(key)

        str_list.append(URI) if URI else str_list.append('/')

        # 最后检查路径参数里是否有ACL，有则加入
        if path_args:
            e1 = '?'
            e2 = '&'
            for path_key, path_value in path_args.items():
                flag = True
                if path_key not in common_util.ALLOWED_RESOURCE_PARAMTER_NAMES:
                    flag = False
                if flag:
                    path_key = common_util.toString(path_key)
                    if path_value is None:
                        e1 += path_key + '&'
                        continue
                    e2 += path_key + '=' + common_util.toString(path_value) + '&'
            e = (e1 + e2).replace('&&', '&').replace('?&', '?')[:-1]
            str_list.append(e)
        return ''.join(item for item in str_list)  # 返回待签名的字符串 