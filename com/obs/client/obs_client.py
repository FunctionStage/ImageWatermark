#!/usr/bin/python  
# -*- coding:utf-8 -*- 

from com.obs.log.log_client import *
from com.obs.log.Log import *
from com.obs.utils.request_format import RequestFormat
from com.obs.utils.request_format import PathFormat
from com.obs.utils import convert_util
from com.obs.utils import common_util
from com.obs.utils.v4_authentication import V4Authentication
from com.obs.utils.v2_authentication import V2Authentication
from com.obs.response.get_result import GetResult, RedirectException
from com.obs.models.restore import Restore
from com.obs.models.date_time import DateTime
from com.obs.models.server_side_encryption import SseCHeader,SseKmsHeader, SseHeader
from com.obs.models.base_model import IS_PYTHON2
from com.obs.models.create_bucket_header import CreateBucketHeader
from com.obs.models.acl import ACL
from com.obs.models.list_multipart_uploads_request import ListMultipartUploadsRequest
from com.obs.models.options import Options
from com.obs.models.get_object_request import GetObjectRequest
from com.obs.models.get_object_header import GetObjectHeader
from com.obs.models.put_object_header import PutObjectHeader
from com.obs.models.copy_object_header import CopyObjectHeader
from com.obs.models.complete_multipart_upload_request import CompleteMultipartUploadRequest


import socket
import ssl
import time
import functools

if IS_PYTHON2:
    from urlparse import urlparse
    import httplib
    import imp
else:
    import http.client as httplib
    from urllib.parse import urlparse


