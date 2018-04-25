#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'python web app'

import logging
import asyncio, os, sys, json, time
from datetime import datetime
from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from lib.common import cookie2user, COOKIE_NAME, ctr_dir, datetime_filter
import core.orm as orm
from core.coreweb import add_route, add_routes, add_static
from config import configs

db = configs.db

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#0、管理员
#1、运营侧
#2、财务侧

finance = set(["/board","/apis/main/index","/","/apis/board/index","/apis/invoiceApply_index/index","/apis/settleApply_index/index","/apis/settleApply_look/look","/settleApply_identify","/invoiceApply_index","/settleApply_index","/settleApply_look","/login/index","/main"])
operate = set(["/apis/income/formInit","/apis/income/getIncomeId","/apis/income/form","/apis/invoice/formInit","/invoice/form","/apis/business/index","/apis/settlement/del","/apis/settlement/form","/apis/settlement/formInit","/apis/settlement/info","/apis/settlement/index","/settlement","/apis/business/index","/apis/business/form","/apis/client/form","/apis/client/index","/apis/invoice/index","/invoice","/","/client","/client/form","/apis/income/index","/business","/business/form","/income","/income/form","/login/index","/main"])
manager = set(["/apis/manager/del","/apis/board/index","/syslog","/apis/manager/index","/apis/manager/info","/apis/manager/form","/api/login","/manager/edit","/manager/form","/manager"])
super_user = finance | operate | manager
roles = {0:super_user,1:operate,2:finance}

def init_jinja2(app, **kw):
    logging.debug('init jinjia2...')
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '<%'),
        variable_end_string = kw.get('varialbe_end_string', '%>'),
        auto_reload = kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(sys.path[0], 'templates')
    logging.debug('set jinja2 template path:%s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__tmplating__'] = env


async def logger_factory(app, handler):
    async def logger(request):
        logging.debug('Request:%s %s' % (request.method, request.path))
        return await handler(request)
    return logger

async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.debug('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form:%s' % str(request.__data__))
        return (await handler(request))
    return parse_data

async def response_factory(app, handler):
    async def response(request):
        logging.debug('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'applicattion/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json'
                return resp
            else:
                resp = web.Response(body=app['__tmplating__'].get_template(
                    template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r > 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t > 100 and t < 600:
                return web.Response(r, str(m))
        
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response




async def auth_factory(app, handler):
    @asyncio.coroutine
    def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        #从cookie能解析 用户名
        if cookie_str:
            try:
                user = yield from cookie2user(cookie_str)
                if user:
                    if request.path.startswith('/static/'):
                        return (yield from handler(request))
                    if request.path.startswith('/api/login'):
                        return (yield from handler(request))
                    if request.path.startswith('/apis/main/index'):
                        return (yield from handler(request))
                    logging.info('set current user: %s' % user.email)
                    request.__user__ = user['email']
                    role = user.role
                    modules = roles[int(role)]
                    if request.path in modules:
                	    return (yield from handler(request))
            except:
                return web.HTTPFound('/login/index')
                #return (yield from handler(request))

            #先放宽一些，其他后续再改
        elif request.path.startswith('/login/index') and (request.__user__ is None):
            return (yield from handler(request))
        elif request.path.startswith('/static/'):
            return (yield from handler(request))
        elif request.path.startswith('/api/login'):
            return (yield from handler(request))
        else:
            return web.HTTPFound('/login/index')
            #return web.HTTPMovedPermanently('/login/index')
    return auth

async def init(loop):
    await orm.create_pool(loop=loop, host=db.host, port=db.port, user=db.user, password=db.password, db=db.database)
    app = web.Application(loop=loop, middlewares=[
        auth_factory,logger_factory, data_factory, response_factory
    ])
    #auth_factory,
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'handlers')

    # 将controllers文件夹下的所有文件，都添加的路由中
    for root, dirs, files in os.walk(ctr_dir):
        if not files:
            break
        for action in files:
            if action.startswith("_") or not action.endswith('.py'):
                continue
            add_routes(app, action[:-3])
        break

    add_static(app)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', configs.app.port)
    logging.info('server started at http://127.0.0.1:%s' % configs.app.port)
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
