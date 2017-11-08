#!/usr/bin/python  
# -*- coding:utf-8 -*- 

import xml.etree.ElementTree as ET
from com.obs.response.list_buckets_response import ListBucketsResponse
from com.obs.response.get_bucket_quota_response import GetBucketQuotaResponse
from com.obs.response.get_bucket_storage_info_response import GetBucketStorageInfoResponse
from com.obs.response.object_version_response import ObjectVersions
from com.obs.response.list_objects_response import ListObjectsResponse
from com.obs.response.lifecycle_response import LifecycleResponse
from com.obs.response.bucket_website_response import BucketWebsite
from com.obs.response.location_responce import LocationResponce
from com.obs.response.options_response import OptionsResp
from com.obs.response.delete_objects_response import DeleteObjectsResponse, ErrorResult, DeleteObjectResult
from com.obs.response.list_multipart_uploads_response import ListMultipartUploadsResponse
from com.obs.response.complete_multipart_upload_response import CompleteMultipartUploadResponse
from com.obs.response.initiate_multipart_upload_response import InitiateMultipartUploadResponse
from com.obs.response.copy_object_response import CopyObjectResponse
from com.obs.response.list_parts_response import ListPartsResponse,Part
from com.obs.response.copy_part_response import CopyPartResponse
from com.obs.models.object_version_head import ObjectVersionHead
from com.obs.models.object_version import ObjectVersion
from com.obs.models.object_delete_marker import ObjectDeleteMarker
from com.obs.models.common_prefix import CommonPrefix
from com.obs.models.bucket import Bucket
from com.obs.models.grantee import Group
from com.obs.models.owner import Owner
from com.obs.models.acl import ACL
from com.obs.models.grantee import Grantee
from com.obs.models.grant import Grant
from com.obs.models.policy import Policy
from com.obs.models.content import Content
from com.obs.models.expiration import  Expiration, NoncurrentVersionExpiration
from com.obs.models.rule import Rule
from com.obs.models.lifecycle import Lifecycle
from com.obs.models.condition import Condition
from com.obs.models.redirect import Redirect
from com.obs.models.routing_rule import RoutingRule
from com.obs.models.error_document import ErrorDocument
from com.obs.models.index_document import IndexDocument
from com.obs.models.redirect_all_request_to import RedirectAllRequestTo
from com.obs.models.tag import TagInfo
from com.obs.models.logging import Logging
from com.obs.models.cors_rule import CorsRule
from com.obs.models.notification import Notification, FilterRule
from com.obs.models.initiator import Initiator
from com.obs.models.upload import Upload
from com.obs.models.date_time import DateTime
from com.obs.utils import common_util
from xml import sax
import time

def transLocationToXml(location):
    return ''.join(['<CreateBucketConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">',
                    '<LocationConstraint>', str(location), '</LocationConstraint></CreateBucketConfiguration>'])

def transQuotaToXml(quota):
    str_list = []
    str_list.append('<?xml version="1.0" encoding="UTF-8"?>')
    str_list.append('<Quota xmlns="http://s3.amazonaws.com/doc/2006-03-01/">')
    str_quota = common_util.toString(quota)
    str_list.append('<StorageQuota>' + str_quota + '</StorageQuota>')
    str_list.append('</Quota>')

    return ''.join(str_list)

def transGranteeToXml(grantee):
    str_list = []

    if grantee.group:
        str_list.append('<Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Group">')
        if grantee.group == Group.ALL_USERE:
            str_list.append('<URI>http://acs.amazonaws.com/groups/global/AllUsers</URI>')
        elif grantee.group == Group.AUTHENTICATED_USERS:
            str_list.append('<URI>http://acs.amazonaws.com/groups/global/AuthenticatedUsers</URI>')
        elif grantee.group == Group.LOG_DELIVERY:
            str_list.append('<URI>http://acs.amazonaws.com/groups/s3/LogDelivery</URI>')
        str_list.append('</Grantee>')

    if grantee.grantee_id is not None and grantee.grantee_name is not None:
        str_list.append('<Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">')
        if grantee.grantee_id is not None:
            str_list.append('<ID>' + common_util.toString(grantee.grantee_id) + '</ID>')
        if grantee.grantee_name is not None:
            str_list.append('<DisplayName>' + common_util.toString(grantee.grantee_name) + '</DisplayName>')
        str_list.append('</Grantee>')

    return ''.join(str_list)

def transAclToXml(acl):
    if acl.owner is None:
        raise Exception('Invalid AccessControlList: missing an S3 Owner')

    str_list = []
    str_list.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    str_list.append('<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>')
    str_list.append(common_util.toString(acl.owner.owner_id) + '</ID><DisplayName>' + common_util.toString(acl.owner.owner_name) + '</DisplayName>')
    str_list.append('</Owner><AccessControlList>')

    for grant in acl.grants:
        grantee = grant.grantee
        permission = grant.permission
        str_list.append('<Grant>' + transGranteeToXml(grantee) + '<Permission>' + common_util.toString(permission) + '</Permission></Grant>')

    str_list.append('</AccessControlList></AccessControlPolicy>')

    return ''.join(str_list)

def transVersionStatusToXml(status):
    xml = '<VersioningConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
    xml += '<Status>' + common_util.toString(status) + '</Status>'
    xml += '</VersioningConfiguration>'
    return xml


