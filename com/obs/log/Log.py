#!/usr/bin/python  
# -*- coding:utf-8 -*- 


from com.obs.log import log_client

LOGMODE = 'OBS_LOGGER'
DEFAULT_LOGGER = None

CRITICAL = log_client.CRITICAL
ERROR = log_client.ERROR
WARNING = log_client.WARNING
INFO = log_client.INFO
DEBUG = log_client.DEBUG

LogConf = log_client.LogConf

def LogInit(logConfig=log_client.LogConf()):
    global DEFAULT_LOGGER
    DEFAULT_LOGGER = log_client.LogClient(logConfig,LOGMODE)


def LOG(level, msg, *args, **kwargs):
    global DEFAULT_LOGGER
    if DEFAULT_LOGGER is not None:
        DEFAULT_LOGGER.LOG(level, msg, *args, **kwargs)

