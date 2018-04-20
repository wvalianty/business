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
    indate_start = DateField()
    indate_end = DateField()
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
    income_id = StringField(ddl=6)
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
    client_id = IntegerField()
    income_id = IntegerField()
    info = StringField()
    add_date = DateTimeField()
    finished = IntegerField(default=0)
    finished_time = DateTimeField()

class Settlement(Model):
    __table__ = 'settlement'
    id = IntegerField(primary_key=True)
    income_id = IntegerField()
    client_id = IntegerField()
    balance = FloatField()
    status = IntegerField()
    add_date = DateTimeField()

class Syslog(Model):
    __table__ = 'syslog'
    id = IntegerField(primary_key=True)
    uid = StringField()
    operate =  StringField()
    table = StringField()
    module = StringField()
    sql = StringField()
    datetime = DateTimeField()

class IncomeNo(Model):
    
    __table__ = 'income_no'
    income_no = StringField(primary_key=True)
    aff_date = StringField()

class Users(Model):
    __table__ = 'users'
    id = StringField(primary_key=True)
    phoneN = StringField()
    email = StringField()
    passwd = StringField()
    role = IntegerField()
    name = StringField()
    created_at =  DateTimeField()
    admin = IntegerField()