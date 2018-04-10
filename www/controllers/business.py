#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"业务管理模块"
import math, datetime
from core.coreweb import get, post
from lib.models import Business
from lib.common import obj2str

@get('/apis/business/index')
async def index(*, keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    where = '1 = 1'
    if keyword:
        where = "`type` like '%%{}%%'".format(keyword)

    total = await Business.findNumber('count(id)', where)
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total = total, page = p, list = ())
    lists = await Business.findAll(orderBy='id desc', where=where, limit=limit)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    return {
        'total': total,
        'page': p,
        'list': lists
    }


@post('/apis/business/form')
async def form(*,id, btype):

    action = '添加'
    info = dict(
        type = btype.strip(),
    )

    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info['id'] = id
        rows = await Business(**info).update()
    else:
        rows = await Business(**info).save()

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