def countTime(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start = time.time()
        try:
            ret = func(*args, **kw)
        except RedirectException as e:
            try:
                ret = func(*args, **kw)
            finally:
                GetResult.CONTEXT.location = None
        LOG(DEBUG, '%s cost %s ms' % (func.__name__ ,int((time.time() - start) * 1000)))
        return ret
    return wrapper



class ObsClient(object):

    DEFAULT_SECURE_PORT = 443
    DEFAULT_INSECURE_PORT = 80

    def __init__(self, access_key_id, secret_access_key, is_secure=True, server=None, signature='v4', region=None, path_style=True, ssl_verify=False,
                 port=None, max_retry_count=5, timeout=20, chuck_size=65536):
        #===========================================================================
        # __init__ 初始化
        # @access_key_id     连接华为S3的AK
        # @secret_access_key 鉴权使用的SK，可用于字符串的签名
        # @is_secure         连接是否使用SSL
        # @server            连接的服务器
        # @signature         鉴权方式 取值为 v2或v4
        # @region            服务器所在区域，当鉴权方式为v4时，必选
        # @path_style        连接请求的格式是否是路径方式，True 是，False 不是
        # @ssl_verify        是否验证服务器CA证书，True 是，False 不是
        # @port              端口号
        # @max_retry_count   HTTP请求最大重试次数
        # @timeout           单次HTTP请求超时时间（单位：秒）
        # @is_crypt          是否将AK,SK加密保存
        # @chuck_size        处理流文件时单次读写的最大字节数
        #
        #===========================================================================
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.is_secure = is_secure
        self.server = server
        self.signature = signature
        self.region = region
        self.path_style = path_style
        self.ssl_verify = ssl_verify
        self.calling_format = RequestFormat.get_pathformat() if self.path_style else RequestFormat.get_subdomainformat()
        self.port = port if port is not None else self.DEFAULT_SECURE_PORT if is_secure else self.DEFAULT_INSECURE_PORT
        self.max_retry_count = max_retry_count
        self.timeout = timeout
        self.chuck_size = chuck_size
        self.initLog()
        self.context = ssl._create_unverified_context() if not self.ssl_verify and hasattr(ssl, '_create_unverified_context') else ssl.create_default_context()


    def initLog(self, log_config=LogConf(), log_name='OBS_LOGGER'):
        self.log_client = LogClient(log_config, log_name)

    def __assert_not_null(self, param, msg):
        param = common_util.safe_encode(param)
        if param is None or str(param).strip() == '':
            raise Exception(msg)

    @countTime
    def createBucket(self, bucketName, header=CreateBucketHeader(), location=None):
        # ===========================================================================
        # 创建存储空间
        # @bucketName     存储空间名.一个用户可以拥有的存储空间的数量不能超过100个。
        # @header         HTTP头
        # @location       存储空间所在区域
        # @return         GetResult
        # ===========================================================================
        self.log_client.log(INFO, 'enter createBucket ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        headers = {}
        if header is not None:
            if header.aclControl:
                headers['x-amz-acl'] = header.aclControl
            if header.storageClass:
                headers['x-default-storage-class'] = header.storageClass

        conn = self.__makePutRequest(bucketName, headers=headers, entity=None if location is None else convert_util.transLocationToXml(location))
        return GetResult.parse_xml(conn)

    @countTime
    def deleteBucket(self, bucketName):
        # ==========================================================================
        # 删除存储空间
        # @bucketName 存储空间名
        # @return     GetResult
        # ==========================================================================
        self.log_client.log(INFO, 'enter deleteBucket ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeDeleteRequest(bucketName, '')
        return GetResult.parse_xml(conn)

    @countTime
    def listBuckets(self):
        # ==========================================================================
        # 罗列用户所有存储空间
        # @return GetResult,GetResult.body: ListBucketsResponse
        # ==========================================================================
        self.log_client.log(INFO, 'enter listBuckets ...')
        conn = self.__makeGetRequest()

        return GetResult.parse_xml(conn, 'listBuckets')

    @countTime
    def headBucket(self, bucketName):
        # ===========================================================================
        # 检查存储空间是否存在
        # @bucketName  待检查的存储空间名
        # @return      GetResult
        # ===========================================================================
        self.log_client.log(INFO, 'enter headBucket ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeHeadRequest(bucketName)

        return GetResult.parse_xml(conn)

    @countTime
    def getBucketMetadata(self, bucketName, origin=None, requestHeaders=None):
        #===========================================================================
        # 获取桶元数据信息
        # @bucketName           桶名称
        # @origin               预请求指定的跨域请求
        # @requestHeaders       实际请求可以带的HTTP头域
        # @return GetResult     获取对象元数据响应
        #===========================================================================
        self.log_client.log(INFO, 'enter getBucketMetadata ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        headers = {}
        if origin:
            headers['Origin'] = common_util.toString(origin)
        _requestHeaders = requestHeaders[0] if isinstance(requestHeaders,list) and len(requestHeaders) == 1 else requestHeaders
        if _requestHeaders:
            headers['Access-Control-Request-Headers'] = common_util.toString(_requestHeaders)
        conn = self.__makeHeadRequest(bucketName, headers=headers)
        result = GetResult.parse_xml(conn)

        if result.status < 300 and not result.errorCode and result.header:
            flag = False
            for k, v in result.header:
                if k == 'x-default-storage-class':
                    flag = True
                    break
            if not flag:
                result.header.append(('x-default-storage-class', 'STANDARD'))
        return result

    @countTime
    def setBucketQuota(self, bucketName, quota):
        # ===========================================================================
        # 更新桶配额
        # @bucketName     桶名
        # @quota          指定桶空间配额值
        # @return         GetResult GetResult.body:GetBucketQuotaResponse 获取桶配额响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter setBucketQuota ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(quota, 'quota is null')
        conn = self.__makePutRequest(bucketName, pathArgs={'quota': None}, entity=convert_util.transQuotaToXml(quota))
        return GetResult.parse_xml(conn)

    @countTime
    def getBucketQuota(self, bucketName):
        #===========================================================================
        # 获取桶配额
        # @bucketName   桶名
        # @return       GetResult GetResult.body:GetBucketQuotaResponse 获取桶配额响应
        #===========================================================================
        self.log_client.log(INFO, 'enter getBucketQuota ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'quota': None})
        return GetResult.parse_xml(conn, 'getBucketQuota')

    @countTime
    def getBucketStorageInfo(self , bucketName):
        #===========================================================================
        # 获取桶存量
        # @bucketName 桶名
        # @return     GetResult GetResult.body:GetBucketStorageInfoResponse 获取桶存量响应
        #===========================================================================
        self.log_client.log(INFO, 'enter getBucketStorageInfo ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'storageinfo': None})
        return GetResult.parse_xml(conn, 'getBucketStorageInfo')

    @countTime
    def setBucketAcl(self, bucketName, acl=ACL(), x_amz_acl=None):
        # ===========================================================================
        # 指定存储空间内写入ACL
        # @bucketName     存储空间名
        # @acl            ACL对象
        # @x_amz_acl      附加头部，Permission对象值
        # @return GetResult
        # ===========================================================================
        self.log_client.log(INFO, 'enter setBucketAcl...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        if acl is not None and len(acl) > 0 and x_amz_acl is not None:
            raise Exception('Both acl and x_amz_acl are set')

        headers = None if x_amz_acl is None else {'x-amz-acl': x_amz_acl}

        entity = None if acl is None or len(acl) == 0 else convert_util.transAclToXml(acl)

        conn = self.__makePutRequest(bucketName,pathArgs={'acl': None}, headers=headers, entity=entity)
        return GetResult.parse_xml(conn)

    @countTime
    def getBucketAcl(self, bucketName):
        # ===========================================================================
        # 获取存储空间的ACL
        # @bucket 存储空间名
        # @return GetResult.body:ACL
        # ===========================================================================
        self.log_client.log(INFO, 'enter getBucketAcl...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'acl': None})

        return GetResult.parse_xml(conn, 'getBucketAcl')

    @countTime
    def setBucketPolicy(self, bucketName, policyJSON):
        # ==========================================================================
        # 获取桶的策略
        # @bucketName       存储空间名
        # @policyJSON       策略信息，JSON格式的字符串
        # @retrun           GetResult
        # ==========================================================================
        self.log_client.log(INFO, 'enter setBucketPolicy ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(policyJSON, 'policyJSON is null')
        conn = self.__makePutRequest(bucketName, pathArgs={'policy' : None}, entity=policyJSON)
        return GetResult.parse_xml(conn)

    @countTime
    def getBucketPolicy(self, bucketName):
        # ==========================================================================
        # 获取桶的策略
        # @bucketName          存储空间名
        # @return              GetResult          GetResult.body:Policy
        # ==========================================================================
        self.log_client.log(INFO, 'enter getBucketPolicy ...')
        self.__assert_not_null(bucketName, 'bucketName is null')

        conn = self.__makeGetRequest(bucketName, pathArgs={'policy' : None})
        return GetResult.parse_xml(conn,'getBucketPolicy')

    @countTime
    def deleteBucketPolicy(self, bucketName):
        # ==========================================================================
        # 删除桶的策略
        # @bucketName         存储空间名
        # @return             GetResult
        # ==========================================================================
        self.log_client.log(INFO, 'enter deleteBucketPolicy ...')
        self.__assert_not_null(bucketName, 'bucketName is null')

        conn = self.__makeDeleteRequest(bucketName, pathArgs={'policy' : None})
        return GetResult.parse_xml(conn)

    @countTime
    def setBucketVersioningConfiguration(self, bucketName, status):
        # ==========================================================================
        # 设置桶的多版本信息
        # @bucketName        存储空间名
        # @status            版本状态Enabled Suspended
        # @retrun            GetResult
        # ==========================================================================
        self.log_client.log(INFO, 'enter setBucketVersioningConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(status, 'status is null')
        conn = self.__makePutRequest(bucketName, pathArgs={'versioning' : None}, entity=convert_util.transVersionStatusToXml(status))

        return GetResult.parse_xml(conn)

    @countTime
    def getBucketVersioningConfiguration(self, bucketName):
        # ==========================================================================
        # 获取桶的多版本信息
        # @bucketName               存储空间名
        # @return                   GetResult         GetResult.body:BucketVesion
        # ==========================================================================
        self.log_client.log(INFO, 'enter getBucketVersioningConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')

        conn = self.__makeGetRequest(bucketName, pathArgs={'versioning' : None})

        return GetResult.parse_xml(conn,'getBucketVersioningConfiguration')

    @countTime
    def listVersions(self, bucketName, version=None):
        # ==========================================================================
        # 获取桶内对象多版本信息
        # @bucketName          存储空间名
        # @version             版本信息
        # @return              GetResult        GetResult.body:ObjectVersions
        # ==========================================================================
        self.log_client.log(INFO, 'enter listVersions ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        path_args = {'versions' : None}
        if version:
            if version.prefix:
                path_args['prefix'] = version.prefix
            if version.key_marker:
                path_args['key-marker'] = version.key_marker
            if version.max_keys:
                path_args['max-keys'] = version.max_keys
            if version.delimiter:
                path_args['delimiter'] = version.delimiter
            if version.version_id_marker:
                path_args['version-id-marker'] = version.version_id_marker


        conn = self.__makeGetRequest(bucketName, pathArgs=path_args)

        return GetResult.parse_xml(conn, 'listVersions')

    @countTime
    def listObjects(self, bucketName, prefix=None, marker=None, max_keys=None, delimiter=None):
        # ===========================================================================
        # 罗列对象.
        # @bucketName     存储空间名
        # @prefix         对象前缀，设置此字段，带该前缀的对象才会返回，可为空
        # @marker         所有返回的对象名的字典序必须大于marker指定的字符串的字典序
        # @max_keys       对象返回的最大个数，输入0默认处理1000个对象，输入大于1000，实际处理1000个，返回MaxKeys为实际输入的值
        # @delimiter      分隔符，前缀（prefix）与分隔符（delimiter）第一次出现之
        #                 间的字符串讲保存到CommonPrefix字段中，返回对象列表中包含CommonPrefix 中字
        #                 符串的对象将不显示。常用的字段有“/”（用于分类文件和文件夹）
        # @return        GetResult. GetResult.body:ListObjectsResponse
        # ===========================================================================
        self.log_client.log(INFO, 'enter listObjects ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        path_args = {}
        if prefix:
            path_args['prefix'] = prefix
        if marker:
            path_args['marker'] = marker
        if delimiter:
            path_args['delimiter'] = delimiter
        if max_keys:
            path_args['max-keys'] = max_keys
        conn = self.__makeGetRequest(bucketName, pathArgs=path_args)
        return GetResult.parse_xml(conn,'listObjects')

    @countTime
    def listMultipartUploads(self, bucketName, multipart=ListMultipartUploadsRequest()):
        # ===========================================================================
        # 列出多段上传任务
        # @bucketName     桶名
        # @multipart      ListMultipartUploadsRequest
        # @return         GetResult,GetResult.body:ListMultipartUploadsResponse
        # ===========================================================================
        self.log_client.log(INFO, 'enter listMultipartUploads ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        path_args = multipart.params_multipart_for_dict_options() if multipart is not None else {'uploads': None}

        conn = self.__makeGetRequest(bucketName, pathArgs=path_args)

        return GetResult.parse_xml(conn,'listMultipartUploads')

    @countTime
    def deleteBucketLifecycleConfiguration(self, bucketName):
        # ==========================================================================
        # 删除桶的生命周期配置
        # @bucketName     存储空间名
        # @return        GetResult
        # ==========================================================================

        self.log_client.log(INFO, 'enter deleteBucketLifecycleConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeDeleteRequest(bucketName, pathArgs={'lifecycle':None})

        return GetResult.parse_xml(conn)

    @countTime
    def setBucketLifecycleConfiguration(self, bucketName, lifecycle):
        # ==========================================================================
        # 获取桶的生命周期配置
        # @bucketName             存储空间名
        # @lifecycle              生命周期配置
        # @return                 GetResult
        # ==========================================================================
        self.log_client.log(INFO, 'enter setBucketLifecycleConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(lifecycle, 'lifecycle is null')

        entity = convert_util.transLifecycleToXml(lifecycle)
        base64_md5 = common_util.base64_encode(common_util.md5_encode(entity))
        headers = {'Content-MD5' : base64_md5}

        conn = self.__makePutRequest(bucketName, pathArgs={'lifecycle':None}, headers=headers, entity=entity)
        return GetResult.parse_xml(conn)

    @countTime
    def getBucketLifecycleConfiguration(self, bucketName):
        # ==========================================================================
        # 获取桶的生命周期配置
        # @bucketName       存储空间名
        # @return           GetResult,GetResult.body：LifecycleResponse
        # ==========================================================================
        self.log_client.log(INFO, 'enter getBucketLifecycleConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')

        conn = self.__makeGetRequest(bucketName, pathArgs={'lifecycle':None})

        return GetResult.parse_xml(conn, 'getBucketLifecycleConfiguration')

    @countTime
    def deleteBucketWebsiteConfiguration(self, bucketName):
        # ==========================================================================
        # 获取桶的网站配置信息
        # @bucketName     桶名
        # @retrun         GetResult
        # ==========================================================================
        self.log_client.log(INFO, 'enter deleteBucketWebsiteConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeDeleteRequest(bucketName, pathArgs={'website':None})
        return GetResult.parse_xml(conn)

    @countTime
    def setBucketWebsiteConfiguration(self, bucketName, website):
        # ==========================================================================
        # 设置桶的网站配置信息
        # @bucketName                    桶名
        # @website                       网络配置信息
        # @return                        GetResult
        # ==========================================================================
        self.log_client.log(INFO, 'enter setBucketWebsiteConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(website, 'website is null')

        conn = self.__makePutRequest(bucketName, pathArgs={'website':None},entity=convert_util.transWebsiteToXml(website))
        return GetResult.parse_xml(conn)

    @countTime
    def getBucketWebsiteConfiguration(self, bucketName):
        # ==========================================================================
        # 获取桶的网站配置信息
        # @param bucketName  桶名
        # @return GetResult  GetResult.body:BucketWebsite
        # ==========================================================================
        self.log_client.log(INFO, 'enter getBucketWebsiteConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'website':None})
        return GetResult.parse_xml(conn, 'getBucketWebsiteConfiguration')

    @countTime
    def setBucketLoggingConfiguration(self, bucketName, logstatus):
        # ==========================================================================
        # 设置桶的日志管理配置
        # @bucketName           存储空间名
        # @logstatus            日志状态信息
        # @return               GetResult
        # ==========================================================================
        self.log_client.log(INFO, 'enter setBucketLoggingConfiguration...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(bucketName, 'logstatus is null')
        conn = self.__makePutRequest(bucketName, pathArgs={'logging':None}, entity=convert_util.transLoggingToXml(logstatus))
        return GetResult.parse_xml(conn)

    @countTime
    def getBucketLoggingConfiguration(self, bucketName):
        # ==========================================================================
        # 获取桶的日志管理配置
        # @bucketName                存储空间名
        # @retrun                    GetResult          GetResult.body:Logging
        # ==========================================================================
        self.log_client.log(INFO, 'enter getbucketLoggingConfiguration ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'logging':None})
        return GetResult.parse_xml(conn,'getBucketLoggingConfiguration')

    @countTime
    def getBucketLocation(self, bucketName):
        # ==========================================================================
        # 获取桶的区域位置
        # @bucketName         存储空间名
        # @return             GetResult         GetResult.body：LocationResponce
        # ==========================================================================
        self.log_client.log(INFO, 'enter getBucketLocation ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'location':None})
        return GetResult.parse_xml(conn, 'getBucketLocation')

    @countTime
    def getBucketTagging(self, bucketName):
        # ===========================================================================
        # 获取桶标签信息
        # @bucketName 桶名
        # @return     GetResult.body:TagInfo对象
        # ===========================================================================
        self.log_client.log(INFO, 'enter getBucketTagging...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'tagging' : None})
        return GetResult.parse_xml(conn, 'getBucketTagging')

    @countTime
    def setBucketTagging(self,bucketName,tagInfo):
        # ===========================================================================
        # 设置桶标签
        # @bucketName 桶名
        # @tagInfo    TagInfo对象
        # @return     GetResult
        # ===========================================================================
        self.log_client.log(INFO, 'enter setBucketTagging...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(tagInfo, 'tagInfo is null')
        entity = convert_util.transTagInfoToXml(tagInfo)
        base64_md5 = common_util.base64_encode(common_util.md5_encode(entity))
        headers = {'Content-MD5': base64_md5}
        conn = self.__makePutRequest(bucketName, pathArgs={'tagging' : None}, headers=headers, entity=entity)
        return GetResult.parse_xml(conn)

    @countTime
    def deleteBucketTagging(self, bucketName):
        # ===========================================================================
        # 删除桶标签
        # @bucketName 桶名
        # @return     GetResult
        # ===========================================================================
        self.log_client.log(INFO, 'enter deleteBucketTagging...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeDeleteRequest(bucketName, pathArgs={'tagging' : None})
        return GetResult.parse_xml(conn)

    @countTime
    def setBucketCors(self, bucketName, corsRuleList):
        # ===========================================================================
        # 设置桶的CORS
        # @bucketName 存储空间名
        # @corsRule   CorsRule对象
        # @return     GetResult
        # ===========================================================================
        self.log_client.log(INFO, 'enter setBucketCors...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(corsRuleList, 'corsRuleList is null')
        entity = convert_util.transCorsRuleToXml(corsRuleList)
        base64_md5 = common_util.base64_encode(common_util.md5_encode(entity))
        headers = {'Content-MD5': base64_md5}
        conn = self.__makePutRequest(bucketName, pathArgs={'cors' : None}, headers=headers, entity=entity)
        return GetResult.parse_xml(conn)

    @countTime
    def deleteBucketCors(self, bucketName):
        # ===========================================================================
        # 删除桶的CORS
        # @bucketName 存储空间名
        # @return     GetResult
        # ===========================================================================
        self.log_client.log(INFO, 'enter deleteBucketCors...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeDeleteRequest(bucketName, pathArgs={'cors' : None})
        return GetResult.parse_xml(conn)

    @countTime
    def getBucketCors(self, bucketName):
        # ===========================================================================
        # 获取桶的CORS
        # @bucketName 存储空间名
        # @return     GetResult.body:CorsRule
        # ===========================================================================
        self.log_client.log(INFO, 'enter getBucketCors...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'cors': None})
        return GetResult.parse_xml(conn,'getBucketCors')

    @countTime
    def optionsBucket(self, bucketName, option=Options()):
        # ===========================================================================
        # OPTIONS桶
        # @bucketName 存储空间名
        # @option     Options对象
        # @return     GetResult.body:OptionResp
        # ===========================================================================
        self.log_client.log(INFO, 'enter optionsBucket...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        headers = {}
        if option is not None:
            if option.origin:
                headers['Origin'] = option.origin
            if option.accessControlRequestMethods:
                headers['Access-Control-Request-Method'] = option.accessControlRequestMethods
            if option.accessControlRequestHeaders:
                headers['Access-Control-Request-Headers'] = option.accessControlRequestHeaders

        conn = self.__makeOptionsRequest(bucketName, headers=headers)
        return GetResult.parse_xml(conn, 'optionsBucket')

    @countTime
    def setBucketNotification(self,bucketName, notification):
        # ===========================================================================
        # 设置桶的通知配置
        # @bucketName   存储空间名
        # @notification Notification对象
        # @return       GetResult
        # ===========================================================================
        self.log_client.log(INFO, 'enter setBucketNotification...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(notification, 'notification is null')
        conn = self.__makePutRequest(bucketName, pathArgs={'notification': None}, entity=convert_util.transNotificationToXml(notification))
        return GetResult.parse_xml(conn)

    @countTime
    def getBucketNotification(self, bucketName):
        # ===========================================================================
        # 获取桶的通知配置
        # @bucketName 存储空间名
        # @return     GetResult.body:Notification对象
        # ===========================================================================
        self.log_client.log(INFO, 'enter getBucketNotification...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        conn = self.__makeGetRequest(bucketName, pathArgs={'notification': None})
        return GetResult.parse_xml(conn, 'getBucketNotification')

    @countTime
    def optionsObject(self, bucketName, objectKey, option=Options()):
        # ===========================================================================
        # OPTIONS桶
        # @bucketName 存储空间名
        # @objectKey  对象名
        # @option     Options对象
        # @return     GetResult.body:OptionResp
        # ===========================================================================
        self.log_client.log(INFO, 'enter optionsObject...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        headers = {}
        if option is not None:
            if option.origin:
                headers['Origin'] = option.origin
            if option.accessControlRequestMethods:
                headers['Access-Control-Request-Method'] = option.accessControlRequestMethods
            if option.accessControlRequestHeaders:
                headers['Access-Control-Request-Headers'] = option.accessControlRequestHeaders

        conn = self.__makeOptionsRequest(bucketName, objectKey, headers=headers)
        return GetResult.parse_xml(conn, 'optionsBucket')

    @countTime
    def getObjectMetadata(self, bucketName, objectKey, versionId=None, sseHeader=SseHeader()):
        #===========================================================================
        # 获取对象的元数据。
        # @bucketName    桶名
        # @objectKey     对象名
        # @versionId     对象的版本号
        # @sseHeader     服务端加密头信息,用于解密对象
        # @return        GetResult    GetResult.header 对象的元数据
        #===========================================================================
        self.log_client.log(INFO, 'enter getObjectMetadata...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        path_args = {}
        if versionId:
            path_args['versionId'] = versionId
        conn = self.__makeHeadRequest(bucketName, objectKey, pathArgs=path_args, headers=self.__setSseHeader(sseHeader, onlySseCHeader=True))
        return GetResult.parse_xml(conn)

    @countTime
    def getObject(self , bucketName, objectKey, downloadPath=None, getObjectRequest=GetObjectRequest(), headers=GetObjectHeader(), loadStreamInMemory=False):
        #===========================================================================
        # 下载对象。
        # @bucketName           桶名
        # @objectKey            对象名
        # @downloadPath         文件下载路径，默认当前文件路径
        # @getObjectRequest     下载对象请求消息
        # @headers              GetObjectHeader,HTTP附加的消息头
        # @loadStreamInMemory   是否将对象流加载到内存
        # @return               GetResult 下载对象响应。
        #===========================================================================
        self.log_client.log(INFO, 'enter getObject ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        pathArgs = {}
        if getObjectRequest is not None and len(getObjectRequest) > 0:
            if getObjectRequest.cache_control is not None:
                pathArgs['response-cache-control'] = getObjectRequest.cache_control
            if getObjectRequest.content_disposition is not None:
                pathArgs['response-content-disposition'] = getObjectRequest.content_disposition
            if getObjectRequest.content_encoding is not None:
                pathArgs['response-content-encoding'] = getObjectRequest.content_encoding
            if getObjectRequest.content_language is not None:
                pathArgs['response-content-language'] = getObjectRequest.content_language
            if getObjectRequest.content_type is not None:
                pathArgs['response-content-type'] = getObjectRequest.content_type
            if getObjectRequest.expires is not None:
                pathArgs['response-expires'] = getObjectRequest.expires
            if getObjectRequest.versionId is not None:
                pathArgs['versionId'] = getObjectRequest.versionId

        _headers = {}
        if headers is not None and len(headers) > 0:
            if headers.range:
                _headers['Range'] = 'bytes=' + headers.range
            if headers.if_modified_since:
                _headers['If-Modified-Since'] = headers.if_modified_since.ToGMTTime() if isinstance(headers.if_modified_since, DateTime) else headers.if_modified_since
            if headers.if_unmodified_since:
                _headers['If-Unmodified-Since'] = headers.if_unmodified_since.ToGMTTime() if isinstance(headers.if_unmodified_since, DateTime) else headers.if_unmodified_since
            if headers.if_match:
                _headers['If-Match'] = headers.if_match
            if headers.if_none_match:
                _headers['If-None-Match'] = headers.if_none_match
            if headers.origin:
                _headers['Origin'] = headers.origin
            if headers.accessControlRequestHeader:
                _headers['Access-Control-Request-Headers'] = headers.accessControlRequestHeader
            if headers.sseHeader:
                self.__setSseHeader(headers.sseHeader,_headers, True)
        conn = self.__makeGetRequest(bucketName, objectKey, pathArgs=pathArgs, headers=_headers)
        return GetResult.parse_content(conn, objectKey, downloadPath, self.chuck_size, loadStreamInMemory)

    @countTime
    def putObject(self, bucketName, objectKey, content, metadata=None, headers=PutObjectHeader()):
        # ===========================================================================
        # 上传内容
        # @bucketName    桶名
        # @objectKey     对象名
        # @content       对象内容
        # @metadata      自定义的元数据
        # @headers       PutObjectHeader,HTTP附加的消息头
        # @return        GetResult     上传内容响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter putObject...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        if content is None:
            raise Exception('content is null')

        _headers = self.__assembleHeadersForPutObject(metadata=metadata, headers=headers)

        conn = self.__makePutRequest(bucketName, objectKey, headers=_headers,
                                     entity=common_util.toString(content))
        return GetResult.parse_xml(conn)

    @countTime
    def postObject(self, bucketName, objectKey, file_path, metadata=None, headers=PutObjectHeader()):
        # ===========================================================================
        # 上传对象
        # @bucketName    桶名
        # @objectKey     对象名
        # @file_path     对象路径
        # @metadata      自定义的元数据
        # @headers       PutObjectHeader,HTTP附加的消息头
        # @return        GetResult    上传对象响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter postObject...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        file_path = common_util.safe_encode(file_path)
        if not os.path.exists(file_path):
            file_path = common_util.safe_trans_to_gb2312(file_path)
            if not os.path.exists(file_path):
                raise Exception('file [{0}] doesnot exist'.format(file_path))

        _flag = os.path.isdir(file_path)

        if _flag:
            results = []
            for file in os.listdir(file_path):  # windows中文文件路径
                file = common_util.safe_encode(file)
                __file_path = os.path.join(file_path, file)
                if not objectKey:
                    key = common_util.safe_trans_to_utf8('{0}/'.format(os.path.split(file_path)[1]) + file)
                else:
                    key = '{0}/'.format(objectKey) + common_util.safe_trans_to_utf8(file)
                result = self.postObject(bucketName, key, __file_path, metadata, headers)
                results.append((key, result))
            return results

        if not objectKey:
            objectKey = os.path.split(file_path)[1]
        _headers = self.__assembleHeadersForPutObject(metadata=metadata, headers=headers)
        _headers['Content-Length'] = common_util.toString(os.path.getsize(file_path))
        conn = self.__makePutRequest(bucketName, objectKey, headers=_headers)
        self.log_client.log(DEBUG, 'send Path:%s' % file_path)
        with open(file_path, 'rb') as f:
            CHUNKSIZE = self.chuck_size
            while True:
                chunk = f.read(CHUNKSIZE)
                if not chunk:
                    break
                conn.send(chunk)

        return GetResult.parse_xml(conn)

    @countTime
    def copyObject(self, sourceBucketName, sourceObjectKey, destBucketName, destObjectKey, metadata=None, headers=CopyObjectHeader(), versionId=None):
        #===========================================================================
        # 复制对象
        # @sourceBucketName 源桶名
        # @sourceObjectKey  源对象名
        # @destBucketName   桶名
        # @destObjectKey    对象名
        # @metadata         自定义元数据
        # @headers          CopyObjectHeader,HTTP附加的消息头
        # @versionId        指定版本的复制对象。
        # @return           GetResult GetResult.body:CopyObjectResponse 复制对象响应。
        #===========================================================================
        self.log_client.log(INFO, 'enter copyObject...')
        self.__assert_not_null(sourceBucketName, 'sourceBucketName is null')
        self.__assert_not_null(sourceObjectKey, 'sourceObjectKey is null')
        self.__assert_not_null(destBucketName, 'destBucketName is null')
        self.__assert_not_null(destObjectKey, 'destObjectKey is null')
        _headers = {}
        if metadata:
            for k, v in metadata.items():
                if not common_util.toString(k).lower().startswith('x-amz-'):
                    k = 'x-amz-meta-' + k
                _headers[k] = v

        copy_source = '/%s/%s' % (sourceBucketName, sourceObjectKey)
        if versionId:
            copy_source += '?versionId=%s' % (versionId)
        _headers['x-amz-copy-source'] = copy_source

        if headers is not None and len(headers) > 0:
            if headers.acl:
                _headers['x-amz-acl'] = headers.acl
            if headers.directive :
                _headers['x-amz-metadata-directive'] = headers.directive
            if headers.if_match:
                _headers['x-amz-copy-source-if-match'] = headers.if_match
            if headers.if_none_match:
                _headers['x-amz-copy-source-if-none-match'] = headers.if_none_match
            if headers.if_modified_since:
                _headers['x-amz-copy-source-if-modified-since'] = headers.if_modified_since.ToGMTTime() if isinstance(headers.if_modified_since, DateTime) else headers.if_modified_since
            if headers.if_unmodified_since:
                _headers['x-amz-copy-source-if-unmodified-since'] = headers.if_unmodified_since.ToGMTTime() if isinstance(headers.if_unmodified_since, DateTime) else headers.if_unmodified_since
            if headers.location:
                _headers['x-amz-website-redirect-location'] = headers.location
            if headers.destSseHeader:
                self.__setSseHeader(headers.destSseHeader, _headers)
            if headers.sourceSseHeader:
                self.__setSourceSseHeader(headers.sourceSseHeader, _headers)
        conn = self.__makePutRequest(destBucketName, destObjectKey, headers=_headers)
        return GetResult.parse_xml(conn, 'copyObject')

    @countTime
    def setObjectAcl(self, bucketName, objectKey, acl=ACL(), versionId=None, aclControl=None):
        # ===========================================================================
        # 修改对象的ACL
        # @bucketName    桶名
        # @objectKey     对象名
        # @acl           需要设置的ACL请求信息
        # @versionId     对象的版本号，标示更改指定版本的对象ACL
        # @aclControl    附加头域x-amz-acl值
        # @return        GetResult    修改对象的ACL响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter setObjectAcl ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        if acl is not None and len(acl) > 0 and aclControl is not None:
            raise Exception('Both acl and aclControl are set')

        path_args = {'acl': None}
        if versionId:
            path_args['versionId'] = common_util.toString(versionId)

        headers = None if aclControl is None else {'x-amz-acl': aclControl}

        entity = None if acl is None or len(acl) == 0 else convert_util.transAclToXml(acl)
        conn = self.__makePutRequest(bucketName, objectKey, pathArgs=path_args, headers=headers, entity=entity)

        return GetResult.parse_xml(conn)

    @countTime
    def getObjectAcl(self, bucketName, objectKey, versionId=None):
        # ===========================================================================
        # 获取对象的ACL信息
        # @bucketName    桶名
        # @objectKey     对象名
        # @versionId     对象的版本号
        # @return        GetResult    GetResult.body:ACL 获取对象的ACL信息响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter getObjectAcl ...')
        self.__assert_not_null(bucketName, 'bucketName is null')

        path_args = {'acl': None}
        if versionId:
            path_args['versionId'] = common_util.toString(versionId)

        conn = self.__makeGetRequest(bucketName, objectKey, pathArgs=path_args)
        return GetResult.parse_xml(conn, 'getObjectAcl')

    @countTime
    def deleteObject(self , bucketName, objectKey, versionId=None):
        #===========================================================================
        # 删除对象
        # @bucketName    桶名
        # @objectKey     对象名
        # @versionId     待删除对象的版本号
        # @return        GetResult     删除对象响应
        #===========================================================================
        self.log_client.log(INFO, 'enter deleteObject ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        path_args = {}
        if versionId:
            path_args['versionId'] = common_util.toString(versionId)
        conn = self.__makeDeleteRequest(bucketName, objectKey, pathArgs=path_args)
        return GetResult.parse_xml(conn)

    @countTime
    def deleteObjects(self, bucketName, deleteObjectsRequest):
        # ===========================================================================
        # 批量删除对象。
        # @bucketName               桶名
        # @deleteObjectsRequset     批量删除对象列表请求
        # @return                   GetResult GetResult.body:DeleteObjectsResponse 批量删除对象响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter deleteObjects ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(deleteObjectsRequest, 'deleteObjectsRequest is null')

        entity = convert_util.transDeleteObjectsRequestToXml(deleteObjectsRequest)
        base64_md5 = common_util.base64_encode(common_util.md5_encode(entity))
        headers = {'Content-MD5': base64_md5}
        conn = self.__makePostRequest(bucketName, pathArgs={'delete': None}, headers=headers, entity=entity)
        return GetResult.parse_xml(conn, 'deleteObjects')

    @countTime
    def restoreObject(self, bucketName, objectKey, days, tier=None, versionId=None):
        #===========================================================================
        # 取货归档存储对象
        # @bucketName 桶名
        # @objectKey  对象名
        # @days       取回对象的保存时间（单位：天），最小值为1，最大值为30
        # @tier       取回选项，支持三种取值：[Expedited|Standard|Bulk]。Expedited表示取回对象耗时1~5分钟，
        #             Standard表示耗时3~5小时，Bulk表示耗时5~12小时。默认取值为Standard
        # @versionId  待取回冷存储对象的版本号
        # @return     GetResult 取回归档存储对象响应
        #===========================================================================
        self.log_client.log(INFO, 'enter restoreObject ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        self.__assert_not_null(days, 'days is null')

        path_args = {'restore': None}
        if versionId:
            path_args['versionId'] = common_util.toString(versionId)

        restore = Restore(days=days, tier=tier)
        entity = convert_util.transRestoreToXml(restore)
        base64_md5 = common_util.base64_encode(common_util.md5_encode(entity))
        headers = {'Content-MD5': base64_md5}
        conn = self.__makePostRequest(bucketName, objectKey, pathArgs=path_args, headers=headers, entity=entity)
        return GetResult.parse_xml(conn)

    @countTime
    def initiateMultipartUpload(self, bucketName, objectKey, acl=None, metadata=None, websiteRedirectLocation=None, contentType=None, sseHeader=SseHeader()):
        # ===========================================================================
        # 初始化多段上传任务。
        # @bucketName              桶名
        # @objectKey               对象名
        # @acl                     ACL控制权限
        # @metadata                对象自定义元数据
        # @websiteRedirectLocation 当桶设置了Website配置，可以将获取这个对象的请求重定向到桶内另一个对象或一个外部的URL，OBS将这个值从头域中取出，保存在对象的元数据中，必须以“/”、“http://”或“https://”开头，长度不超过2K
        # @contentType             对象mime类型
        # @sseHeader               服务端加密头信息，用于加密对象
        # @return                  GetResult              GetResult.body:InitiateMultipartUploadResponse 初始化多段上传任务响应。
        # ==========================================================================
        self.log_client.log(INFO, 'enter initiateMultipartUpload ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        headers = {}
        if acl:
            headers['x-amz-acl'] = acl
        if metadata:
            for k, v in metadata.items():
                if not common_util.toString(k).lower().startswith('x-amz-'):
                    k = 'x-amz-meta-' + k
                headers[k] = v
        if websiteRedirectLocation:
            headers['x-amz-website-redirect-location'] = websiteRedirectLocation
        if contentType:
            headers['Content-Type'] = contentType
        if sseHeader:
            self.__setSseHeader(sseHeader, headers)
        conn = self.__makePostRequest(bucketName, objectKey, pathArgs={'uploads': None}, headers=headers)
        return GetResult.parse_xml(conn, 'initiateMultipartUpload')

    @countTime
    def uploadPart(self, bucketName, objectKey, partNumber, uploadId, object, isFile=False, partSize=None, offset=0, sseHeader=SseHeader(), isAttachMd5 = False):
        # ===========================================================================
        # 上传段
        # @bucketName   桶名
        # @objectKey    对象名
        # @partNumber   上传段的段号
        # @uploadId     多段上传任务的id
        # @object       上传对象路径或对象内容
        # @isFile       传输的是否为文件，True传输文件，False传输元数据
        # @partSize     多段上传任务中某一分段的大小，默认值为文件大小除去offset的剩下字节数，单位字节
        # @offset       多段上传文件任务中某一分段偏移的大小，默认值为0, 单位字节
        # @sseHeader    服务端加密头信息，用于加密对象
        # @isAttachMd5  是否传递MD5值到请求头信息
        # @return       GetResult   上传段响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter uploadPart ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        self.__assert_not_null(partNumber, 'partNumber is null')
        self.__assert_not_null(uploadId, 'uploadId is null')
        self.__assert_not_null(object, 'object is null')

        path_args = {'partNumber': partNumber, 'uploadId': uploadId}
        if isFile:
            file_path = common_util.safe_encode(object)
            if not os.path.exists(file_path):
                file_path = common_util.safe_trans_to_gb2312(file_path)
                if not os.path.exists(file_path):
                    raise Exception('file [{0}] does not exist'.format(file_path))
            file_size = os.path.getsize(file_path)
            offset = common_util.toLong(offset)
            offset = offset if offset is not None and 0 <= offset < file_size else 0
            partSize = common_util.toLong(partSize)
            partSize = partSize if partSize is not None and 0 < partSize <= (file_size - offset) else file_size - offset

            headers = {'Content-Length' : common_util.toString(partSize)}

            if isAttachMd5:
                headers['Content-MD5'] = common_util.base64_encode(common_util.md5_file_encode_by_size_offset(file_path, partSize, offset, self.chuck_size))

            if sseHeader:
                self.__setSseHeader(sseHeader, headers, True)

            conn = self.__makePutRequest(bucketName, objectKey, pathArgs=path_args, headers=headers)
            with open(file_path, 'rb') as f:
                CHUNKSIZE = self.chuck_size
                readCount = 0
                f.seek(offset)
                while readCount < partSize:
                    read_size = CHUNKSIZE if partSize - readCount >= CHUNKSIZE else partSize - readCount
                    chunk = f.read(read_size)
                    readCountOnce = len(chunk)
                    if readCountOnce <= 0:
                        break
                    conn.send(chunk)
                    readCount += readCountOnce
        else:
            entity = common_util.toString(object)
            headers = {}
            if isAttachMd5:
                headers['Content-MD5'] = common_util.base64_encode(common_util.md5_encode(entity))
            if sseHeader:
                self.__setSseHeader(sseHeader, headers, True)
            conn = self.__makePutRequest(bucketName, objectKey, pathArgs=path_args, headers=headers, entity=entity)

        return GetResult.parse_xml(conn)

    @countTime
    def copyPart(self, bucketName, objectKey, partNumber, uploadId, copySource, copySourceRange=None, destSseHeader=SseHeader(), sourceSseHeader=SseHeader()):
        # ===========================================================================
        # 拷贝段
        # @bucketName      桶名
        # @objectKey       对象名
        # @partNumber      上传段的段号
        # @uploadId        多段上传任务的id
        # @copySource      拷贝的源对象
        # @copySourceRange 源对象中待拷贝的段的字节范围（start - end），start为段起始字节，end为段结束字节
        # @destSseHeader   目标对象服务端加密算法
        # @sourceSseHeader 源对象服务端解密算法，用于解密源对象，当源对象使用SSE-C方式加密时必选
        # @return          GetResult      GetResult.body:CopyPartResponse 拷贝段响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter copyPart ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        self.__assert_not_null(partNumber, 'partNumber is null')
        self.__assert_not_null(uploadId, 'uploadId is null')
        self.__assert_not_null(copySource, 'copySource is null')
        path_args = {'partNumber': partNumber, 'uploadId': uploadId}
        headers = {'x-amz-copy-source': copySource}
        if copySourceRange:
            headers['x-amz-copy-source-range'] = 'bytes=' + common_util.toString(copySourceRange)
        if destSseHeader:
            self.__setSseHeader(destSseHeader, headers)
        if sourceSseHeader:
            self.__setSourceSseHeader(sourceSseHeader, headers)
        conn = self.__makePutRequest(bucketName, objectKey, pathArgs=path_args, headers=headers)
        return GetResult.parse_xml(conn, 'copyPart')

    @countTime
    def completeMultipartUpload(self, bucketName, objectKey, uploadId,
                                completeMultipartUploadRequest=CompleteMultipartUploadRequest()):
        # ===========================================================================
        # 合并段
        # @bucketName                     桶名
        # @objectKey                      对象名
        # @uploadId                       多段上传任务的id
        # @completeMultipartUploadRequest 合并段请求
        # @return                         GetResult      GetResult.body:CompleteMultipartUploadResponse 合并段响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter completeMultipartUpload ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        self.__assert_not_null(uploadId, 'uploadId is null')
        self.__assert_not_null(completeMultipartUploadRequest, 'completeMultipartUploadRequest is null')

        conn = self.__makePostRequest(bucketName, objectKey, pathArgs={'uploadId':uploadId},
                                      entity=convert_util.transCompleteMultipartUploadRequestToXml(completeMultipartUploadRequest))
        return GetResult.parse_xml(conn,'completeMultipartUpload')

    @countTime
    def abortMultipartUpload(self, bucketName, objectKey, uploadId):
        # ===========================================================================
        # 取消多段上传任务
        # @bucketName  桶名
        # @objectKey   获取要取消的多段上传任务上传的对象
        # @uploadId    多段上传任务的id
        # @return      GetResult  取消多段上传任务响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter abortMultipartUpload ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        self.__assert_not_null(uploadId, 'uploadId is null')
        conn = self.__makeDeleteRequest(bucketName, objectKey, pathArgs={'uploadId' : uploadId})
        return GetResult.parse_xml(conn)

    @countTime
    def listParts(self, bucketName, objectKey, uploadId, maxParts=None, partNumberMarker=None):
        # ===========================================================================
        # 列出段
        # @bucketName       桶名
        # @objectKey        对象名
        # @uploadId         多段上传任务的id
        # @maxParts         规定在列举已上传段响应中的最大Part数目
        # @partNumberMarker 指定List的起始位置，只有Part Number数目大于该参数的Part会被列出
        # @return           GetResult       GetResult.body:ListPartsResponse 列出段响应
        # ===========================================================================
        self.log_client.log(INFO, 'enter listParts ...')
        self.__assert_not_null(bucketName, 'bucketName is null')
        self.__assert_not_null(objectKey, 'objectKey is null')
        self.__assert_not_null(uploadId, 'uploadId is null')
        path_args = {'uploadId':uploadId}
        if maxParts:
            path_args['max-parts'] = maxParts
        if partNumberMarker:
            path_args['part-number-marker'] = partNumberMarker
        conn = self.__makeGetRequest(bucketName, objectKey, pathArgs=path_args)
        return GetResult.parse_xml(conn, 'listParts')

    def __assembleHeadersForPutObject(self, metadata, headers):
        _headers = {}
        if metadata:
            for k, v in metadata.items():
                if not common_util.toString(k).lower().startswith('x-amz-'):
                    k = 'x-amz-meta-' + k
                _headers[k] = v
        if headers is not None and len(headers) > 0:
            if headers.md5 :
                _headers['Content-MD5'] = headers.md5
            if headers.acl :
                _headers['x-amz-acl'] = headers.acl
            if headers.location :
                _headers['x-amz-website-redirect-location'] = headers.location
            if headers.contentType:
                _headers['Content-Type'] = headers.contentType
            if headers.sseHeader:
                self.__setSseHeader(headers.sseHeader,_headers)
        return _headers

    def __setSourceSseHeader(self, sseHeader, headers=None):
        if headers is None:
            headers = {}
        if isinstance(sseHeader, SseCHeader):
            headers['x-amz-copy-source-server-side-encryption-customer-algorithm'] = sseHeader.encryption
            key = common_util.toString(sseHeader.key).strip()
            headers['x-amz-copy-source-server-side-encryption-customer-key'] = common_util.base64_encode(key)
            headers['x-amz-copy-source-server-side-encryption-customer-key-MD5'] = common_util.base64_encode(common_util.md5_encode(key))
        return headers

    def __setSseHeader(self, sseHeader,headers=None, onlySseCHeader=False):
        if headers is None:
            headers = {}
        if isinstance(sseHeader, SseCHeader):
            headers['x-amz-server-side-encryption-customer-algorithm'] = sseHeader.encryption
            key = common_util.toString(sseHeader.key).strip()
            headers['x-amz-server-side-encryption-customer-key'] = common_util.base64_encode(key)
            headers['x-amz-server-side-encryption-customer-key-MD5'] = common_util.base64_encode(common_util.md5_encode(key))
        if isinstance(sseHeader, SseKmsHeader) and not onlySseCHeader:
            headers['x-amz-server-side-encryption'] = sseHeader.encryption
            if sseHeader.key is not None:
                key = common_util.toString(sseHeader.key).strip()
                if key != '':
                    headers['x-amz-server-side-encryption-aws-kms-key-id'] = key
        return headers

    def __makeOptionsRequest(self, bucketName, objectKey=None, pathArgs=None, headers=None):
        return self.__makeRequest('OPTIONS', bucketName, objectKey, pathArgs, headers)

    def __makeHeadRequest(self, bucketName, objectKey=None, pathArgs=None, headers=None):
        return self.__makeRequest('HEAD', bucketName, objectKey, pathArgs, headers)

    def __makeGetRequest(self, bucketName='', objectKey=None, pathArgs=None, headers=None):
        return self.__makeRequest('GET', bucketName, objectKey, pathArgs, headers)

    def __makeDeleteRequest(self, bucketName, objectKey=None, pathArgs=None, headers=None, entity=None):
        return self.__makeRequest('DELETE', bucketName, objectKey, pathArgs, headers, entity)

    def __makePostRequest(self, bucketName, objectKey=None, pathArgs=None, headers=None, entity=None):
        return self.__makeRequest('POST', bucketName, objectKey, pathArgs, headers, entity)

    def __makePutRequest(self, bucketName, objectKey=None, pathArgs=None, headers=None, entity=None):
        return self.__makeRequest('PUT', bucketName, objectKey, pathArgs, headers, entity)


    def __makeRequest(self, method, bucketName='', objectKey=None, pathArgs=None, headers=None, entity=None):
        start = time.time()
        objectKey = common_util.safe_encode(objectKey)
        calling_format = self.calling_format if common_util.valid_subdomain_bucketname(bucketName) else RequestFormat.get_pathformat()

        if self.is_secure and not isinstance(calling_format, PathFormat) and bucketName.find('.') != -1:
            raise Exception('You are making an SSL connection, however, the bucket contains periods and \
                            the wildcard certificate will not match by default. Please consider using HTTP.')
        path = calling_format.get_url(bucketName, objectKey, pathArgs)

        location = GetResult.CONTEXT.location
        if location:
            location = urlparse(location)
            connect_server = location.hostname
            GetResult.CONTEXT.location = None
        else:
            connect_server = calling_format.get_server(self.server, bucketName)
        headers = self.__rename_headers(headers, method)
        entity = common_util.safe_encode(entity)

        if entity is not None:
            if not isinstance(entity, str):
                entity = common_util.toString(entity)
            if not IS_PYTHON2:
                entity = entity.encode('UTF-8')
            headers['Content-Length'] = len(entity)

        headers['Host'] = connect_server
        header_config = self.__add_auth_headers(headers, method, bucketName, objectKey, pathArgs)
        header_log = header_config.copy()
        header_log['Host'] = '******'
        header_log['Authorization'] = '******'
        self.log_client.log(DEBUG, 'method:%s, path:%s, header:%s', method, path, header_log)
        conn = self.__send_request(connect_server, method, path, header_config, entity)
        self.log_client.log(DEBUG, '%s request cost %s ms for url:%s' % ('https' if self.is_secure else 'http',int((time.time()-start) * 1000), connect_server + path))
        return conn

    # ===========================================================================
    # 为HttpConnection添加可信的HTTP头
    # @headers    将可信HTTP头添加到headers头中，字典型
    # @method     HTTP方法（PUT,GET,DELETE)
    # @bucketName 存储空间名
    # @objectKey  对象名
    # @pathArgs   请求URL中的路径参数
    # ===========================================================================
    def __add_auth_headers(self, headers, method, bucketName, objectKey, pathArgs):
        if IS_PYTHON2:
            imp.acquire_lock()
            try:
                from datetime import datetime
            finally:
                imp.release_lock()
        else:
            from datetime import datetime

        # 如果headers头中不存在Date和Content-Type或其值为空时，则添加
        if 'x-amz-date' in headers:
            headers['Date'] = datetime.strptime(headers['x-amz-date'], common_util.LONG_DATE_FORMAT).strftime(common_util.GMT_DATE_FORMAT)
        elif 'X-Amz-Date' in headers:
            headers['Date'] = datetime.strptime(headers['X-Amz-Date'], common_util.LONG_DATE_FORMAT).strftime(common_util.GMT_DATE_FORMAT)
        elif 'date' not in headers or 'Date' not in headers:
            headers['Date'] = datetime.utcnow().strftime(common_util.GMT_DATE_FORMAT)  # 用当前时间来生成datetime对象

        if 'Content-Type' not in headers and 'content-type' not in headers:
            headers['Content-Type'] = ''

        ak = self.access_key_id
        sk = self.secret_access_key

        if self.signature.lower() == 'v4':
            date = headers['Date'] if 'Date' in headers else headers['date']
            date = datetime.strptime(date, common_util.GMT_DATE_FORMAT)
            shortDate = date.strftime(common_util.SHORT_DATE_FORMAT)
            longDate = date.strftime(common_util.LONG_DATE_FORMAT)
            v4 = V4Authentication(sk, ak, str(self.region) if self.region is not None else '', shortDate, longDate, self.path_style)
            auth = v4.v4Auth(method, bucketName, objectKey, pathArgs, headers)
        else:
            v2 = V2Authentication(sk, ak, self.path_style)
            auth = v2.v2Auth(method, bucketName, objectKey, pathArgs, headers)
        headers['Authorization'] = auth
        return headers

    #===========================================================================
    # 为HttpConnection添加头
    # @headers 需要在HTTP头中添加的字段，key-value格式的字典类型
    # @method  请求的方法类型
    #===========================================================================
    def __rename_headers(self, headers, method):
        new_headers = {}
        if isinstance(headers, dict):
            for k, v in headers.items():
                if k is not None and v is not None:
                    k = str(k).strip()
                    if k.lower() not in common_util.ALLOWED_REQUEST_HTTP_HEADER_METADATA_NAMES and not k.lower().startswith(common_util.AMAZON_HEADER_PREFIX):
                        if method in ('PUT', 'POST'):
                            k = common_util.METADATA_PREFIX + k
                        else:
                            continue
                    new_headers[k] = v if isinstance(v, list) else common_util.encode_item(v, ' ,:?/+=%')
        return new_headers

    def __get_server_connection(self, server):
        if self.is_secure:
            self.log_client.log(DEBUG, 'is ssl_verify: %s', self.ssl_verify)
            return httplib.HTTPSConnection(server, port=self.port, timeout=self.timeout, context=self.context)

        return httplib.HTTPConnection(server, port=self.port, timeout=self.timeout)

    # ===========================================================================
    # 发送请求
    # ===========================================================================
    def __send_request(self, server, method, path, header, entity=None):

        flag = 0
        while True:
            try:
                conn = self.__get_server_connection(server)

                if method == 'OPTIONS' and header is not None:
                    conn.putrequest(method, path)
                    for k, v in header.items():
                        if k == 'Access-Control-Request-Method' and isinstance(v, list):
                            for item in v:
                                conn.putheader('Access-Control-Request-Method', item)
                        elif k == 'Access-Control-Request-Headers' and isinstance(v, list):
                            for item in v:
                                conn.putheader('Access-Control-Request-Headers', item)
                        else:
                            conn.putheader(k, v)
                    conn.endheaders()
                else:
                    conn.request(method, path, headers=header)
            except socket.error as e:
                errno, errstr = sys.exc_info()[:2]
                if errno != socket.timeout or flag >= self.max_retry_count:
                    self.log_client.log(ERROR, 'connect service error, %s' % e)
                    raise e
                flag += 1
                self.log_client.log(DEBUG, 'connect service time out,connect again,connect time:%d', int(flag))
                continue
            break

        if entity is not None:
            conn.send(entity)
        return conn
