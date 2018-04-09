#! /usr/bin/env python3
# -*- coding:utf-8 -*-

# import orm, asyncio, os, sys
# from models import User, Blog, Comment

from lib.common import cookie2user, COOKIE_NAME

# loop = asyncio.get_event_loop()

async def test():
    await orm.create_pool(loop, user='www-data', password='www-data', db='awesome')

    # u = User(name='Test', email='test@qq.com', passwd='123123', image='about:black')

    # await u.save()

    user = User()
    # data = await user.findAll()
    # count = await user.findNumber('count(*)')

    info = await user.findOne()

    print(info)


# loop.run_until_complete(test())

