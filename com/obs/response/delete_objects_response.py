#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

class DeleteObjectsResponse(BaseModel):
    #===========================================================================
    # 获取桶的复制策略返回信息
    #===========================================================================
    allowedAttr = {'deleted': list, 'error': list}


class ErrorResult(BaseModel):
    '''
    #批量删除对象返回的错误信息
    '''
    allowedAttr = {'key': BASESTRING, 'code': BASESTRING, 'message': BASESTRING}
        
class DeleteObjectResult(BaseModel):
    '''
    #批量删除对象返回的成功信息
    '''
    allowedAttr = {'key': BASESTRING, 'deleteMarker': bool, 'deleteMarkerVersionId': BASESTRING}
