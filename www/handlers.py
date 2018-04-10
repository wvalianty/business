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