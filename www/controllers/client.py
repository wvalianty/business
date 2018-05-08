#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"客户管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Client, Income, Settlement
from lib.common import obj2str, returnData, totalLimitP

@get('/apis/client/index')
async def index(*, keyword=None, status=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    # 当前日期
    currDate = time.strftime('%Y-%m-%d')

    where = '1 = 1'
    if keyword:
        where = "name like '%%{}%%'".format(keyword)
    if status and status.isdigit():
        if int(status) == 0:
            where = "%s and indate_end < '%s'" % (where, currDate)
        else:
            where = "%s and indate_end >= '%s'" % (where, currDate)
    
    total = await Client.findNumber('count(id)', where)
    total, limit, p = totalLimitP(total, page, pageSize, True)
    
    if total == 0:
        return dict(total = total, page = p, list = ())
    clients = await Client.findAll(orderBy='id desc', where=where, limit=limit)

    # 将获得数据中的日期转换为字符串
    clients = obj2str(clients)

    # 获得每个客户下的投放数和回款数
    selectField = "count(*) tfCount, sum(money) tfMoney"
    for item in clients:
        # 投放数
        where = 'is_delete = 0 and client_id=%s' % item.id
        info = await Income.findOne(selectField, where)
        item['tfCount'] = round(info['tfCount'], 2) if info['tfCount'] else 0

        # 投放金额
        item['tfMoney'] = round(info['tfMoney'], 2) if info['tfMoney'] else 0

        # 回款金额
        where = "%s and money_status = 1" % where
        field = "count(*) hkCount, sum(money) hkMoney"
        info = await Income.findOne(field, where)
        item['hkMoney'] = round(info['hkMoney'], 2) if info['hkMoney'] else 0

        # 回款数
        item['hkCount'] = round(info['hkCount'], 2) if info['hkCount'] else 0
        item['invoice'] = item['invoice'].replace('\n', '<br/>')

        # 合同是否有效
        item['indate_status'] = item['indate_end'] >= currDate

    return {
        'total': total,
        'page': p,
        'list': clients
    }

@get('/apis/client/info')
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
    


@post('/apis/client/form')
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


@get('/apis/client/del')
async def delete(*, id):
    
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, '删除', '缺少请求参数')
    
    # 判断是否有收入单关联
    count = await Income.findNumber('count(*)', where="client_id=%s" % id)

    if count > 0:
        rows = 0
        msg = "请先删除收入报表中有关该客户的记录"
    else:
        rows = await Client.delete(id)
        msg = None
   
    return returnData(rows, '删除', msg)
