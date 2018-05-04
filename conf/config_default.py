#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'默认配置文件, 这个文件通常不需要修改'

configs = {
    "db": {
        "host": "rm-bp125wn81demb3djuo.mysql.rds.aliyuncs.com",
        "port": 3306,
        "user": "root",
        "password": "W8UnSRjCCqz4JEdVw4",
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
