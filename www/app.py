#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'python web app'

import asyncio, os, sys, json, time,logging
from datetime import datetime
from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from lib.common import cookie2user, COOKIE_NAME, ctr_dir,obj2str
import core.orm as orm
from core.coreweb import add_route, add_routes, add_static
from config import configs
from lib.models import Role,Users,Rule

db = configs.db

COOKIE_NAME = configs.cookie.name
_COOKIE_KEY = configs.session.secret

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


async  def auth_err(request):
    #return web.Response(body=b'<h1>please check your authority,please understand yourself in your  heart where there is a number,then contact the manager ,thankyou</h1>', content_type='text/html')
    return web.Response(body=b'<h1>right error or  backend function error</h1>', content_type='text/html')

async def auth_factory(app, handler):
    @asyncio.coroutine
    def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        if request.path.startswith('/static/') or request.path.startswith('/api/login') or request.path.startswith('/login/index')  or request.path.startswith('/apis'):
            return (yield from handler(request))
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:

            #module可以写到全局变量里面
            modules = []
            try:
                user = yield from cookie2user(cookie_str)
                if user:
                    logging.info('set current user: %s' % user.email)
                    request.__user__ = user['email']
                    configs.user.name = user['email']
                    roles = yield from  Role.find(int(user.role))
                    rules = roles["rules"]
                    for ruleid in rules.split(","):
                        if ruleid != "":
                            route = yield from Rule.find(int(ruleid))
                            if route:
                                modules.append(route["route"])
                    if request.path in modules:
                        return (yield from handler(request))
                    else:
                        return (yield from auth_err(request))
                else:
                    return (yield from auth_err(request))
            except:
                return (yield from auth_err(request))
        else:
            return web.HTTPFound('/login/index')
    return auth


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






async def init(loop):
    await orm.create_pool(loop=loop, host=db.host, port=db.port, user=db.user, password=db.password, db=db.database)
    app = web.Application(loop=loop, middlewares=[
        logger_factory, data_factory, response_factory
    ])
    #auth_factory,
    init_jinja2(app)
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
