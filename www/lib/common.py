#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'公共函数库'

import time, re, logging, hashlib, sys, os, datetime, xlwt, math
from lib.apis import APIValueError, APIError, APIPermissionError
from io import BytesIO
from aiohttp import web
from lib.models import Income,Users

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
            if isinstance(item[field], datetime.datetime):
                item[field] = item[field].strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(item[field], datetime.date):
                item[field] = item[field].strftime("%Y-%m-%d")

    return arr

def exportExcel(name, fields, lists):
    """导出excle报表

    Arguments:
        name {[type]} -- [文件名]
        fields {[type]} -- [导出字段名]
        lists {[type]} -- [数据列表]
    """

    boldStyle = xlwt.easyxf('font: name Times New Roman, color-index black, bold on', num_format_str='#,##0.00')

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet(name, cell_overwrite_ok=True)

    colIndex = 0
    for field in fields:
        sheet.write(0, colIndex, fields[field], boldStyle)
        colIndex += 1

    rowIndex = 1
    colIndex = 0

    for item in lists:
        for field in fields:
            sheet.write(rowIndex, colIndex, item[field])
            colIndex += 1
        rowIndex += 1
        colIndex = 0
    sio = BytesIO()
    workbook.save(sio)
    sio.seek(0)

    resp = web.Response(body=sio.getvalue())
    resp.content_type = 'applicattion/vnd.ms-excel'
    resp.headers['Content-Disposition'] = 'attachment;filename=%s.xls' % name
    return resp

def returnData(rows, action, other=None):
    """格式化返回数据
    """
    status = 0
    msg = "%s失败" % action

    if rows == 1:
        status = 1
        msg = "%s成功" % action

    if other:
        msg = "%s,%s" % (msg, other)

    return {
        'status': status,
        'msg': msg
    }

def totalLimitP(rs, page, pageSize, limitFlag = False):
    """返回数据总条数，limit，页数

    Arguments:
        rs {[type]} -- [description]
        page {[type]} -- [description]
        pageSize {[type]} -- [description]
    """

    if isinstance(rs, int):
        total = rs
    else:
        total = rs[0]['c']
    limit = "%s,%s" % ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)

    if limitFlag:
        limit = tuple([int(x) for x in limit.split(',')])

    return total, limit, p

async def addAffDateWhere1(where, month, isSearch=None, year=None):
    """where 条件添加归属日期参数
    """
    if not year:
        year = time.strftime('%Y')
    if month and month.isdigit():
        month = month.zfill(2)
    elif not month and not isSearch:
        lastDate = await Income.findNumber('aff_date', orderBy='aff_date desc')
        if lastDate:
            dates = lastDate.split('-')
            year, month = (dates[0], dates[1])
        else:
            month = time.strftime('%m')

    if month:
        where = "{} and aff_date = '{}-{}'".format(where, year, month)
    elif year:
        where = "{} and aff_date like '{}-{}'".format(where, year, '%%')

    return where

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [str(user.id), expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await Users.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

def ruleTree(lists, isList=False):
    """
    获得权限规则菜单
    """
    if not lists:
        return []

    maps = {}

    for item in lists:
        maps[item['id']] = item

    for id in list(maps.keys()):
        if id not in maps:
            continue
        item = maps[id]

        if item['pid'] == 0:
            continue

        if item['pid'] in maps:

            if 'child' not in maps[item['pid']]:
                maps[item['pid']]['child'] = []

            maps[item['pid']]['child'].append(item)
            del maps[id]
        else:
            for id2 in list(maps.keys()):
                if id2 not in maps:
                    continue

                tmp = maps[id2]
                if 'child' in tmp:
                    for i, child in enumerate(tmp['child']):
                        if child['id'] == item['pid']:
                            if 'child' not in maps[id2]['child'][i]:
                                maps[id2]['child'][i]['child'] = []

                            maps[id2]['child'][i]['child'].append(item)
                            del maps[id]
                            break
                        elif 'child' in child:
                            for j, twochild in enumerate(child['child']):
                                if twochild['id'] == item['pid']:
                                    if 'child' not in maps[id2]['child'][i]['child'][j]:
                                        maps[id2]['child'][i]['child'][j]['child'] = []
                                    
                                    maps[id2]['child'][i]['child'][j]['child'].append(
                                        item)
                                    del maps[id]
                                    break
    
    if isList:
        lists = []
        for id in list(maps.keys()):
            item = maps[id]
            item['level'] = 0
            lists.append(item)
            if 'child' in item:
                for onechild in item['child']:
                    onechild['level'] = 1
                    lists.append(onechild)
                    if 'child' in onechild:
                        for twochild in onechild['child']:
                            twochild['level'] = 2
                            lists.append(twochild)
                            if 'child' in twochild:
                                for threechild in twochild['child']:
                                    threechild['level'] = 3
                                    lists.append(threechild)
        
        return lists
 
    return maps


async def addAffDateWhere(rangeDate=None, isSearch=None, delField="is_delete", affField="aff_date", lastDate=None):
    """获得起止日期
    """
    
    localtimes = time.localtime()
    currYear = localtimes[0]
    currMonth = localtimes[1]

    if not lastDate:
        lastDate = await Income.findNumber('aff_date', orderBy='aff_date desc')
    if (not isSearch and lastDate) or (isSearch and not rangeDate):
        dates = lastDate.split('-')
        currYear, currMonth = (int(dates[0]), int(dates[1]))

    if not rangeDate or rangeDate.find(' - ') != 7:
        endYear = currYear
        endMonth = currMonth + 1
        if currMonth == 13:
            endMonth = 1
            endYear += 1

        startDate = "%s-%s" % (currYear, str(currMonth).zfill(2))
        endDate = "%s-%s" % (endYear, str(endMonth).zfill(2))
    else:
        startDate, endDate = rangeDate.split(' - ')

    baseWhere = "%s = 0" % delField
    dateWhere = "{} >= '{}' and {} < '{}'".format(affField, startDate, affField, endDate)
    
    where = baseWhere
    if not isSearch or (isSearch and rangeDate):
        where = '{} and {}'.format(where, dateWhere)

    return where

def replBatch(text, old, new):
    """文本批量替换
    
    Arguments:
        text {[type]} -- [要处理的文本]
        old {[type]} -- [要替换的文本， 可以是字符串或list]
        new {[type]} -- [要替换成的文本, 可以是字符串或list]
    """

    if not text:
        return text

    if not isinstance(old, list):
        old = [old]

    for val in old:
        if isinstance(new, list):
            text = text.replace(val, new[old.index(val)])
        else:
            text = text.replace(val, new)
    
    return text


def replLineBreak(text, symbol='<br/>'):
    """替换换行符
    
    Arguments:
        text {[type]} -- [文本]
        symbol {[type]} -- [替换成的符号]
    """

    return replBatch(text, ['\r\n', '\r', '\n'], symbol)
