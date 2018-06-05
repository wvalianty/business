#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"业务管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Business, Income, Settlement
from lib.common import obj2str, returnData, addAffDateWhere, totalLimitP

@get('/apis/business/index')
async def index(*, keyword=None,media_type=None, rangeDate=None, isSearch=0, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    where = await addAffDateWhere(rangeDate, isSearch)

    if keyword and keyword.strip() != '':
        where = "{} and `business_type` like '%%{}%%'".format(where, keyword)
    if media_type is not None and media_type.isdigit():
        where = "{} and `media_type` = {}".format(where, media_type) 

    baseWhere = where

    # 查询数据总数
    groupBy = 'aff_date,business_type'
    sql = 'SELECT COUNT(*) c FROM ( \
                SELECT id FROM `income` where %s GROUP BY %s \
            ) t' % (where, groupBy)
    rs = await Income.query(sql)
    
    total, limit, p = totalLimitP(rs, page, pageSize, True)
   
    # 获得所有业务类型
    types = await Business.findAll()

    if total == 0:
        return dict(total = total, page = p, list = (), other = {'types': types})
    
    # 查询数据列表
    field='client_id, income_id, business_type type,aff_date,count(*) tfCount, sum(money) tfMoney'
    lists = await Income.findAll(field=field, orderBy="aff_date desc",groupBy=groupBy, where=where, limit=limit)

    for item in lists:
       
        # 查询回款数
        where = "%s and business_type = '%s' and money_status = 1" % (baseWhere, item.type) 
        item['hkCount'] = await Income.findNumber('count(id)', where)

        # 回款金额
        hkMoney = await Income.findNumber('sum(money)', where)
        item['hkMoney'] = round(hkMoney, 2) if hkMoney else 0

        # 投放金额
        item['tfMoney'] = round(item['tfMoney'], 2)

    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'types': types
        }
    }


@post('/apis/business/form')
async def form(*,id, btype=None):

    action = '添加'
    if not btype or btype.strip() == '':
        return returnData(0, action, '业务ID不能为空')

    info = dict(
        type = btype.strip().upper(),
    )

    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info['id'] = id

    try:
        rows = await Business(**info).save()
        return returnData(rows, action)
    except Exception as e:
        return returnData(0, action, '业务ID已存在')
