#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"后台管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Role, Rule, Users
from lib.common import obj2str, returnData, ruleTree
from config import configs

@get('/apis/admin/leftmenu')
async def leftmenu(request):
    
    # 获得当前用户名
    username = configs.user.name
    # 获得当前用户信息
    userInfo = await Users.findOne(where="email='%s'" % username)
    if not userInfo:
        return {
            'status': 0,
            'msg': '请登录',
        }
    
    # 获得当前用户角色信息
    roleInfo = await Role.find(userInfo['role'])

    if not roleInfo:
        return {
            'status': 0,
            'msg': '用户所属用户组不存在，请联系管理员重新授权'
        }
    
    if not roleInfo['rules']:
        return {
            'status': 1,
            'msg': '查询成功',
            'leftmenu': [],
            'username': username
        }
    
    # 获得角色菜单列表
    selectField = "id, pid, route, title, icon"
    where = "menustatus=1 and id in (%s)" % roleInfo.rules.rstrip(',')
    order = "sort desc, id asc"
    ruleList = await Rule.findAll(field=selectField, where=where, orderBy=order)
    menuTree = ruleTree(ruleList).values()
    
    return {
        'status': 1,
        'msg': '查询成功',
        'leftmenu': list(menuTree),
        'username': username
    }

