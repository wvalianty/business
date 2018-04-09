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
    __table__ = 'client'

    id = IntegerField(primary_key=True)
    name = StringField()
    indate = DateField()
    invoice = StringField()
    add_date = DateTimeField(default=curr_datetime)


class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id)
    email = StringField()
    passwd = StringField()
    admin = BooleanField()
    name = StringField()
    image = StringField(ddl="varchar(500)")
    created_at = FloatField(default=time.time)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id)
    user_id = StringField()
    user_name = StringField()
    user_image = StringField(ddl="varchar(500)")
    name = StringField()
    summary = StringField(ddl="varchar(200)")
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)
