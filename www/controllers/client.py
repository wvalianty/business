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
    for item in clients:
        # 投放数
        where = 'client_id=%s' % item.id
        item['tfCount'] = await Income.findNumber('count(id)', where)

        # 投放金额
        tfMoney = await Income.findNumber('sum(money)', where)
        item['tfMoney'] = round(tfMoney, 2) if tfMoney else 0  

        # 回款金额
        incomeIds = await Income.findCols(selectField='income_id', where="client_id=%s" % item.id)
        
        if not incomeIds and len(incomeIds) > 0:
            where = "income_id in (%s)" % (','.join(incomeIds))
            hkMoney = await Settlement.findNumber('sum(balance)', where)
            item['hkMoney'] = round(hkMoney, 2) if hkMoney else 0
        else:
            item['hkMoney'] = 0

        # 回款数
        where = '%s and status = 2' % where
        item['hkCount'] = await Income.findNumber('count(id)', where)
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
    
    try:
        rows = await Client.delete(id)
        msg = None
    except Exception as e:
        rows = 0
        msg = "请先删除收入报表中有关该客户的记录"

    return returnData(rows, '删除', msg)