# encoding:utf-8
import time
import datetime


class GetTime(object):

    @staticmethod
    def getNowTime():
        return time.strftime('%H:%M:%S', time.localtime(time.time()))

    @staticmethod
    def getNowDate():
        return str(datetime.date.today())

    @staticmethod
    def getYesterday():
        today = datetime.date.today()
        return str(today - datetime.timedelta(days=1))