def transRuleToXml(rule):
    xml_list = []
    xml_list.append('<Rule>')
    id = '<ID>' + common_util.toString(rule.id) + '</ID>'
    xml_list.append(id)
    prefix = '<Prefix>' + common_util.toString(rule.prefix) + '</Prefix>'
    xml_list.append(prefix)
    status = '<Status>' + common_util.toString(rule.status) + '</Status>'
    xml_list.append(status)
    if rule.expiration is not None and (rule.expiration.date is not None or rule.expiration.days is not None):
        xml_list.append('<Expiration>')
        if rule.expiration.date is not None:
            date = rule.expiration.date.ToUTMidTime() if isinstance(rule.expiration.date, DateTime) else rule.expiration.date
            date = '<Date>' + common_util.toString(date) + '</Date>'
            xml_list.append(date)

        if rule.expiration.days is not None:
            days = '<Days>' + common_util.toString(rule.expiration.days) + '</Days>'
            xml_list.append(days)
        xml_list.append('</Expiration>')
    if rule.noncurrentVersionExpiration is not None and rule.noncurrentVersionExpiration.noncurrentDays is not None:
        xml_list.append('<NoncurrentVersionExpiration>')
        days = '<NoncurrentDays>' + common_util.toString(rule.noncurrentVersionExpiration.noncurrentDays) + '</NoncurrentDays>'
        xml_list.append(days)
        xml_list.append('</NoncurrentVersionExpiration>')

    xml_list.append('</Rule>')

    return ''.join(xml_list)

def transLifecycleToXml(lifecycle):
    xml_list = []
    xml_list.append('<LifecycleConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">')
    for item in lifecycle.rule:
        xml_list.append(transRuleToXml(item))
    xml_list.append('</LifecycleConfiguration>')
    return ''.join(xml_list)

def transRedirectAllRequestToXml(redirectAllRequestTo):
    xml_list = []
    if redirectAllRequestTo.hostName is not None:
        name = '<HostName>' + common_util.toString(redirectAllRequestTo.hostName) + '</HostName>'
        xml_list.append(name)
    if redirectAllRequestTo.Protocol is not None:
        prot = '<Protocol>' + common_util.toString(redirectAllRequestTo.protocol) + '</Protocol>'
        xml_list.append(prot)
    return '' if len(xml_list) == 0 else '<RedirectAllRequestsTo>{0}</RedirectAllRequestsTo>'.format(''.join(xml_list))

def transConditionToXml(condition):
    xml_list = []
    if condition.keyPrefixEquals is not None:
        xml_list.append('<KeyPrefixEquals>' + common_util.toString(condition.keyPrefixEquals) + '</KeyPrefixEquals>')
    if condition.httpErrorCodeReturnedEquals is not None:
        xml_list.append('<HttpErrorCodeReturnedEquals>' + common_util.toString(condition.httpErrorCodeReturnedEquals) + '</HttpErrorCodeReturnedEquals>')
    return '' if len(xml_list) == 0 else '<Condition>{0}</Condition>'.format(''.join(xml_list))

def transRedirectToXml(redirect):
    xml_list = []
    if redirect.protocol is not None:
        xml = '<Protocol>' + common_util.toString(redirect.protocol) + '</Protocol>'
        xml_list.append(xml)
    if redirect.hostName is not None:
        xml = '<HostName>' + common_util.toString(redirect.hostName) + '</HostName>'
        xml_list.append(xml)
    if redirect.replaceKeyPrefixWith is not None:
        xml = '<ReplaceKeyPrefixWith>' + common_util.toString(redirect.replaceKeyPrefixWith) + '</ReplaceKeyPrefixWith>'
        xml_list.append(xml)
    if redirect.replaceKeyWith is not None:
        xml = '<ReplaceKeyWith>' + common_util.toString(redirect.replaceKeyWith) + '</ReplaceKeyWith>'
        xml_list.append(xml)
    if redirect.httpRedirectCode is not None:
        xml = '<HttpRedirectCode>' + common_util.toString(redirect.httpRedirectCode) + '</HttpRedirectCode>'
        xml_list.append(xml)
    return '' if len(xml_list) == 0 else '<Redirect>{0}</Redirect>'.format(''.join(xml_list))

def transRoutingRuleToXml(routingRule):
    xml = transConditionToXml(routingRule.condition) if routingRule.condition is not None else ''
    xml += transRedirectToXml(routingRule.redirect) if routingRule.redirect is not None else ''
    return xml

def transWebsiteToXml(website):
    xml_list = []
    xml_list.append('<WebsiteConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">')
    if website.redirectAllRequestTo is not None:
        xml_list.append(transRedirectAllRequestToXml(website.redirectAllRequestTo))
    else:
        if website.indexDocument is not None:
            temp = ''
            if website.indexDocument.suffix is not None:
                temp += '<IndexDocument>'
                temp += '<Suffix>' + common_util.toString(website.indexDocument.suffix) + '</Suffix>'
                temp += '</IndexDocument>'
            xml_list.append(temp)
        if website.errorDocument is not None:
            temp = ''
            if website.errorDocument.key is not None:
                temp = '<ErrorDocument><Key>' + common_util.toString(website.errorDocument.key) + '</Key></ErrorDocument>'
            xml_list.append(temp)
        if website.routingRules is not None and len(website.routingRules) > 0:
            xml_list.append('<RoutingRules>')
            for routingRule in website.routingRules:
                xml_list.append('<RoutingRule>')
                xml_list.append(transRoutingRuleToXml(routingRule))
                xml_list.append('</RoutingRule>')
            xml_list.append('</RoutingRules>')
    xml_list.append('</WebsiteConfiguration>')
    return ''.join(xml_list)


def transTagInfoToXml(tagInfo):
    if not tagInfo.tagSet or len(tagInfo.tagSet) == 0:
        raise Exception('Invalid TagInfo, at least one tag should be specified!')
    temp = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Tagging xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><TagSet>']
    for tag in tagInfo.tagSet:
        temp.append('<Tag><Key>{0}</Key><Value>{1}</Value></Tag>'.format(common_util.safe_encode(tag.key), common_util.safe_encode(tag.value)))
    temp.append('</TagSet></Tagging>')
    return ''.join(temp)

