#!/usr/bin/python  
# -*- coding:utf-8 -*- 

import sys

IS_PYTHON2 = sys.version_info.major == 2 or not sys.version > '3'
BASESTRING = basestring if IS_PYTHON2 else str

UNICODE = unicode if IS_PYTHON2 else str

LONG = long if IS_PYTHON2 else int

if IS_PYTHON2:
    from com.obs.models.model_python2 import _BaseModel
else:
    from com.obs.models.model_python3 import _BaseModel

BaseModel = _BaseModel






