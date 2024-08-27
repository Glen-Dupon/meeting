# encoding: utf-8
from __future__ import absolute_import, unicode_literals

SECRET_KEY = 'c79dc00106ae3354bc61c7533aceef59'

# REDIS_HOST = '172.24.118.106'
#on realserver pw Redis123Redis

REDIS_HOST = '127.0.0.1'
REDIS_PASSWORD = 'BQJSSZ888'
REDIS_PORT = '6379'
REDIS_CACHE_DB = 5
REDIS_SESSION_DB = 6
REDIS_CELERY_DB = 7
REDIS_CONSTANCE_DB = 8
REDIS_CHANNEL_DB = 9

# CREATE SCHEMA `meeting` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci ;

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = '3306'
MYSQL_DBNAME = 'meeting'
MYSQL_USERNAME = 'meetingdbuser'
MYSQL_PASSWORD = 'meetingdbuser_555'

WECHAT_APPID = 'wx696535edefb304bd'
#'小程序appid'
WECHAT_APPSECRET = 'c79dc00106ae3354bc61c7533aceef59'
#'小程序appsecret'

# 配置以下信息管理员会收到异常邮件，不需要可直接删除
# EMAIL_HOST = ''
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# SERVER_EMAIL = ''
# DEFAULT_FROM_EMAIL = ''

# ADMINS = (('管理员姓名', '管理员邮箱'),)