def transLoggingToXml(logging):
    xml_list = []
    xml_list.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_list.append('<BucketLoggingStatus  xmlns="http://doc.s3.amazonaws.com/2006-03-01/">')
    if logging.targetBucket is not None or logging.targetPrefix is not None or (logging.targetGrants is not None and len(logging.targetGrants) > 0):
        xml_list.append('<LoggingEnabled>')
        if logging.targetBucket is not None:
            xml_backet = '<TargetBucket>' + common_util.toString(logging.targetBucket) + '</TargetBucket>'
            xml_list.append(xml_backet)
        if logging.targetPrefix is not None:
            xml_prefix = '<TargetPrefix>' + common_util.toString(logging.targetPrefix) + '</TargetPrefix>'
            xml_list.append(xml_prefix)
        if logging.targetGrants is not None and len(logging.targetGrants) > 0:
            xml_list.append('<TargetGrants>')
            for grant in logging.targetGrants:
                xml_list.append('<Grant>')
                if grant.grantee is not None:
                    xml_list.append(transGranteeToXml(grant.grantee))
                if grant.permission is not None:
                    permission = '<Permission>' + common_util.toString(grant.permission) + '</Permission>'
                    xml_list.append(permission)
                xml_list.append('</Grant>')
            xml_list.append('</TargetGrants>')
        xml_list.append('</LoggingEnabled>')

    xml_list.append('</BucketLoggingStatus>')

    return ''.join(xml_list)

def transCorsRuleToXml(corsRuleList):
    xml = []
    xml.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    xml.append('<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">')
    for cors in corsRuleList:
        xml.append('<CORSRule>')
        if cors.id is not None:
            xml.append('<ID>' + common_util.toString(cors.id) + '</ID>')
        if cors.allowedMethod is not None:
            for v in cors.allowedMethod:
                xml.append('<AllowedMethod>' + common_util.toString(v) + '</AllowedMethod>')
        if cors.allowedOrigin is not None:
            for v in cors.allowedOrigin:
                xml.append('<AllowedOrigin>' + common_util.toString(v) + '</AllowedOrigin>')

        if cors.allowedHeader is not None:
            for v in cors.allowedHeader:
                xml.append('<AllowedHeader>' + common_util.toString(v) + '</AllowedHeader>')
        if cors.maxAgeSecond is not None:
            xml.append('<MaxAgeSeconds>' + common_util.toString(cors.maxAgeSecond) + '</MaxAgeSeconds>')
        if cors.exposeHeader is not None:
            for v in cors.exposeHeader:
                xml.append('<ExposeHeader>' + common_util.toString(v) + '</ExposeHeader>')
        xml.append("</CORSRule>")

    xml.append('</CORSConfiguration>')
    return ''.join(xml)

def transNotificationToXml(notification):
    xml_list = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    xml_list.append('<NotificationConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">')
    if notification is not None and len(notification) > 0:
        xml_list.append('<TopicConfiguration>')
        if notification.id is not None:
            xml_list.append('<Id>{0}</Id>'.format(common_util.toString(notification.id)))
        if isinstance(notification.filterRules, list) and len(notification.filterRules)>0:
            xml_list.append('<Filter><S3Key>')
            for filterRule in notification.filterRules:
                xml_list.append('<FilterRule>')
                xml_list.append('<Name>{0}</Name>'.format(common_util.toString(filterRule.name)))
                xml_list.append('<Value>{0}</Value>'.format(common_util.toString(filterRule.value)))
                xml_list.append('</FilterRule>')
            xml_list.append('</S3Key></Filter>')

        if notification.topic is not None:
            xml_list.append('<Topic>{0}</Topic>'.format(common_util.toString(notification.topic)))
        if isinstance(notification.events,list) and len(notification.events)>0:
            for event in notification.events:
                xml_list.append('<Event>{0}</Event>'.format(common_util.toString(event)))
        xml_list.append('</TopicConfiguration>')
    xml_list.append('</NotificationConfiguration>')
    return ''.join(xml_list)

def transDeleteObjectsRequestToXml(deleteObjectsRequest):
    str_list = []
    str_list.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    str_list.append('<Delete>')
    if deleteObjectsRequest is not None:
        if deleteObjectsRequest.quiet:
            str_list.append('<Quiet>' + common_util.toString(deleteObjectsRequest.quiet).lower() + '</Quiet>')
        if deleteObjectsRequest.objects:
            for obj in deleteObjectsRequest.objects:
                if obj.key is not None:
                    str_list.append('<Object><Key>' + common_util.safe_encode(obj.key) + '</Key>')
                    if obj.versionId is not None:
                        str_list.append('<VersionId>' + common_util.toString(obj.versionId) + '</VersionId>')
                    str_list.append('</Object>')
    str_list.append('</Delete>')

    return ''.join(str_list)

def transRestoreToXml(restore):
    str_list = ['<RestoreRequest xmlns="http://s3.amazonaws.com/doc/2006-03-01/" ><Days>', common_util.toString(restore.days), '</Days>']
    if restore.tier:
        str_list.append('<GlacierJobParameters><Tier>')
        str_list.append(common_util.toString(restore.tier))
        str_list.append('</Tier></GlacierJobParameters>')
    str_list.append('</RestoreRequest>')
    return ''.join(str_list)

def transCompleteMultipartUploadRequestToXml(completeMultipartUploadRequest):
    str_list = []
    if completeMultipartUploadRequest.parts is not None:
        str_list.append('<CompleteMultipartUpload xmlns="http://s3.amazonaws.com/doc/2006-03-01/">')
        for obj in completeMultipartUploadRequest.parts:
            str_list.append('<Part><PartNumber>' + common_util.toString(obj.partNum) + '</PartNumber>')
            str_list.append('<ETag>' + common_util.toString(obj.etag) + '</ETag></Part>')

        str_list.append('</CompleteMultipartUpload>')

    return ''.join(str_list)

