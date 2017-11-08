#!/usr/bin/python
# -*- coding:utf-8 -*-

class HeadPermission(object):
    '''
    classdocs
    '''
    PRIVATE = 'private'
    PUBLIC_READ = 'public-read'
    PUBLIC_READ_WRITE = 'public-read-write'
    AUTHENTICATED_READ = 'authenticated-read'
    BUCKET_OWNER_READ = 'bucket-owner-read'
    BUCKET_OWNER_FULL_CONTROL = 'bucket-owner-full-control'
    LOG_DELIVERY_WRITE = 'log-delivery-write'
