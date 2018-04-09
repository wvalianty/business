#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"客户管理模块"
import math
from core.coreweb import get, post
from lib.models import Client

@get('/apis/client/index')
async def index(*, page=1, pageSize=1):
    page = int(page)
    pageSize = int(pageSize)

    total = await Client.findNumber('count(id)')
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(page = p, list = ())
    clients = await Client.findAll(orderBy='id desc', limit=limit)
    
    for item in clients:
        item.indate = item.indate.strftime('%Y-%m-%d')
        item.add_date = item.add_date.strftime('%Y-%m-%d %H:%M:%S')

    return {
        'total': total,
        'p': p,
        'list': clients
    }


@post('/apis/client/add')
async def add(*, name, indate, invoice):

    clientInfo = dict(
        name = name.strip(),
        indate = indate.strip(),
        invoice = invoice.strip()
    )

    client = Client(**clientInfo)
    rows = await client.save()

    if rows == 1:
        return {
            'status': 1,
            'msg': '添加成功'
        }
    else:
        return {
            'status': 0,
            'msg': '添加失败'
        }


   