def UTCToLocal(strUTC):
    if strUTC is None:
        return None

    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    CST_FORMAT = '%Y/%m/%d %H:%M:%S'

    gmt_time = time.strptime(common_util.toString(strUTC), date_format)

    cst_time = time.localtime(time.mktime(gmt_time) - time.timezone)
    dt = time.strftime(CST_FORMAT, cst_time)
    return dt

def parseGrants(grants):
    grant_list = []
    if grants is not None:
        ns = '{http://www.w3.org/2001/XMLSchema-instance}'
        for grant in grants:
            if grant.find('./Grantee').attrib.get('{0}type'.format(ns)) == 'Group':
                group1 = grant.find('./Grantee/URI')
                if group1 is not None:
                    group1 = group1.text
                    group1 = group1[group1.rfind('/') + 1:]
                grantee = Grantee(group=group1)
            elif grant.find('./Grantee').attrib.get('{0}type'.format(ns)) == 'CanonicalUser':
                owner_id = grant.find('./Grantee/ID')
                owner_id = owner_id.text if owner_id is not None else None
                owner_name = grant.find('./Grantee/DisplayName')
                owner_name = owner_name.text if owner_name is not None else None
                grantee = Grantee(grantee_id=owner_id, grantee_name=owner_name)

            permission = grant.find('./Permission')
            permission = permission.text if permission is not None else None
            cur_grant = Grant(grantee=grantee, permission=permission)
            grant_list.append(cur_grant)
    return grant_list

def parseGetBucketAcl(xml):
    root = ET.fromstring(xml)
    owner_id = root.find('.//ID')
    owner_id = owner_id.text if owner_id is not None else None
    owner_name = root.find('.//DisplayName')
    owner_name = owner_name.text if owner_name is not None else None
    owner = Owner(owner_id=owner_id, owner_name=owner_name)  # 创建Owner对象
    grants = root.findall('./AccessControlList/Grant')
    return ACL(owner=owner, grants=parseGrants(grants))  # 返回ACL的对象

def parseGetObjectAcl(xml):
    return parseGetBucketAcl(xml)

def parseGetBucketQuota(xml):
    root = ET.fromstring(xml)
    quota = root.find('.//StorageQuota')
    quota = quota.text if quota is not None else None
    return GetBucketQuotaResponse(quota=common_util.toInt(quota))  # 返回GetBucketQuotaResponse的对象

def parseGetBucketStorageInfo(xml):
    root = ET.fromstring(xml)
    size = root.find('.//Size')
    size = size.text if size is not None else None
    objectNumber = root.find('.//ObjectNumber')
    objectNumber = objectNumber.text if objectNumber is not None else None
    return GetBucketStorageInfoResponse(size=common_util.toLong(size), objectNumber=common_util.toInt(objectNumber))  # 返回GetBucketStorageInfoResponse的对象

def parseListBuckets(xml):
    root = ET.fromstring(xml)  # 获取xml文件的根节点root
    owner_id = root.find('.//ID')
    owner_id = owner_id.text if owner_id is not None else None
    owner_name = root.find('.//DisplayName')
    owner_name = owner_name.text if owner_name is not None else None
    owner = Owner(owner_id=owner_id, owner_name=owner_name)  # 创建Owner对象

    buckets = root.find('Buckets').findall('Bucket')
    entries = []

    for bucket in buckets:
        name = bucket.find('Name')  # 获取bucket的名称
        name = name.text if name is not None else None
        d = bucket.find('CreationDate') # 获取bucket的创建日期
        d = d.text if d is not None else None
        create_date = UTCToLocal(d)  # 将创建日期转换为当地时间
        curr_bucket = Bucket(name=name, create_date=create_date)  # 创建bucket对象
        entries.append(curr_bucket)  # 向entries列表中添加bucket对象
    return ListBucketsResponse(buckets=entries, owner=owner)  # 返回ListBucketsResponse的对象


def parseGetBucketPolicy(jsonStr):
    return Policy(policyJSON = jsonStr)

def parseGetBucketVersioningConfiguration(xml):
    root = ET.fromstring(xml)
    status = root.find('./Status')
    return status.text if status is not None else None

