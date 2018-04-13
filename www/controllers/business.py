#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"业务管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Business, Income
from lib.common import obj2str

@get('/apis/business/index')
async def index(*, keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    currDate = time.strftime('%Y-%m-%d')
    where = '1=1'
    if keyword and keyword.strip() != '':
        where = "`business_type` like '%%{}%%'".format(keyword)

    groupBy = 'aff_date,business_type'
    sql = 'SELECT COUNT(*) c FROM (SELECT id FROM `income` where %s GROUP BY %s) t' % (where, groupBy)
    rs = await Income.query(sql)
    total = rs[0]['c']
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total = total, page = p, list = ())
  
    field='business_type type,aff_date,count(*) tfCount'
    lists = await Income.findAll(field=field, orderBy="aff_date desc",groupBy=groupBy, where=where, limit=limit)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    # 查询回款数
    for item in lists:
        where = "business_type = '%s' and aff_date = '%s' and status = 2" % (item.type, currDate)
        item['hkCount'] = await Income.findNumber('count(id)', where)

    # 获得所有业务类型
    types = await Business.findAll()
    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'types': types
        }
    }


@post('/apis/business/form')
async def form(*,id, btype):

    action = '添加'
    info = dict(
        type = btype.strip().upper(),
    )

    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info['id'] = id
        rows = await Business(**info).update()
    else:
        try:
            rows = await Business(**info).save()
        except Exception as e:
            return {
                'status': 0,
                'msg': '%s失败，%s' % (action, '业务ID已存在')
            }
        

    if rows == 1:
        return {
            'status': 1,
            'msg': '%s成功' % action
        }
    else:
        return {
            'status': 0,
            'msg': '%s失败' % action
        }
