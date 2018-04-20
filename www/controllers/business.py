#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"业务管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Business, Income, Settlement
from lib.common import obj2str, returnData, addAffDateWhere, totalLimitP

@get('/apis/business/index')
async def index(*, keyword=None, month=None,isSearch=0, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    currDate = time.strftime('%Y-%m-%d')
    where = '1=1'
    if keyword and keyword.strip() != '':
        where = "`business_type` like '%%{}%%'".format(keyword)
    
    where = await addAffDateWhere(where, month, isSearch)

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
    field='client_id, income_id, business_type type,aff_date,count(*) tfCount'
    lists = await Income.findAll(field=field, orderBy="aff_date desc",groupBy=groupBy, where=where, limit=limit)
   
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