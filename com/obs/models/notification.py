#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel,BASESTRING

#===============================================================================
# 桶通知配置
#===============================================================================
class Notification(BaseModel):
    allowedAttr = {'id': BASESTRING, 'topic': BASESTRING, 'events': list, 'filterRules': list}

#===============================================================================
# 桶通知配置过滤规则
#===============================================================================
class FilterRule(BaseModel):
    allowedAttr = {'name': BASESTRING, 'value': BASESTRING}




