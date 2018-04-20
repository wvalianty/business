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
@get("/adminAdd")
def adminAdd(request):
    return {
        '__template__': 'adminAdd.html'
    }
