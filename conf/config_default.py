#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'默认配置文件, 这个文件通常不需要修改'

configs = {
    "db": {
        "host": "",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "business"
    }, 
    "session": {
        "secret": "AwEsOmE"
    },
    "cookie": {
        "name": "python_business"
    },
    'app': {
        'port': '8080'
    },
    'user': {
        'name': ''
    }
}
