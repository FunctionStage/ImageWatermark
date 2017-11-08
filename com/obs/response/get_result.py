#!/usr/bin/python
# -*- coding:utf-8 -*-

import xml.etree.ElementTree as ET
from com.obs.log.Log import *
from com.obs.utils import common_util
from com.obs.utils import convert_util
from com.obs.models.base_model import BaseModel, BASESTRING, IS_PYTHON2
import re
import os
import platform
import traceback
import threading

class RedirectException(Exception):
    pass

class ResponseWrapper(object):
    def __init__(self, conn, res):
        self.conn = conn
        self.res = res

    def __getattr__(self, name):
        return getattr(self.res, name) if self.res else None

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                LOG(ERROR, e)

class ObjectStream(BaseModel):

    allowedAttr = {'response': ResponseWrapper, 'buffer': object, 'size': int}



class GetResult(BaseModel):

    CONTEXT = threading.local()

    CONTEXT.location = None

    PLATFORM = platform.system()

    PATTERN = re.compile('xmlns="http.*?"')

    allowedAttr = {'status': int, 'reason':BASESTRING, 'errorCode': BASESTRING, 'errorMessage': BASESTRING,
                'body': object, 'requestId': BASESTRING, 'hostId': BASESTRING, 'resource': BASESTRING, 'header':list}

    #===========================================================================
    # 接口响应信息。
    #===========================================================================
    def __init__(self, code=None, message=None, status=None, reason=None, body=None, requestId=None, hostId=None, resource=None, header=None):
        #===========================================================================
        # 初始化响应参数。
        # @param status 状态码，用于描述响应类型。
        # @param reason 原因短语，给出了关于状态码的简单的文本描述。
        # @param errorCode 错误响应消息体，错误响应对应的HTTP消息返回码。
        # @param errorMessage 错误响应消息体，具体错误更全面、详细的英文解释。
        # @param body 响应消息元素。
        # @param requestId 本次错误请求的请求ID，用于内部错误定位。。
        # @param hostId 返回该消息的服务端ID。
        # @param resource 该错误相关的桶或对象资源。
        # @param header 响应消息头，当错误发生时，消息头中都会包含： Content-Type: application/xml。
        #===========================================================================
        self.status = status
        self.reason = reason
        self.errorCode = code
        self.errorMessage = message
        self.body = body
        self.requestId = requestId
        self.hostId = hostId
        self.resource = resource
        self.header = header

    @classmethod
    def getNoneResult(cls, message='None Result'):
        return GetResult(code=-1, message=message, status=-1)

    @classmethod
    def get_data(cls, result, objectKey, downloadPath,chuckSize):
        origin_file_path = os.path.join(downloadPath, objectKey[objectKey.rfind('/') + 1:])
        if cls.PLATFORM == 'Windows':
            downloadPath = common_util.safe_trans_to_gb2312(downloadPath)
            objectKey = common_util.safe_trans_to_gb2312(objectKey)
            file_path = os.path.join(downloadPath, objectKey[objectKey.rfind('/') + 1:])
        else:
            file_path = origin_file_path
        if not os.path.exists(downloadPath):
            os.makedirs(downloadPath, 755)
        with open(file_path, 'wb') as f:
            while True:
                chunk = result.read(chuckSize)
                if not chunk:
                    break
                f.write(chunk)
        return origin_file_path

    @classmethod
    def parse_content(cls, conn, objectKey, downloadPath=None, chuckSize=65536, loadStreamInMemory=False):
        if not conn:
            return cls.getNoneResult('connection is null')
        closeConn = True
        try:
            result = conn.getresponse()
            if not result:
                return cls.getNoneResult('response is null')
            if not result.status < 300:
                return cls.__parse_xml(result)

            if loadStreamInMemory:
                LOG(DEBUG, 'loadStreamInMemory is True, read stream into memory')
                buffer = result.read()
                body = ObjectStream(buffer=buffer, size=len(buffer))
            elif downloadPath is None or common_util.toString(downloadPath).strip() == '':
                LOG(DEBUG, 'DownloadPath is null, return conn directly')
                closeConn = False
                body = ObjectStream(response=ResponseWrapper(conn, result))
            else:
                objectKey = common_util.safe_encode(objectKey)
                downloadPath = common_util.safe_encode(downloadPath)
                file_path = cls.get_data(result, objectKey, downloadPath, chuckSize)
                body = 'DownloadPath : %s' % str(file_path)
                LOG(DEBUG, body)
            status = common_util.toInt(result.status)
            reason = result.reason
            header = cls.__parse_headers(dict(result.getheaders()))
            return GetResult(status=status, reason=reason, header=header, body=body)
        except RedirectException as re:
            raise re
        except Exception as e:
            LOG(ERROR, traceback.format_exc())
            return cls.getNoneResult(common_util.toString(e))
        finally:
            if closeConn:
                try:
                    conn.close()
                except Exception as ex:
                    LOG(ERROR, ex)

    @classmethod
    def __parse_headers(cls, headers):
        header = []
        for k, v in headers.items():
            k = common_util.toString(k).lower()
            flag = 0
            if k.startswith(common_util.METADATA_PREFIX):
                k = k[k.index(common_util.METADATA_PREFIX) + len(common_util.METADATA_PREFIX):]
                flag = 1
            elif k.startswith(common_util.AMAZON_HEADER_PREFIX):
                k = k[k.index(common_util.AMAZON_HEADER_PREFIX) + len(common_util.AMAZON_HEADER_PREFIX):]
                flag = 1
            elif k in common_util.ALLOWED_RESPONSE_HTTP_HEADER_METADATA_NAMES:
                flag = 1
            if flag:
                header.append((k, v))
        return header

    @classmethod
    def __parse_xml(cls, result, methodName=None):
        status = common_util.toInt(result.status)
        reason = result.reason
        code = None
        message = None
        body = None
        requestId = None
        hostId = None
        resource = None
        headers = dict(result.getheaders())
        if status == 307 and 'location' in headers:
            location = headers['location']
            LOG(WARNING, 'http code is %d, need to redirect to %s', status, location)
            cls.CONTEXT.location = location
            raise RedirectException('http code is {0}, need to redirect to {1}'.format(status, location))
        else:
            header = cls.__parse_headers(headers)
            xml = result.read()
            if status < 300:
                if methodName is not None:
                    methodName = 'parse' + methodName[:1].upper() + methodName[1:]
                    parseMethod = getattr(convert_util, methodName)
                    if parseMethod is not None:
                        if xml:
                            xml = xml if IS_PYTHON2 else xml.decode('UTF-8')
                            LOG(DEBUG, 'recv Msg:%s', xml)
                            try:
                                search = cls.PATTERN.search(xml)
                                xml = xml if search is None else xml.replace(search.group(), '')
                                body = parseMethod(xml)
                            except AttributeError as e:
                                LOG(ERROR, e)
                        else:
                            body = parseMethod(dict(header))
            elif xml:
                xml = xml if IS_PYTHON2 else xml.decode('UTF-8')
                try:
                    root = ET.fromstring(xml)
                    code = root.find('./Code')
                    code = code.text if code is not None else None
                    message = root.find('./Message')
                    message = message.text if message is not None else None
                    requestId = root.find('./RequestId')
                    requestId = requestId.text if requestId is not None else None
                    hostId = root.find('./HostId')
                    hostId = hostId.text if hostId is not None else None
                    key = root.find('./Key')
                    bucket = root.find('./BucketName')
                    resource = bucket if bucket is not None else key
                    resource = resource.text if resource is not None else None
                except Exception as ee:
                    LOG(WARNING, traceback.format_exc())

        LOG(INFO, 'http response result:status:%d,reason:%s,code:%s,message:%s,headers:%s', status, reason, code,
            message, header)

        return GetResult(code=code, message=message, status=status, reason=reason, body=body, requestId=requestId, hostId=hostId, resource=resource, header=header)
    #===========================================================================
    # 定义静态方法，用来解析xml，最后返回GetResult对象
    #===========================================================================
    @classmethod
    def parse_xml(cls, conn, methodName=None):
        if not conn:
            return cls.getNoneResult('connection is null')
        try:
            result = conn.getresponse()
            if not result:
                return cls.getNoneResult('response is null')
            return cls.__parse_xml(result, methodName)
        except RedirectException as re:
            raise re
        except Exception as e:
            LOG(ERROR, traceback.format_exc())
            return cls.getNoneResult(common_util.toString(e))
        finally:
            try:
                conn.close()
            except Exception as ex:
                LOG(ERROR, ex)



