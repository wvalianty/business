#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'url handlers'

from lib.common import *
from core.coreweb import get, post
from lib.apis import APIValueError, APIError, APIPermissionError
from aiohttp import web
import time, re, json, logging, hashlib, base64, asyncio, sys, os
from config import configs

@get('/')
async def index(request):
    return {
        '__template__': 'index.html'
    }

@get('/main')
async def main(request):
    return {
        '__template__': 'main.html'
    }

# 客户管理模块 ----- start
@get('/client')
async def client(request):
    return {
        '__template__': 'client_index.html'
    }

@get('/client/form')
async def client_form(**kw):
    return {
        '__template__': 'client_form.html'
    }

# 客户管理模块 ----- end


# 业务管理模块 ----- start
@get('/business')
async def business(request):
    return {
        '__template__': 'business_index.html'
    }

@get('/business/form')
async def business_form(**kw):
    return {
        '__template__': 'business_form.html'
    }
# 业务管理模块 ------ end

# 发票管理模块 ------ start
@get('/invoice')
async def invoice(request):
    return {
        '__template__': 'invoice_index.html'
    }

@get('/invoice/form')
async def invoice_form(**kw):
    return {
        '__template__': 'invoice_form.html'
    }
# 发票管理模块------- end

# 收入管理模块 ----- start
@get('/income')
async def income(request):
    return {
        '__template__': 'income_index.html'
    }

@get('/income/form')
async def income_form(**kw):
    return {
        '__template__': 'income_form.html'
    }
# 收入管理模块 ------ end


# 结算单管理模块 ----- start
@get('/settlement')
async def settlement(request):
    return {
        '__template__': 'settlement_index.html'
    }

@get('/settlement/form')
async def settlement_form(**kw):
    return {
        '__template__': 'settlement_form.html'
    }
# 结算单管理模块 ------ end


# 系统日志管理模块 ----- start
@get('/syslogs')
async def syslogs(request):
    return {
        '__template__': 'syslogs_index.html'
    }
# 系统日志管理模块 ------ end


# 发票申请模块  --start
@get("/invoiceApply_index")
def invoiceApply_index(request):
    return {
        '__template__': 'invoiceApply_index.html'
    }
#发票申请模块  --stop

#结算申请 --start
@get("/settleApply_index")
def settleApply_index(request):
    return {
        '__template__': 'settleApply_index.html'
    }
@get("/settleApply_look")
def settleApply_form(**kv):
    return {
        '__template__': 'settleApply_look.html'
    }

#结算申请 --stop

#登陆模块  --start
@get("/login/index")
def login_index(request):
    return {
        '__template__': 'login_index.html'
    }





#业务报表  --start
@get("/board")
def board_index(request):
    return {
        '__template__': 'board.html'
    }
#业务报表   --stop

#用户管理   --start

@get("/manager")
def manager(request):
    return {
        '__template__': 'manager.html'
    }
@get("/manager/form")
def adminAdd(**kv):
    return {
        '__template__': 'adminAdd.html'
    }

@get("/manager/edit")
def  managerEdit(**kv):
    return {
        '__template__':'adminEdit.html'
    }

# 用户管理 ----- end


# 权限管理 ------- start
@get("/rule")
def rule(request):
    return {
        '__template__': 'rule_index.html'
    }
@get("/rule/form")
def rule_form(**kv):
    return {
        '__template__': 'rule_form.html'
    }

# 权限管理 ------- end


# 角色管理 ------- start
@get("/role")
def role(request):
    return {
        '__template__': 'role_index.html'
    }
@get("/role/form")
def role_form(**kv):
    return {
        '__template__': 'role_form.html'
    }

@get("/role/rule")
def role_rule(**kv):
    return {
        '__template__': 'role_rule.html'
    }
# 角色管理 ------- end

@get("/main_operate")
def main_operate(request):
    return {
        '__template__': 'main_operate.html'
    }


@get("/invoiceApply_comment")
def  invoiceApply_comment(**kv):
    return {
        '__template__': 'invoiceApply_comment.html'
    }

@get("/board/money_identify")
def money_identify(**kv):
    return {
        '__template__': 'board_money_identify.html'
    }

@get("/invoice_finish")
def invoice_finish(**kv):
    return {
        '__template__': 'invoice_finish.html'
    }