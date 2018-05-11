#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"权限管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Rule
from lib.common import obj2str, totalLimitP, returnData, ruleTree

# 菜单状态
menuStatusMap = (
    '隐藏',
    '显示'
)

# 权限状态
authopenMap = (
    '无需验证',
    '需要验证'
)

@get('/apis/rule/index')
async def index(*, keyword=None, page=1, pageSize=10):

    page = int(page)
    pageSize = int(pageSize)

    where = "1=1"
    if keyword:
        where = "{} and title like '%%{}%%'".format(where, keyword)

    lists = await Rule.findAll(where=where, orderBy="sort desc, id asc")

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    for item in lists:
        item['menustatus_text'] = menuStatusMap[item['menustatus']]
        item['authopen_text'] = authopenMap[item['authopen']]
    
    lists = ruleTree(lists, True)
    return {
        'total': 0,
        'page': [1,10],
        'list': lists
    }

@get('/apis/rule/info')
async def info(*,id):

    action = '查询'
    id = int(id)

    if not id:
        return returnData(0, action, 'ID不存在')

    info = await Rule.find(id)
    if not info:
        return returnData(0, action)

    res = returnData(1, action)
    res['info'] = obj2str([info])[0]

    return res

@get('/apis/rule/formInit')
async def formInit(*, id):
    """form表单初始化数据加载
    """

    # 获得所有规则列表
    lists = await Rule.findAll(field="id, pid, title",orderBy='sort desc, id asc')
    lists = ruleTree(lists)

    res = {
        'ruleList': lists
    }

    return res

@post('/apis/rule/form')
async def form(**kw):

    action = '添加'
    info = dict(
        pid = kw.get('pid', 0),
        title = kw.get('title', ''),
        route = kw.get('route', ''),
        icon = kw.get('icon', 0),
        menustatus = kw.get('menustatus', 0),
        authopen = kw.get('authopen', 1),
        sort = kw.get('sort', 50)
    )

    if info['title'] == '':
        return returnData(0, action, '权限名称或路由不能为空')

    id = kw.get('id', 0)
    if id.isdigit() and int(id) > 0:
        action = '编辑'
        oldInfo = await Rule.find(id)
        info = dict(oldInfo, **info)
    
    rows = await Rule(**info).save()

    return returnData(rows, action)

@get('/apis/rule/del')
async def delete(*, id):

    action = '删除'
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, action, '缺少请求参数')

    count = await Rule.findNumber('count(*)', where="pid = %s" % id)
    if count > 0:
        return returnData(0, action, '请先删除子菜单')
    
    rows = await Rule.delete(id)
    return returnData(rows, action)