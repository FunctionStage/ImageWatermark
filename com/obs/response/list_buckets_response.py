#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel
from com.obs.models.owner import Owner


#罗列存储空间方法返回对象，可解析返回的XML为S3存储空间
class ListBucketsResponse(BaseModel):

    allowedAttr = {'buckets': list, 'owner': Owner}
            

 
    
    