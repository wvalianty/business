#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"index controller"

from core.coreweb import get, post


@get('/apis/index/index')
async def index(request):
    return {
        'name': 'lisi',
        'age': 33,
        'sex': '女'
    }