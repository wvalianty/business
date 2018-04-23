#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"系统操作日志"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Syslog
from lib.common import obj2str, returnData, totalLimitP

operateMaps = {
    'INSERT': '新增',
    'UPDATE': '编辑',
    'DELETE': '删除'
}

moduleMaps = {
    'CLIENT': '客户管理',
    'BUSINESS_TYPE': '业务管理',
    'INVIOCE': '发票管理',
    'INCOME': '收入报表',
    'SETTLEMENT': '结算单'
}

# sql模板
sqlTpl = "SELECT {} FROM syslog s \
       INNER JOIN users u ON s.uid = u.id \
       WHERE {}"

# 搜索字段
selectField = 's.id, u.name, s.operate, s.module, s.sql, s.add_date'

@get('/apis/syslog/index')
async def index(*, keyword=None, operate=None, module=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    # 当前日期
    # currDate = time.strftime('%Y-%m-%d')

    where = '1 = 1'
    if keyword:
        where = "u.name like '%%{}%%'".format(keyword)
    if operate and operate in operateMaps.keys():
        where = "%s and operate = '%s'" % (where, operate)
    if module and module in moduleMaps.keys():
        where = "%s and module = '%s'" % (where, module)
    
    sql = sqlTpl.format('count(*) c', where)
    rs = await Syslog.query(sql)
    total, limit, p = totalLimitP(rs, page, pageSize)
    
    if total == 0:
        return dict(total = total, page = p, list = (), other={
            'operateMaps': operateMaps,
            'moduleMaps': moduleMaps
        })
    
    where = "%s order by %s limit %s" % (where, 'id desc', limit)
    sql = sqlTpl.format(selectField, where)
    lists = await Syslog.query(sql)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    # 获得每个客户下的投放数和回款数
    for item in lists:
        item['operate_text'] = operateMaps[item['operate']]
        item['module_text'] = moduleMaps[item['module']]
       

    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'operateMaps': operateMaps,
            'moduleMaps': moduleMaps
        }
    }

@get('/apis/syslog/info')
async def info(*,id):
    id = int(id)

    if not id:
        return returnData(0, '查询', 'ID不存在')
    
    info = await Client.find(id)

    if not info:
        return returnData(0, '查询')

    info = obj2str([info])[0]
    info['indate'] = "%s - %s" % (info['indate_start'], info['indate_end'])
    del info['indate_start']
    del info['indate_end']

    res = returnData(1, '查询')

    res['info'] = info

    return res
    


@post('/apis/syslog/form')
async def form(*, id, name, indate, invoice):

    action = '添加'
    indates = indate.split(' - ')

    if not indates or len(indates) != 2:
        return returnData(0, action, '日期格式错误')

    info = dict(
        name = name.strip(),
        indate_start = indates[0].strip(),
        indate_end = indates[1].strip(),
        invoice = invoice.strip()
    )

    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info['id'] = id

    rows = await Client(**info).save()

    return returnData(rows, action)


@get('/apis/syslog/del')
async def delete(*, id):
    
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, '删除', '缺少请求参数')
    
    try:
        rows = await Client.delete(id)
        msg = None
    except Exception as e:
        rows = 0
        msg = "请先删除收入报表中有关该客户的记录"

    return returnData(rows, '删除', msg)
