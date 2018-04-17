#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"客户管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Client, Income, Settlement
from lib.common import obj2str

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
        op = '>='
        if int(status) == 0:
            op = '<'

        where = "%s and indate %s '%s'" % (where, op, currDate)

    total = await Client.findNumber('count(id)', where)
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
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
        hkMoney = await Settlement.findNumber('sum(balance)', where)
        item['hkMoney'] = round(hkMoney, 2) if hkMoney else 0

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

    res = {
        'status': 1,
        'msg': '查询成功',
        'info': []
    }

    if not id:
        res['status'] = 0
        res['msg'] = 'id不存在'
        return res
    
    info = await Client.find(id)

    if not info:
        res['status'] = 0
        res['msg'] = '查询失败'
        return res

    info = obj2str([info])[0]
    info['indate'] = "%s - %s" % (info['indate_start'], info['indate_end'])
    del info['indate_start']
    del info['indate_end']

    res['info'] = info

    return res
    


@post('/apis/client/form')
async def form(*, id, name, indate, invoice):

    action = '添加'

    indates = indate.split(' - ')
    if not indates or len(indates) != 2:
        print(indates)
        return {
            'status': 0,
            'msg': '编辑失败，日期格式错误'
        }
    clientInfo = dict(
        name = name.strip(),
        indate_start = indates[0].strip(),
        indate_end = indates[1].strip(),
        invoice = invoice.strip()
    )

    if id.isdigit() and int(id) > 0:
        action = '编辑'
        clientInfo['id'] = id
        rows = await Client(**clientInfo).update()
    else:
        rows = await Client(**clientInfo).save()

    if rows == 1:
        return {
            'status': 1,
            'msg': '%s成功' % action
        }
    else:
        return {
            'status': 0,
            'msg': '%s失败' % action
        }


@get('/apis/client/del')
async def delete(*, id):
    
    if not id.isdigit() or int(id) <= 0:
        return {
            'status': 0,
            'msg': '删除失败,缺少请求参数'
        }
    
    rows = await Client.delete(id)

    if rows == 1:
        return {
            'status': 1,
            'msg': '删除成功'
        }
    else:
        return {
            'status': 0,
            'msg': '删除失败'
        }