def parseListVersions(xml):

    root = ET.fromstring(xml)
    Name = root.find('./Name')
    Name =  Name.text if Name is not None else None
    Prefix = root.find('./Prefix')
    Prefix = Prefix.text if Prefix is not None else None
    KeyMarker = root.find('./KeyMarker')
    KeyMarker = KeyMarker.text if KeyMarker is not None else None
    VersionIdMarker = root.find('./VersionIdMarker')
    VersionIdMarker = VersionIdMarker.text if VersionIdMarker is not None else None
    NextKeyMarker = root.find('./NextKeyMarker')
    NextKeyMarker = NextKeyMarker.text if NextKeyMarker is not None else None
    NextVersionIdMarker = root.find('./NextVersionIdMarker')
    NextVersionIdMarker = NextVersionIdMarker.text if NextVersionIdMarker is not None else None
    MaxKeys = root.find('./MaxKeys')
    MaxKeys = MaxKeys.text if MaxKeys is not None else None
    IsTruncated = root.find('./IsTruncated')
    IsTruncated = IsTruncated.text if IsTruncated is not None else None

    head = ObjectVersionHead(name=Name, prefix=Prefix, keyMarker=KeyMarker, versionIdMarker=VersionIdMarker,
                             nextKeyMarker=NextKeyMarker, nextVersionIdMarker=NextVersionIdMarker, maxKeys=common_util.toInt(MaxKeys),
                             isTruncated=common_util.toBool(IsTruncated))

    versions = root.findall('./Version')
    version_list = []
    for version in versions:
        Key = version.find('./Key')
        Key = Key.text if Key is not None else None
        VersionId = version.find('./VersionId')
        VersionId = VersionId.text if VersionId is not None else None
        IsLatest = version.find('./IsLatest')
        IsLatest = IsLatest.text if IsLatest is not None else None
        LastModified = version.find('./LastModified')
        LastModified = LastModified.text if LastModified is not None else None
        ETag = version.find('./ETag')
        ETag = ETag.text if ETag is not None else None
        Size = version.find('./Size')
        Size = Size.text if Size is not None else None
        owner = version.find('./Owner')
        Owners = None
        if owner is not None:
            ID = version.find('.//ID')
            ID = ID.text if ID is not None else None
            DisplayName = version.find('.//DisplayName')
            DisplayName = DisplayName.text if DisplayName is not None else None
            Owners = Owner(owner_id=ID, owner_name=DisplayName)

        StorageClass = version.find('./StorageClass')
        StorageClass = StorageClass.text if StorageClass is not None else None

        Version = ObjectVersion(key=Key, versionId=VersionId, isLatest=common_util.toBool(IsLatest), lastModified=UTCToLocal(LastModified), eTag=ETag, size=common_util.toLong(Size), owner=Owners,
                                storageClass=StorageClass)
        version_list.append(Version)

    markers = root.findall('./DeleteMarker')
    marker_list = []
    for marker in markers:
        Key = marker.find('./Key')
        Key = Key.text if Key is not None else None
        VersionId = marker.find('./VersionId')
        VersionId = VersionId.text if VersionId is not None else None
        IsLatest = marker.find('./IsLatest')
        IsLatest = IsLatest.text if IsLatest is not None else None
        LastModified = marker.find('./LastModified')
        LastModified = LastModified.text if LastModified is not None else None
        owner = marker.find('./Owner')
        Owners = None
        if owner is not None:
            ID = marker.find('.//ID')
            ID = ID.text if ID is not None else None
            DisplayName = marker.find('.//DisplayName')
            DisplayName = DisplayName.text if DisplayName is not None else None
            Owners = Owner(owner_id=ID, owner_name=DisplayName)

        Marker = ObjectDeleteMarker(key=Key, versionId=VersionId, isLatest=common_util.toBool(IsLatest), lastModified=UTCToLocal(LastModified), owner=Owners)
        marker_list.append(Marker)

    prefixs = root.findall('./CommonPrefixes')
    prefix_list = []
    for prefix in prefixs:
        Prefix = prefix.find('./Prefix')
        Prefix = Prefix.text if Prefix is not None else None
        Pre = CommonPrefix(prefix=Prefix)
        prefix_list.append(Pre)
    ret = ObjectVersions(head=head, markers=marker_list, commonPrefixs=prefix_list)
    ret.versions=version_list
    return ret

def find_item(root, itemname):
    result = root.find(itemname)
    return result.text if result is not None else None

def parseListObjects(xml):
    root = ET.fromstring(xml)  # 获取xml文件的根节点root

    key_entries = []
    commonprefix_entries = []

    name = root.find('Name')
    name = name.text if name is not None else None
    prefix = find_item(root, 'Prefix')
    marker = find_item(root, 'Marker')
    delimiter = find_item(root, 'Delimiter')
    max_keys = find_item(root, 'MaxKeys')
    is_truncated = find_item(root, 'IsTruncated')
    next_marker = find_item(root, 'NextMarker')

    # 获取对象key的相关信息，在Contents节点中
    contents = root.findall('Contents')
    if contents is not None:
        for node in contents:
            key = find_item(node, 'Key')
            lastmodified = find_item(node, 'LastModified')
            etag = find_item(node, 'ETag')
            size = find_item(node, 'Size')
            storage = find_item(node, 'StorageClass')

            # 获取Owner相关信息
            owner_id = find_item(node, './/ID')
            owner_name = find_item(node, './/DisplayName')
            owner = Owner(owner_id=owner_id, owner_name=owner_name)  # 创建Owner对象
            key_entry = Content(key=key, lastmodified=UTCToLocal(lastmodified), etag=etag, size=common_util.toLong(size), owner=owner, storageClass=storage)
            key_entries.append(key_entry)  # 将对象添加到对象列表中

    # 获取CommonPrefixes的相关信息
    prefixes = root.findall('CommonPrefixes')
    if prefixes is not None:
        for p in prefixes:
            pre = find_item(p, 'Prefix')
            commonprefix = CommonPrefix(prefix=pre)
            commonprefix_entries.append(commonprefix)
    # 返回ListObjectsResponse的对象
    return ListObjectsResponse(name=name, prefix=prefix, marker=marker, delimiter=delimiter, max_keys=common_util.toInt(max_keys),
                               is_truncated=common_util.toBool(is_truncated), next_marker=next_marker, contents=key_entries, commonprefixs=commonprefix_entries)



def parseGetBucketLifecycleConfiguration(xml):
    root = ET.fromstring(xml)
    rules = root.findall('./Rule')
    entries = []
    for rule in rules:
        id = rule.find('./ID')
        id = id.text if id is not None else None
        prefix = rule.find('./Prefix')
        prefix = prefix.text if prefix is not None else None
        status = rule.find('./Status')
        status = status.text if status is not None else None
        expira = rule.find('./Expiration')
        expiration = None
        if expira is not None:
            d = expira.find('./Date')
            date = UTCToLocal(d.text) if d is not None else None  # UTC时间转当地时间
            day = expira.find('./Days')
            days = common_util.toInt(day.text) if day is not None else None
            expiration = Expiration(date=date, days=days)

        nocurrentExpira = rule.find('./NoncurrentVersionExpiration')
        noncurrentVersionExpiration = NoncurrentVersionExpiration(noncurrentDays=common_util.toInt(nocurrentExpira.find('./NoncurrentDays').text)) if nocurrentExpira is not None else None

        Rules = Rule(id=id, prefix=prefix, status=status, expiration=expiration, noncurrentVersionExpiration=noncurrentVersionExpiration)
        entries.append(Rules)  # 向entries列表中添加bucket对象

    lifecycle = Lifecycle(rule=entries)
    return LifecycleResponse(lifecycleConfig=lifecycle)


