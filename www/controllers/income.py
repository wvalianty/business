#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"收入管理模块"
import math, datetime
from core.coreweb import get, post
from lib.models import Income, Client, Business
from lib.common import obj2str

@get('/apis/income/index')
async def index(*, keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    where = '1 = 1'
    if keyword:
        where = "name like '%%{}%%'".format(keyword)

    total = await Income.findNumber('count(id)', where)
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total = total, page = p, list = ())
    lists = await Income.findAll(orderBy='id desc', where=where, limit=limit)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    return {
        'total': total,
        'page': p,
        'list': lists
    }

@get('/apis/income/info')
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

    res['info'] = obj2str([info])[0]

    return res

@get('/apis/income/formInit')
async def formInit(request):
    """form表单初始化数据加载
    """
    
    # 获得所有公司列表， id,name
    clientList = await Client.findAll(field='id,name')
 

    # 获得所有业务类型，id,type
    typeList = await Business.findAll(field='id,type')

    return {
        'clientList': clientList,
        'typeList': typeList
    }

@post('/apis/income/form')
async def form(*, id, name, indate, invoice):

    action = '添加'
    clientInfo = dict(
        name = name.strip(),
        indate = indate.strip(),
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


@get('/apis/income/del')
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