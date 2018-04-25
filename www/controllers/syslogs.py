#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"系统操作日志"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Syslogs
from lib.common import obj2str, returnData, totalLimitP

operateMaps = {
    'INSERT': '新增',
    'UPDATE': '编辑',
    'DELETE': '删除'
}

moduleMaps = {
    'CLIENT': '客户管理',
    'BUSINESS_TYPE': '业务管理',
    'INVOICE': '发票管理',
    'INCOME': '收入报表',
    'SETTLEMENT': '结算单',
    'USERS': '用户管理'
}

# sql模板
sqlTpl = "SELECT {} FROM syslog \
       WHERE module != 'INCOME_NO' and {}"

# 搜索字段
selectField = 'id, username, `operate`, `module`, `sql`, `add_date`'

@get('/apis/syslogs/index')
async def index(*, keyword=None, operate=None, module=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    # 当前日期
    # currDate = time.strftime('%Y-%m-%d')

    where = 'is_delete=0'
    if keyword:
        where = "username like '%%{}%%'".format(keyword)
    if operate and operate in operateMaps.keys():
        where = "%s and operate = '%s'" % (where, operate)
    if module and module in moduleMaps.keys():
        where = "%s and module = '%s'" % (where, module)
    
    sql = sqlTpl.format('count(*) c', where)
    rs = await Syslogs.query(sql)
    total, limit, p = totalLimitP(rs, page, pageSize)
    
    if total == 0:
        return dict(total = total, page = p, list = (), other={
            'operateMaps': operateMaps,
            'moduleMaps': moduleMaps
        })
    
    where = "%s order by %s limit %s" % (where, 'id desc', limit)
    sql = sqlTpl.format(selectField, where)
    lists = await Syslogs.query(sql)

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



@get('/apis/syslogs/del')
async def delete(*, id):
    
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, '删除', '缺少请求参数')
    
    try:
        rows = await Syslogs.delete(id)
        msg = None
    except Exception as e:
        rows = 0
        msg = "请先删除收入报表中有关该客户的记录"

    return returnData(rows, '删除', msg)