def parseGetBucketWebsiteConfiguration(xml):
    root = ET.fromstring(xml)
    redirectAll = None
    redirectAllRequestTo = root.find('./RedirectAllRequestsTo')
    if redirectAllRequestTo is not None:
        hostname = root.find('.//HostName')
        hostname = common_util.toString(hostname.text) if hostname is not None else None
        protocol = root.find('.//Protocol')
        protocol = common_util.toString(protocol.text) if protocol is not None else None
        redirectAll = RedirectAllRequestTo(hostName=hostname, protocol=protocol)

    index = None
    indexDocument = root.find('./IndexDocument')
    if indexDocument is not None:
        Suffix = root.find('.//Suffix')
        Suffix =  common_util.toString(Suffix.text) if Suffix is not None else None
        index = IndexDocument(suffix=Suffix)

    error = None
    errorDocument = root.find('./ErrorDocument')
    if errorDocument is not None:
        Key = root.find('.//Key')
        Key = common_util.toString(Key.text) if Key is not None else None
        error = ErrorDocument(key=Key)

    routs = None
    routingRules = root.findall('./RoutingRules/RoutingRule')
    if routingRules is not None and len(routingRules) > 0:
        routs = []
        for rout in routingRules:
            KeyPrefixEquals = rout.find('.//Condition/KeyPrefixEquals')
            KeyPrefixEquals = common_util.toString(KeyPrefixEquals.text) if KeyPrefixEquals is not None else None
            HttpErrorCodeReturnedEquals = rout.find(
                './/Condition/HttpErrorCodeReturnedEquals')
            HttpErrorCodeReturnedEquals = common_util.toInt(HttpErrorCodeReturnedEquals.text) if HttpErrorCodeReturnedEquals is not None else None

            condition = Condition(keyPrefixEquals=KeyPrefixEquals, httpErrorCodeReturnedEquals=HttpErrorCodeReturnedEquals)

            Protocol = rout.find('.//Redirect/Protocol')
            Protocol = common_util.toString(Protocol.text) if Protocol is not None else None
            HostName = rout.find('.//Redirect/HostName')
            HostName = common_util.toString(HostName.text) if HostName is not None else None
            ReplaceKeyPrefixWith = rout.find('.//Redirect/ReplaceKeyPrefixWith')
            ReplaceKeyPrefixWith = common_util.toString(ReplaceKeyPrefixWith.text) if ReplaceKeyPrefixWith is not None else None
            ReplaceKeyWith = rout.find('.//Redirect/ReplaceKeyWith')
            ReplaceKeyWith = common_util.toString(ReplaceKeyWith.text) if ReplaceKeyWith is not None else None
            HttpRedirectCode = rout.find('.//Redirect/HttpRedirectCode')
            HttpRedirectCode = common_util.toInt(HttpRedirectCode.text) if HttpRedirectCode is not None else None

            redirect = Redirect(protocol=Protocol, hostName=HostName, replaceKeyPrefixWith=ReplaceKeyPrefixWith, replaceKeyWith=ReplaceKeyWith,
                                httpRedirectCode=HttpRedirectCode)
            routingRule = RoutingRule(condition=condition, redirect=redirect)
            routs.append(routingRule)

    return BucketWebsite(redirectAllRequestTo=redirectAll, indexDocument=index, errorDocument=error, routingRules=routs)


class _TagInfoHandler(sax.ContentHandler):

    def startElement(self,name, attrs):
        self.__currentName = name
        if name == 'Tag':
            self.__tag = {}

    def endElement(self,name):
        if name == 'Tag' and 'Key' in self.__tag and 'Value' in self.__tag:
            self.__result.addTag(self.__tag['Key'], self.__tag['Value'])

    def getResult(self):
        return self.__result

    def startDocument(self):
        self.__result = TagInfo()

    def characters(self, content):
        if self.__currentName == 'Key':
            self.__tag['Key'] = common_util.safe_encode(content)
        elif self.__currentName == 'Value':
            self.__tag['Value'] = common_util.safe_encode(content)

def parseGetBucketTagging(xml):
    handler = _TagInfoHandler()
    sax.parseString(xml, handler)
    return handler.getResult()


def parseGetBucketLoggingConfiguration(xml):
    root = ET.fromstring(xml)
    TargetBucket = root.find('.//TargetBucket')
    bucket = common_util.toString(TargetBucket.text) if TargetBucket is not None else None
    TargetPrefix = root.find('.//TargetPrefix')
    prefix = common_util.toString(TargetPrefix.text) if TargetPrefix is not None else None

    grants = root.findall('.//TargetGrants/Grant')
    return Logging(targetBucket=bucket, targetPrefix=prefix, targetGrants=parseGrants(grants))

def parseGetBucketLocation(xml):
    root = ET.fromstring(xml)
    location = root.find('./LocationConstraint')
    location = common_util.toString(location.text) if location is not None else None
    return LocationResponce(location=location)

def parseGetBucketCors(xml):
    root = ET.fromstring(xml)
    corsList = []
    rules = root.findall('./CORSRule')
    if rules is not None:
        for rule in rules:
            id = rule.find('./ID')
            id = common_util.toString(id.text) if id is not None else None
            maxAgeSecond = rule.find('./MaxAgeSeconds')
            maxAgeSecond = common_util.toInt(maxAgeSecond.text) if maxAgeSecond is not None else None

            method = rule.findall('./AllowedMethod')
            allowMethod = []
            if method is not None:
                for v in method:
                    allowMethod.append(common_util.toString(v.text))
            allowedOrigin = []
            method = rule.findall('./AllowedOrigin')
            if method is not None:
                for v in method:
                    allowedOrigin.append(common_util.toString(v.text))
            allowedHeader = []
            method = rule.findall('./AllowedHeader')
            if method is not None:
                for v in method:
                    allowedHeader.append(common_util.toString(v.text))
            exposeHeader = []
            method = rule.findall('./ExposeHeader')
            if method is not None:
                for v in method:
                    exposeHeader.append(common_util.toString(v.text))

            corsList.append(CorsRule(id=id, allowedMethod=allowMethod, allowedOrigin=allowedOrigin, allowedHeader=allowedHeader, maxAgeSecond=maxAgeSecond, exposeHeader=exposeHeader))
    return corsList


