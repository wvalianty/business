#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'公共函数库'

import time, re, json, logging, hashlib, base64, asyncio, sys, os, datetime
from lib.models import User
from lib.apis import APIValueError, APIError, APIPermissionError

lib_dir = os.path.dirname(os.path.realpath(__file__))
conf_dir = os.path.join(lib_dir, '..','..', 'conf')
ctr_dir = os.path.join(lib_dir, '..', 'controllers')
sys.path.append(conf_dir)
sys.path.append(ctr_dir)
from config import configs

_RE_EMAIL = re.compile(
    r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'[0-9a-f]{40}$')

COOKIE_NAME = configs.cookie.name
_COOKIE_KEY = configs.session.secret

def user2cookie(user, max_age):
    """根据用户信息，生成用户cookie字符串"""
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = ('%s-%s-%s-%s' % (user['id'], user['passwd'], expires, _COOKIE_KEY)).encode('utf-8')
    L = [user['id'], expires, hashlib.sha1(s).hexdigest()]
    return '-'.join(L)

async def cookie2user(cookie_str):
    """检查用户cookie是否合法,如合法，则返回用户信息"""
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = ('%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)).encode('utf-8')
        if sha1 != hashlib.sha1(s).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

def check_admin(request):
    """检查用户是否是后台管理员
    """
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


def obj2str(arr):
    """对象转字符串"""
    
    for item in arr:
        for field in item:
            if isinstance(field, datetime.datetime):  
                field = field.strftime('%Y-%m-%d %H:%M:%S')  
            elif isinstance(field, datetime.date):  
                field = field.strftime("%Y-%m-%d")  
    
    return arr