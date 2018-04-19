#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"业务管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Business, Income, Settlement
from lib.common import obj2str

@get('/apis/business/index')
async def index(*, keyword=None, month=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    year = time.strftime('%Y')
    currDate = time.strftime('%Y-%m-%d')
    where = '1=1'
    if keyword and keyword.strip() != '':
        where = "`business_type` like '%%{}%%'".format(keyword)
    if month and month.isdigit():
        month = month.zfill(2)
    else:
        lastDate = await Income.findNumber('aff_date', orderBy='aff_date desc')
        if lastDate:
            dates = lastDate.split('-')
            year, month = (dates[0], dates[1])
        else:
            month = time.strftime('%m')
        
    where = "{} and aff_date like '{}-{}'".format(where, year, month)

    # 查询数据总数
    groupBy = 'aff_date,business_type'
    sql = 'SELECT COUNT(*) c FROM (SELECT id FROM `income` where %s GROUP BY %s) t' % (where, groupBy)
    rs = await Income.query(sql)
    total = rs[0]['c']
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)

    # 获得所有业务类型
    types = await Business.findAll()

    if total == 0:
        return dict(total = total, page = p, list = (), other = {'types': types})
    
    # 查询数据列表
    field='client_id, income_id, business_type type,aff_date,count(*) tfCount'
    lists = await Income.findAll(field=field, orderBy="aff_date desc",groupBy=groupBy, where=where, limit=limit)

    # 将获得数据中的日期转换为字符串
    # lists = obj2str(lists)

   
    for item in lists:

        # 查询回款数
        where = "business_type = '%s' and aff_date = '%s' and status = 2" % (item.type, currDate)
        item['hkCount'] = await Income.findNumber('count(id)', where)

        # 投放金额
        where = "client_id = %s" % item.client_id
        tfMoney = await Income.findNumber('sum(money)', where)
        item['tfMoney'] = round(tfMoney, 2) if tfMoney else 0  

        # 回款金额
        where = 'income_id = %s' % item.income_id
        hkMoney = await Settlement.findNumber('sum(balance)', where)
        item['hkMoney'] = round(hkMoney, 2) if hkMoney else 0

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
