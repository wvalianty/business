#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'url handlers'

from lib.common import *
from core.coreweb import get, post
from lib.models import User, Blog, next_id
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
    
@get('/client')
async def client(request):
    return {
        '__template__': 'client_index.html'
    }

""" 
@get('/')
async def blogs(request):
    # 获得用户cookie
    user = dict()
    if COOKIE_NAME in request.cookies:
        cookie_str = request.cookies[COOKIE_NAME]
        user = await cookie2user(cookie_str)

    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='test2222 blog', summary=summary, create_at=time.time()-120),
        Blog(id='2', name='Somethin news blog', summary=summary, create_at=time.time()-3600),
        Blog(id='3', name='Learn Swift blog', summary=summary, create_at=time.time()-7200),
    ]
    
    return {
        '__template__': 'blogs.html',
        'blogs': blogs,
        'user': user
    }

@get('/api/users')
async def api_get_users(*, page=1, pageSize = 2):
    num = await User.findNumber('count(id)')
    limit = ((page - 1) * pageSize, pageSize)
    p = (page, pageSize)
    if num == 0:
        return dict(page = p, users = ())
    users = await User.findAll(orderBy='created_at desc', limit=limit)
    for u in users:
        u.passwd = '******'
    return dict(page = p, users = users)


@get('/register')
async def register(request):
    
    return {
        '__template__': 'register.html'
    }

@get('/signin')
async def signin():
    return {
        '__template__': 'signin.html'
    }

@post('/signin')
async def signin_post(*, email, passwd):
    if not email or not email.strip():
        raise APIValueError('email')
    if not passwd or not passwd.strip():
        raise APIValueError('passwd')

    user = await User.findOne('*', 'email=?', [email])
    if not user:
        raise APIValueError('email', 'Email not exist')
    
    sha1_passwd = '%s:%s' % (user['id'], passwd)
    passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
    if user['passwd'] != passwd:
        raise APIValueError('passwd', 'Invalid password')
    
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    r.content_type = 'application/json'
    user['passwd'] = '******'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@post('/register')
async def register_post(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not email.strip():
        raise APIValueError('email')
    if not passwd or not passwd.strip():
        raise APIValueError('passwd')
    
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed email is already in use.')
    
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    userInfo = dict(
        id = uid,
        name = name.strip(),
        email = email.strip(),
        passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
        image = 'http://img01.store.sogou.com/net/a/04/link?appid=100520040&url=http://i02.pic.sogou.com/3c28af542f2d49f7-8437bbc8e07dde51-26796eca2eee9ec501a1630d4307af73_qq',
    )
    user = User(**userInfo)
    await user.save()

    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/signout')
async def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@post('/api/add_blogs')
async def api_create_blog(request, *, name, summary, content):
    ''' 创建博客 '''
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')
    
    data = dict(
        id = next_id(),
        user_id = request.__user__.id,
        user_name = request.__user__.name,
        user_image = request.__user__.image,
        name = name.strip(),
        summary = summary.strip(),
        content = content.strip()
    )

    blog = Blog(**data)
    await blog.save()
    return blog
 """