#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"发票管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Income, Client, Invoice
from lib.common import obj2str, exportExcel
import client, income


# 结算状态
statusMap = (
    '未处理',
    '已处理',
)

# sql模板
sqlTpl = "SELECT {} FROM invoice inv INNER JOIN income i ON inv.`income_id`=i.`id` INNER JOIN `client` c ON i.`client_id` = c.`id`  where {}"

# 查询字段
selectField = "inv.id,inv.info, inv.finished, inv.finished_time, inv.add_date,c.name company_name, i.income_id, i.money, i.aff_date"

@get('/apis/invoice/index')
async def index(*, keyword=None, month=None, status=None, isSearch=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    year = time.strftime('%Y')
    
    # 合计金额
    totalMoney = 0

    where = '1=1'
    if keyword:
        where = "{} and i.income_id like '%%{}%%' or c.name like '%%{}%%'".format(where, keyword, keyword)
    if status and status.isdigit():
        where = "{} and finished = {}".format(where, status)
    if month and month.isdigit():
        month = month.zfill(2)
    elif not month and not isSearch:
        lastDate = await Income.findNumber('aff_date', orderBy='aff_date desc')
        if lastDate:
            dates = lastDate.split('-')
            year, month = (dates[0], dates[1])
        else:
            month = time.strftime('%m')
    if month:
        where = "{} and aff_date like '{}-{}'".format(where, year, month)

    sql = sqlTpl.format('count(*) c', where)
    rs = await Invoice.query(sql)

    total = rs[0]['c']
    limit = "%s,%s" % ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total = total, page = p, list = (), other = {
            'statusMap': statusMap,
            'totalMoney': round(totalMoney, 2)
        })

    
    where = " %s order by %s" % (where, 'income_id desc')
    sql = sqlTpl.format(selectField, where)

    lists = await Invoice.query(sql)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    for item in lists:
        statusDate = item['add_date']
        item['status'] = statusMap[item['finished']]
        if int(item['finished']) == 1:
            statusDate = item['finished_time']
        
        item['status'] = "%s(%s)" % (item['status'], statusDate)
        item['info'] = item['info'].replace('\n', '<br/>')
        totalMoney += item['money']

    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'statusMap': statusMap,
            'totalMoney': round(totalMoney, 2)
        }
    }

@get('/apis/invoice/info')
async def info(*,id=0):

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

    sql = "SELECT inv.id, inv.income_id, i.aff_date,i.money, c.invoice,c.name company_name \
            FROM invoice inv \
            INNER JOIN income i ON inv.`income_id` = i.`id` \
            INNER JOIN `client` c ON i.`client_id` = c.`id`"

    info = await Invoice.query(sql)

    if not info:
        res['status'] = 0
        res['msg'] = '查询失败'
        return res

    res['info'] = obj2str((info))[0]

    return res


@get('/apis/invoice/incomeInfo')
async def incomeInfo(*,income_id):

    id = int(income_id)
    res = {
        'status': 1,
        'msg': '查询成功',
        'info': []
    }

    if not id:
        res['status'] = 0
        res['msg'] = '收入ID不存在'
        return res


    sql = "SELECT i.id, i.income_id, i.`aff_date`, i.`money`, c.`name` company_name, c.`invoice` FROM income i INNER JOIN `client` c ON i.`client_id` = c.`id` where i.id = %s" % id

    info = await Income.query(sql)

    if not info:
        res['status'] = 0
        res['msg'] = '查询失败'
        return res

    res['info'] = obj2str((info))[0]

    return res

@get('/apis/invoice/formInit')
async def formInit(*, id=0):
    """form表单初始化数据加载
    """

    # 获得所有收入ID，id,income_id
    if id == 0:
        sql = "SELECT id, income_id FROM income WHERE id NOT IN (SELECT income_id FROM invoice)"
        incomeIdList = await Income.query(sql)
    else:
        incomeIdList = await Income.findAll(field="id,income_id")

    if not incomeIdList:
        incomeIdList = [
            {
                'id': 0,
                'income_id': '没有符合要求的收入ID'
            }
        ]

    res = {
        'incomeIdList': incomeIdList
    }

    return res

@post('/apis/invoice/form')
async def form(*, id=0, income_id=0):

    action = '添加'

    if  int(income_id) == 0:
        return {
            'status': 0,
            'msg': '请选择收入ID'
        }

    # 判断该收入ID是否添加过发票信息
    rs = await Invoice.findNumber(selectField="count(*)", where="income_id=%s" % income_id)

    if rs:
        return {
            'status': 0,
            'msg': '该收入ID已经添加过发票信息，如需改变请选择编辑'
        }

    # 获得收入信息
    rs = await incomeInfo(income_id=income_id)

    invoiceInfo = dict(
        income_id = income_id,
        info = rs['info']['invoice']
    )

    if id.isdigit() and int(id) > 0:
        action = '编辑'
        invoiceInfo['id'] = id
        rows = await Invoice(**invoiceInfo).update()
    else:
        rows = await Invoice(**invoiceInfo).save()

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


@get('/apis/invoice/del')
async def delete(*, id):

    if not id.isdigit() or int(id) <= 0:
        return {
            'status': 0,
            'msg': '删除失败,缺少请求参数'
        }

    rows = await Invoice.delete(id)

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


