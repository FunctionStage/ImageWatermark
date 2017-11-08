#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import BaseModel
import time

class DateTime(BaseModel):
    '''
    UTC标准时间的年、月、日、时、分、秒。
    '''

    allowedAttr = {'year': int, 'month': int, 'day': int, 'hour': int, 'min':int, 'sec':int}

    def __init__(self, year, month, day, hour=0, min=0, sec=0):
        '''
        Constructor
        '''
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.min = min
        self.sec = sec

    def ToUTTime(self):
        strTime = '%04d-%02d-%02dT%02d:%02d:%02d.000Z' % (
        self.year, self.month, self.day, self.hour, self.min, self.sec)
        return strTime

    def ToGMTTime(self):
        strTime = (self.year, self.month, self.day, self.hour, self.min, self.sec, 0, 0, 0)
        gmt_time = time.gmtime(time.mktime(strTime) - time.timezone)
        return time.strftime('%a, %d %b %Y %H:%M:%S GMT', gmt_time)

    def ToUTMidTime(self):
        strTime = '%04d-%02d-%02dT00:00:00.000Z' % (
            self.year, self.month, self.day)
        return strTime

    @staticmethod
    def UTCToLocal(strUTC):
        if strUTC is None:
            return None

        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        CST_FORMAT = '%Y/%m/%d %H:%M:%S'

        gmt_time = time.strptime(strUTC, date_format)

        cst_time = time.localtime(time.mktime(gmt_time) - time.timezone)
        dt = time.strftime(CST_FORMAT, cst_time)

        return dt