def parseOptionsBucket(headers):
    option = OptionsResp()
    option.accessContorlAllowOrigin = headers.get('access-control-allow-origin')
    option.accessContorlAllowHeaders = headers.get('access-control-allow-headers')
    option.accessContorlAllowMethods = headers.get('access-control-allow-methods')
    option.accessContorlExposeHeaders = headers.get('access-control-expose-headers')
    option.accessContorlMaxAge = common_util.toInt(headers.get('access-control-max-age'))
    return option


def parseGetBucketNotification(xml):
    notification = Notification()
    root = ET.fromstring(xml)
    id = root.find('.//Id')
    notification.id = common_util.toString(id.text) if id is not None else None
    topic = root.find('.//Topic')
    notification.topic = common_util.toString(topic.text) if topic is not None else None
    event_list = []

    events = root.findall('.//Event')
    if events is not None:
        for event in events:
            event_list.append(common_util.toString(event.text))

    notification.events = event_list
    filterRule_list = []
    filterRules = root.findall('.//Filter/S3Key/FilterRule')
    if filterRules is not None:
        for filterRule in filterRules:
            name = filterRule.find('./Name')
            value = filterRule.find('./Value')
            fr = FilterRule(name=common_util.toString(name.text) if name is not None else None, value=common_util.toString(value.text)
                            if value is not None else None)
            filterRule_list.append(fr)
    notification.filterRules = filterRule_list
    return notification

def parseDeleteObjects(xml):
    root = ET.fromstring(xml)
    deleted_list = []
    error_list = []
    deleteds = root.findall('./Deleted')
    if deleteds:
        for d in deleteds:
            key = d.find('./Key')
            key = common_util.toString(key.text) if key is not None else None
            deleteMarker = d.find('./DeleteMarker')
            deleteMarker = common_util.toBool(deleteMarker.text) if deleteMarker is not None else None
            deleteMarkerVersionId = d.find('./DeleteMarkerVersionId')
            deleteMarkerVersionId = common_util.toString(deleteMarkerVersionId.text) if deleteMarkerVersionId is not None else None
            deleted_list.append(DeleteObjectResult(key=key, deleteMarker=deleteMarker, deleteMarkerVersionId=deleteMarkerVersionId))
    errors = root.findall('./Error')
    if errors:
        for e in errors:
            _key = e.find('./Key')
            _key = common_util.toString(_key.text) if _key is not None else None
            _code = e.find('./Code')
            _code = common_util.toString(_code.text) if _code is not None else None
            _message = e.find('./Message')
            _message = common_util.toString(_message.text) if _message is not None else None
            error_list.append(ErrorResult(key=_key, code=_code, message=_message))
    return DeleteObjectsResponse(deleted=deleted_list, error=error_list)


def parseListMultipartUploads(xml):
    root = ET.fromstring(xml)

    Bucket = root.find('./Bucket')
    Bucket = common_util.toString(Bucket.text) if Bucket is not None else None
    KeyMarker = root.find('./KeyMarker')
    KeyMarker = common_util.toString(KeyMarker.text) if KeyMarker is not None else None

    UploadIdMarker = root.find('./UploadIdMarker')
    UploadIdMarker = common_util.toString(UploadIdMarker.text) if UploadIdMarker is not None else None
    NextKeyMarker = root.find('./NextKeyMarker')
    NextKeyMarker = common_util.toString(NextKeyMarker.text) if NextKeyMarker is not None else None
    NextUploadIdMarker = root.find('./NextUploadIdMarker')
    NextUploadIdMarker = common_util.toString(NextUploadIdMarker.text) if NextUploadIdMarker is not None else None

    MaxUploads = root.find('./MaxUploads')
    MaxUploads = common_util.toInt(MaxUploads.text) if MaxUploads is not None else None

    IsTruncated = root.find('./IsTruncated')
    IsTruncated = common_util.toBool(IsTruncated.text) if IsTruncated is not None else None

    Prefix = root.find('./Prefix')
    prefix = common_util.toString(Prefix.text) if Prefix is not None else None
    delimiter = root.find('./Delimiter')
    delimiter = common_util.toString(delimiter.text) if delimiter is not None else None

    rules = root.findall('./Upload')
    uploadlist = []
    if rules:
        for rule in rules:
            Key = rule.find('./Key')
            Key = common_util.toString(Key.text) if Key is not None else None
            UploadId = rule.find('./UploadId')
            UploadId = common_util.toString(UploadId.text) if UploadId is not None else None

            ID = rule.find('./Initiator/ID')
            ID = common_util.toString(ID.text) if ID is not None else None

            DisplayName = rule.find('./Initiator/DisplayName')
            DisplayName = common_util.toString(DisplayName.text) if DisplayName is not None else None
            initiator = Initiator(id=ID, name=DisplayName)

            owner_id = rule.find('./Owner/ID')
            owner_id = common_util.toString(owner_id.text) if owner_id is not None else None
            owner_name = rule.find('./Owner/DisplayName')
            owner_name = common_util.toString(owner_name.text) if owner_name is not None else None
            ower = Owner(owner_id=owner_id, owner_name=owner_name)

            StorageClass = rule.find('./StorageClass')
            StorageClass = common_util.toString(StorageClass.text) if StorageClass is not None else None

            Initiated = rule.find('./Initiated')
            Initiated = UTCToLocal(Initiated.text) if Initiated is not None else None
            upload = Upload(key=Key, uploadID=UploadId, initiator=initiator, owner=ower, storageClass=StorageClass, initiated=Initiated)
            uploadlist.append(upload)
    common = root.findall('./CommonPrefixes')
    commonlist = []
    if common:
        for comm in common:
            comm_prefix = comm.find('./Prefix')
            comm_prefix = common_util.toString(comm_prefix.text) if comm_prefix is not None else None
            Comm_Prefix = CommonPrefix(prefix=comm_prefix)
            commonlist.append(Comm_Prefix)
    return ListMultipartUploadsResponse(bucket=Bucket, keyMarker=KeyMarker, uploadIdMarker=UploadIdMarker,
                                        nextKeyMarker=NextKeyMarker, nextUploadIdMarker=NextUploadIdMarker, maxUploads=MaxUploads,
                                        isTruncated=IsTruncated, prefix=prefix, delimiter=delimiter, upload=uploadlist, commonPrefixs=commonlist)

