#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"收入管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Income, Client, Business
from lib.common import obj2str


# 结算状态
statusMap = (
    '待开票',
    '未回款',
    '已回款'
)

# 媒体类型
mediaTypeMap = (
    '自媒体',
    '外媒'
)

@get('/apis/income/index')
async def index(*, keyword=None, month=None, status=None, mediaType=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    where = '1 = 1'
    if keyword:
        where = "income_id like '%%{}%%' or c.name like '%%{}%%'".format(keyword, keyword)
    if month and month.isdigit():
        year = time.strftime('%Y')
        month = month.zfill(2)
        where = "{} and aff_date like '{}-{}-%%'".format(where, year, month)
    if status and status.isdigit():
        where = "{} and status = {}".format(where, status)
    if mediaType and mediaType.isdigit():
        where = "{} and media_type = {}".format(where, mediaType)
    
    sql = "SELECT count(*) c FROM income i INNER JOIN `client` c ON i.`client_id` = c.`id` where {}".format(where)
    rs = await Income.query(sql)
    total = rs[0]['c']
    limit = "%s,%s" % ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total = total, page = p, list = ())

    sql = "SELECT i.*,c.name company_name FROM income i INNER JOIN `client` c ON i.`client_id` = c.`id` where %s order by %s limit %s" % (where, 'id desc', limit)

    lists = await Income.query(sql)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    for item in lists:
        item['status'] = statusMap[item['status']]
        item['media_type'] = mediaTypeMap[item['media_type']]

    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'statusMap': statusMap,
            'mediaTypeMap': mediaTypeMap
        }
    }

@get('/apis/income/info')
async def info(*,id):
    id = int(id)

    res = {
        'status': 1,
        'msg': '查询成功',
        'info': []
    }

    if not id:
        res['status'] = 0
        res['msg'] = 'id不存在'
        return res
    
    info = await Income.find(id)

    if not info:
        res['status'] = 0
        res['msg'] = '查询失败'
        return res

    res['info'] = obj2str([info])[0]

    return res

@get('/apis/income/formInit')
async def formInit(*, id):
    """form表单初始化数据加载
    """
    
    # 获得所有公司列表， id,name
    clientList = await Client.findAll(field='id,name')

    # 获得所有业务类型，id,type
    typeList = await Business.findAll(field='id,type')

    res = {
        'clientList': clientList,
        'typeList': typeList
    }

    if not id.isdigit() or int(id) == 0:
        # 收入编号
        res['income_id'] = await getIncomeNo()

    return res 

@post('/apis/income/form')
async def form(**kw):

    action = '添加'
    info = dict(
        client_id = kw.get('client_id', 0),
        business_type = kw.get('business_type', ''),
        name = kw.get('name', ''),
        money = kw.get('money', 0),
        status = kw.get('status', 0),
        media_type = kw.get('media_type', 0),
        cost = kw.get('cost', ''),
        aff_date = kw.get('aff_date')
    )

    if info['client_id'] == 0 or info['business_type'] == '':
        return {
            'status': 0,
            'msg': '公司名称或业务类型不能为空'
        }

    id = kw.get('id', 0)
    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info['id'] = id
        info['income_id'] = kw.get('income_id', '')
        rows = await Income(**info).update()
    else:
        info['income_id'] = await getIncomeNo()
        rows = await Income(**info).save()

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


@get('/apis/income/del')
async def delete(*, id):
    
    if not id.isdigit() or int(id) <= 0:
        return {
            'status': 0,
            'msg': '删除失败,缺少请求参数'
        }
    
    rows = await Client.delete(id)

    if rows == 1:
        return {
            'status': 1,
            'msg': '删除成功'
        }
    else:
        return {
            'status': 0,
            'msg': '删除失败'
        }


async def getIncomeNo():
    """获得收入编号
    """

    # 获得收入编号，编号规则 年月比数 180401
    where = "add_date like '{}%%'".format(time.strftime('%Y-%m-%d'))
    count = await Income.findNumber('count(id)')
    no = count + 1
    income_no = '%s%s' % (time.strftime('%y%m'), str(no).zfill(2))

    return income_no


