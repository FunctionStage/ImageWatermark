#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from com.obs.utils.request_format import RequestFormat,PathFormat,SubdomainFormat
from com.obs.models.base_model import LONG, IS_PYTHON2,UNICODE
import hashlib
if IS_PYTHON2:
    import urllib
else:
    import urllib.parse as urllib
import base64


METADATA_PREFIX = 'x-amz-meta-'
AMAZON_HEADER_PREFIX = 'x-amz-'
ALTERNATIVE_DATE_HEADER = 'x-amz-date'
GMT_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
LONG_DATE_FORMAT = '%Y%m%dT%H%M%SZ'
SHORT_DATE_FORMAT = '%Y%m%d'

MIN_BUCKET_LENGTH = 3
MAX_BUCKET_LENGTH = 63

# 存储空间名不能是IP格式
IPv4_REGEX = '^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$'
# DNS子域名格式限制
BUCKET_NAME_REGEX = '^[a-z0-9]([a-z0-9\\-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9\\-]*[a-z0-9])?)*$'

SECURE_PORT = 443
INSECURE_PORT = 80

ALLOWED_RESOURCE_PARAMTER_NAMES = (
        'acl',
        'policy',
        'torrent',
        'logging',
        'location',
        'storageinfo',
        'quota',
        'storagePolicy',
        'requestPayment',
        'versions',
        'versioning',
        'versionId',
        'uploads',
        'uploadId',
        'partNumber',
        'website',
        'notification',
        'lifecycle',
        'deletebucket',
        'delete',
        'cors',
        'restore',
        'tagging',
        'response-content-type',
        'response-content-language',
        'response-expires',
        'response-cache-control',
        'response-content-disposition',
        'response-content-encoding')

ALLOWED_REQUEST_HTTP_HEADER_METADATA_NAMES = (
        'content-type',
        'content-md5',
        'content-length',
        'content-language',
        'expires',
        'origin',
        'cache-control',
        'content-disposition',
        'content-encoding',
        'access-control-request-method',
        'access-control-request-headers',
        'x-default-storage-class',
        'location',
        'date',
        'etag',
        'range',
        'host',
        'if-modified-since',
        'if-unmodified-since',
        'if-match',
        'if-none-match',
        'last-modified',
        'content-range')

ALLOWED_RESPONSE_HTTP_HEADER_METADATA_NAMES = (
        'content-type',
        'content-md5',
        'content-length',
        'content-language',
        'expires',
        'origin',
        'cache-control',
        'content-disposition',
        'content-encoding',
        'x-default-storage-class',
        'location',
        'date',
        'etag',
        'host',
        'last-modified',
        'content-range',
        'x-reserved',
        'access-control-allow-origin',
        'access-control-allow-headers',
        'access-control-max-age',
        'access-control-allow-methods',
        'access-control-expose-headers',
        'connection')


# ==========================================================================
# md5 字符串编码
# @param unencoded    待编码的字符串
# @return md5编码后的字符串
# ==========================================================================
def md5_encode(unencoded):
    m = hashlib.md5()
    unencoded = unencoded if IS_PYTHON2 else unencoded.encode('UTF-8')
    m.update(unencoded)
    return m.digest()

#==========================================================================
# base64编码
# @param unencoded    待编码的字符串
# @return base64编码后的字符串
#==========================================================================
def base64_encode(unencoded):
    encodeestr = base64.b64encode(unencoded, altchars=None)
    return encodeestr if IS_PYTHON2 else encodeestr.decode('UTF-8')

#===========================================================================
# 校验路径方式的存储空间名
# @return bool型值： True或False
#===========================================================================
def validate_bucketname(bucket_name, calling_format):

    if isinstance(calling_format, PathFormat):
        flag = bucket_name and length_in_range(bucket_name, MIN_BUCKET_LENGTH, MAX_BUCKET_LENGTH) and \
               re.match(BUCKET_NAME_REGEX, bucket_name)  # \用于连接下一行字符
        return flag
    return valid_subdomain_bucketname(bucket_name)

def encode_object_key(key):
    return encode_item(key, ',:?/=+&%')

def encode_item(item, safe):
    return urllib.quote(toString(item), safe)


#===========================================================================
# 校验子域名的存储空间
#===========================================================================
def valid_subdomain_bucketname(bucket_name):

    return bucket_name \
            and length_in_range(bucket_name, MIN_BUCKET_LENGTH, MAX_BUCKET_LENGTH) \
            and not re.match(IPv4_REGEX, bucket_name) \
            and re.match(BUCKET_NAME_REGEX, bucket_name)


def safe_trans_to_utf8(item):
    if not IS_PYTHON2:
        return item
    if item is not None:
        item = safe_encode(item)
        try:
            return item.decode('GB2312').encode('UTF-8')
        except:
            return item

def safe_trans_to_gb2312(item):
    if not IS_PYTHON2:
        return item
    if item is not None:
        item = safe_encode(item)
        try:
            return item.decode('UTF-8').encode('GB2312')
        except:
            return item

def safe_encode(item):
    if not IS_PYTHON2:
        return item
    if isinstance(item, UNICODE):
        try:
            item = item.encode('UTF-8')
        except UnicodeDecodeError:
            try:
                item = item.encode('GB2312')
            except:
                item = None
    return item

#==========================================================================
# md5文件编码
# @param file_path   文件路径
# @param size        文件编码段长度
# @param offset      文件起始偏移量
# @return md5编码后的字符串
#==========================================================================
def md5_file_encode_by_size_offset(file_path=None, size=None, offset=None, chuckSize=None):
    if file_path is not None and size is not None and offset is not None:
        m = hashlib.md5()
        with open(file_path, 'rb') as fp:
            CHUNKSIZE = 65536 if chuckSize is None else chuckSize
            fp.seek(offset)
            read_count = 0
            while read_count < size:
                read_size = CHUNKSIZE if size - read_count >= CHUNKSIZE else size - read_count
                data = fp.read(read_size)
                read_count_once = len(data)
                if read_count_once <= 0:
                    break
                m.update(data)
                read_count += read_count_once
        return m.digest()

#===========================================================================
# 检查存储空间的长度
#===========================================================================
def length_in_range(bucket_name, min_len, max_len):
    return len(bucket_name) >= min_len and len(bucket_name) <= max_len

#===========================================================================
# 获取存储空间的调用方式
#===========================================================================
def get_callingformat_for_bucket(desired_format, bucket_name):

    calling_format = desired_format
    if isinstance(calling_format, SubdomainFormat) and not valid_subdomain_bucketname(bucket_name):
        calling_format = RequestFormat.get_pathformat()

    return calling_format


def toBool(item):
    try:
        return True if item is not None and str(item).lower() == 'true' else False
    except Exception:
        return None

def toInt(item):
    try:
        return int(item)
    except Exception:
        return None

def toLong(item):
    try:
        return LONG(item)
    except Exception:
        return None

def toFloat(item):
    try:
        return float(item)
    except Exception:
        return None

def toString(item):
    try:
        return str(item) if item is not None else ''
    except Exception:
        return ''