def parseInitiateMultipartUpload(xml):
    root = ET.fromstring(xml)
    bucketName = root.find('.//Bucket')
    bucketName = common_util.toString(bucketName.text) if bucketName is not None else None
    objectKey = root.find('.//Key')
    objectKey = common_util.toString(objectKey.text) if objectKey is not None else None
    uploadId = root.find('.//UploadId')
    uploadId = common_util.toString(uploadId.text) if uploadId is not None else None
    return InitiateMultipartUploadResponse(bucketName=bucketName, objectKey=objectKey, uploadId=uploadId)  # 返回InitiateMultipartUploadResponse对象

def parseCompleteMultipartUpload(xml):
    root = ET.fromstring(xml)
    location = root.find('.//Location')
    location = common_util.toString(location.text) if location is not None else None
    bucket = root.find('.//Bucket')
    bucket = common_util.toString(bucket.text) if bucket is not None else None
    key = root.find('.//Key')
    key = common_util.toString(key.text) if key is not None else None
    eTag = root.find('.//ETag')
    eTag = common_util.toString(eTag.text) if eTag is not None else None
    return CompleteMultipartUploadResponse(location=location, bucket=bucket, key=key, eTag=eTag)  # 返回CompleteMultipartUploadResponse的对象


def parseCopyPart(xml):
    root = ET.fromstring(xml)
    lastModified = root.find('.//LastModified')
    lastModified = UTCToLocal(lastModified.text) if lastModified is not None else None
    eTag = root.find('.//ETag')
    eTag = common_util.toString(eTag.text) if eTag is not None else None
    return CopyPartResponse(modifiedDate=lastModified, etagValue=eTag)  # 返回CopyPartResponse的对象


def parseListParts(xml):
    root = ET.fromstring(xml)

    bucketName = root.find('.//Bucket')
    bucketName = common_util.toString(bucketName.text) if bucketName is not None else None
    objectKey = root.find('.//Key')
    objectKey = common_util.toString(objectKey.text) if objectKey is not None else None
    uploadId = root.find('.//UploadId')
    uploadId = common_util.toString(uploadId.text) if uploadId is not None else None

    storageClass = root.find('.//StorageClass')
    storageClass = common_util.toString(storageClass.text) if storageClass is not None else None
    partNumbermarker = root.find('.//PartNumberMarker')
    partNumbermarker = common_util.toInt(partNumbermarker.text) if partNumbermarker is not None else None
    nextPartNumberMarker = root.find('.//NextPartNumberMarker')
    nextPartNumberMarker = common_util.toInt(nextPartNumberMarker.text) if nextPartNumberMarker is not None else None
    maxParts = root.find('.//MaxParts')
    maxParts = common_util.toInt(maxParts) if maxParts is not None else None
    isTruncated = root.find('.//IsTruncated')
    isTruncated = common_util.toBool(isTruncated.text) if isTruncated is not None else None

    initiatorid = root.find('.//Initiator/ID')
    initiatorid = common_util.toString(initiatorid.text) if initiatorid is not None else None
    displayname = root.find('.//Initiator/DisplayName')
    displayname = common_util.toString(displayname.text) if displayname is not None else None

    initiator = Initiator(id=initiatorid, name=displayname)

    ownerid = root.find('.//Owner/ID')
    ownerid = common_util.toString(ownerid.text) if ownerid is not None else None
    ownername = root.find('.//Owner/DisplayName')
    ownername = common_util.toString(ownername.text) if ownername is not None else None

    owner = Owner(owner_id=ownerid, owner_name=ownername)

    part_list = root.findall('./Part')
    parts = []
    if part_list:
        for part in part_list:
            partnumber = part.find('./PartNumber')
            partnumber = common_util.toInt(partnumber.text) if partnumber is not None else None
            modifieddate = part.find('./LastModified')
            modifieddate = UTCToLocal(modifieddate.text) if modifieddate is not None else None
            etag = part.find('./ETag')
            etag = common_util.toString(etag.text) if etag is not None else None
            size = part.find('./Size')
            size = common_util.toLong(size.text) if size is not None else None
            __part = Part(partNumber=partnumber, lastModified=modifieddate, etag=etag, size=size)
            parts.append(__part)

    return ListPartsResponse(bucketName=bucketName, objectKey=objectKey, uploadId=uploadId, initiator=initiator, owner=owner, storageClass=storageClass,
                             partNumberMarker=partNumbermarker, nextPartNumberMarker=nextPartNumberMarker, maxParts=maxParts, isTruncated=isTruncated, parts=parts)  # 返回ListPartsResponse的对象


def parseCopyObject(xml):
    root = ET.fromstring(xml)
    lastModified = root.find('.//LastModified')
    lastModified = UTCToLocal(lastModified.text) if lastModified is not None else None
    eTag = root.find('.//ETag')
    eTag = common_util.toString(eTag.text) if eTag is not None else None
    return CopyObjectResponse(lastModified=lastModified, eTag=eTag)  # 返回CopyObjectResponse的对象