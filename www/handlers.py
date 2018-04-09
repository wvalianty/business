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

@get('/client_form')
async def client_form(**kw):
    return {
        '__template__': 'client_form.html'
    }

# 客户管理模块 ----- end