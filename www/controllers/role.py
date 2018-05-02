#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"角色管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Role, Users, Rule
from lib.common import obj2str, totalLimitP, returnData, ruleTree


@get('/apis/role/index')
async def index(*, page=1, pageSize=10):

    page = int(page)
    pageSize = int(pageSize)
   
    lists = await Role.findAll(orderBy="id asc")

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)
    
    return {
        'total': 0,
        'page': [1,10],
        'list': lists
    }

@get('/apis/role/info')
async def info(*,id):

    action = '查询'
    id = int(id)

    if not id:
        return returnData(0, action, 'ID不存在')

    info = await Role.find(id)
    if not info:
        return returnData(0, action)

    res = returnData(1, action)
    res['info'] = obj2str([info])[0]

    return res

@get('/apis/role/formInit')
async def formInit(*, id):
    """form表单初始化数据加载
    """

    # 获得所有规则列表
    lists = await Role.findAll(field="id, pid, title",orderBy='sort desc')
    lists = ruleTree(lists)

    res = {
        'ruleList': lists
    }

    return res

@get('/apis/role/rule')
async def rule(*, id=None): 
    """配置权限
    """
    if not id:
        return returnData(0, '配置权限', '缺少请求参数')

    lists = await Rule.findAll(field="id, pid, title", orderBy="sort desc, id asc")

    # 获得当前用户组的权限
    info = await Role.find(id)
    checkedList = info['rules'].rstrip(',').split(',')
    
    for item in lists:
        item['open'] = True
        if str(item['id']) in checkedList:
            item['checked'] = True
    
    lists.append({
        'id': 0,
        'pid': 0,
        'title': '全部',
        'open': True
    })
    return {
        'status': 1,
        'list': lists
    }

@post('/apis/role/setrule')
async def setrule(*, id=None, rules=None):
    
    action = '配置权限'
    if not id or not rules:
        return returnData(0, action, '缺少参数')

    oldInfo = await Role.find(id)
    oldInfo['rules'] = rules

    rows = await Role(**oldInfo).save()

    return returnData(rows, action)
    

@post('/apis/role/form')
async def form(**kw):

    action = '添加'
    info = dict(
        title = kw.get('title', ''),
    )

    if info['title'] == '':
        return returnData(0, action, '角色名称不能为空')

    id = kw.get('id', 0)
    if id.isdigit() and int(id) > 0:
        action = '编辑'
        oldInfo = await Role.find(id)
        info = dict(oldInfo, **info)

    rows = await Role(**info).save()

    return returnData(rows, action)

@get('/apis/role/del')
async def delete(*, id):

    action = '删除'
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, action, '缺少请求参数')

    count = await Users.findNumber('count(*)', where="role = %s" % id)
    if count > 0:
        return returnData(0, action, '请先删除属于该角色的用户')
    
    rows = await Role.delete(id)
    return returnData(rows, action)
