#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'model'

import time, uuid

from core.orm import *

def next_id():
    return '%1d' % (int(time.time() * 1000))

def curr_datetime():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


class Client(Model):
    """客户表
    """

    __table__ = 'client'

    id = IntegerField(primary_key=True)
    name = StringField()
    indate_start = DateField()
    indate_end = DateField()
    invoice = StringField()
    add_date = DateTimeField(default=curr_datetime)
    is_delete = IntegerField(default=0)

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
    income_id = StringField(ddl=6)
    client_id = IntegerField()
    business_type = StringField(ddl=6)
    name = StringField()
    aff_date = StringField()
    money = FloatField()
    status = IntegerField()
    media_type = IntegerField()
    cost = StringField()
    add_date = DateTimeField(default=curr_datetime)
    is_delete = IntegerField(default=0)

class Invoice(Model):
    __table__ = 'invoice'
    id = IntegerField(primary_key=True)
    income_id = IntegerField()
    info = StringField()
    add_date = DateTimeField(default=curr_datetime)
    finished = IntegerField(default=0)
    finished_time = DateTimeField()
    is_delete = IntegerField(default=0)

class Settlement(Model):
    __table__ = 'settlement'
    id = IntegerField(primary_key=True)
    income_id = IntegerField()
    client_id = IntegerField()
    balance = FloatField()
    status = IntegerField(default=0)
    add_date = DateTimeField(default=curr_datetime)
    finished_time = DateTimeField()
    is_delete = IntegerField(default=0)

class Syslogs(Model):
    __table__ = 'syslog'
    id = IntegerField(primary_key=True)
    username = StringField()
    affetced_id = IntegerField()
    operate =  StringField()
    table = StringField()
    module = StringField()
    sql = StringField()
    add_date = DateTimeField(default=curr_datetime)
    is_delete = IntegerField(default=0)

class IncomeNo(Model):
    
    __table__ = 'income_no'
    id = IntegerField(primary_key=True)
    income_no = StringField()
    aff_date = StringField()

class Users(Model):
    __table__ = 'users'
    id = IntegerField(primary_key=True)
    phone = StringField()
    email = StringField()
    passwd = StringField()
    role = IntegerField()
    name = StringField()
    created_at =  DateTimeField()
    is_delete = IntegerField(default=0)
