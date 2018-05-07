#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"系统操作日志"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Syslogs
from lib.common import obj2str, returnData, totalLimitP
from income import statusMap as incomeStatusMap

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
    'USERS': '用户管理',
    'ROLE': '用户组管理',
    'RULE': '规则管理'
}

# sql模板
sqlTpl = "SELECT {} FROM syslog s \
        INNER JOIN income i ON s.affetced_id = i.id \
        INNER JOIN client c ON i.client_id = c.id \
        WHERE module = 'INCOME' and s.is_delete =0 and {}"

# 搜索字段
selectField = 's.id, s.username, s.`operate`, s.`module`, s.`add_date`, s.is_read, i.income_id, c.name company_name, i.name, i.money, i.status'

@get('/apis/syslogs/index')
async def index(*, keyword=None, operate=None, module=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    # 当前日期
    # currDate = time.strftime('%Y-%m-%d')

    where = "s.is_delete =0"
    if keyword:
        where = "%s and username like '%%{}%%'".format(where, keyword)
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
    
    where = "%s order by %s limit %s" % (where, 's.id desc', limit)
    sql = sqlTpl.format(selectField, where)
   
    lists = await Syslogs.query(sql)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    # 获得每个客户下的投放数和回款数
    for item in lists:
        item['operate_text'] = operateMaps[item['operate']]
        item['module_text'] = moduleMaps[item['module']]
        item['status_text'] = incomeStatusMap[item['status']]
       

    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'operateMaps': operateMaps,
            'moduleMaps': moduleMaps
        }
    }


@get('/apis/syslogs/read')
async def read(*, id):
    
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, '标记已读', '缺少请求参数')
    
    info = await Syslogs.find(id)
    info['is_read'] = 1
    rows = await Syslogs(**info).update()

    return returnData(rows, '标记已读')

@get('/apis/syslogs/readall')
async def read_all(request):
    
    sql = "UPDATE syslog SET is_read = 1"
    rows = await Syslogs.execute(sql)

    return returnData(1, '全部标记已读')


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
