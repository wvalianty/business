#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'model'

import time, uuid

from core.orm import *

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

def curr_datetime():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


class Client(Model):
    """客户表
    """

    __table__ = 'client'

    id = IntegerField(primary_key=True)
    name = StringField()
    indate = DateField()
    invoice = StringField()
    add_date = DateTimeField(default=curr_datetime)

class Business(Model):
    """业务类型表
    """
    
    __table__ = 'business_type'

    id = IntegerField(primary_key=True)
    type = StringField()

class Income(Model):
    """收入管理表
    """
    
    __table__ = 'income'

    id = IntegerField(primary_key=True)
    income_id = StringField()
    client_id = IntegerField()
    business_type = StringField(ddl=6)
    name = StringField()
    aff_date = DateField()
    money = FloatField()
    status = IntegerField()
    media_type = IntegerField()
    cost = StringField()
    add_date = DateTimeField(default=curr_datetime)

class Invoice(Model):
    __table__ = 'invoice'
    id = IntegerField(primary_key=True)
    client_id = StringField()
    income_id = StringField()
    info = StringField()
    add_date = DateTimeField()
    finished = IntegerField(default=0)
    finished_time = DateTimeField()
