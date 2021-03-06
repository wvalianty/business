#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"发票管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Income, Client, Invoice
from lib.common import obj2str, returnData, totalLimitP, addAffDateWhere, replLineBreak
import client, income


# 结算状态
statusMap = (
    '未处理',
    '已处理',
)

# sql模板
sqlTpl = "SELECT {} FROM invoice inv \
            INNER JOIN income i ON i.`id` in (inv.`income_id`) \
            INNER JOIN `client` c ON i.`client_id` = c.`id`  \
            where {}"

# 查询字段
selectField = "inv.id,inv.info,inv.inv_money, inv.finished,inv.income_id in_id, inv.finished_time, inv.add_date,inv.comments, \
                c.name company_name, \
                i.income_id, i.money, i.aff_date"

@get('/apis/invoice/index')
async def index(*, keyword=None, rangeDate=None, status=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    year = time.strftime('%Y')
    
    # 合计金额
    totalMoney = 0

    where = "inv.is_delete = 0"
    if keyword:
        where = "{} and (i.income_id like '%%{}%%' or c.name like '%%{}%%')".format(where, keyword, keyword)
    if status and status.isdigit():
        where = "{} and finished = {}".format(where, status)
    if rangeDate:
        startDate, endDate = rangeDate.split(' - ')
        if startDate and endDate:
            where = "{} and aff_date >= '{}' and aff_date < '{}'".format(where, startDate, endDate)

    sql = sqlTpl.format('count(*) c', where)
    rs = await Invoice.query(sql)

    total, limit, p = totalLimitP(rs, page, pageSize)
    if total == 0:
        return dict(total = total, page = p, list = (), other = {
            'statusMap': statusMap,
            'totalMoney': round(totalMoney, 2)
        })

    where = " %s order by %s limit %s" % (where, 'inv.finished asc, inv.id desc', limit)
    sql = sqlTpl.format(selectField, where)
    lists = await Invoice.query(sql)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    for item in lists:
        statusDate = item['add_date']
        item['status_text'] = statusMap[item['finished']]
        if int(item['finished']) == 1:
            statusDate = item['finished_time']
        
        item['status_text'] = "%s<br/>%s" % (item['status_text'], statusDate)
        item['info'] = replLineBreak(item['info'])
        item['comments'] = replLineBreak(item['comments'])
        totalMoney += item['money']

        if item['in_id'].find(',') > 0:
            income_ids = await Income.findCols('income_id', "id in (%s)" % item['in_id'])
            if income_ids:
                item['income_id'] = ','.join(income_ids)


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
        return returnData(0, '查询', 'id不存在')

    sql = "SELECT inv.id, inv.income_id, i.aff_date,i.money, c.invoice,c.name company_name \
            FROM invoice inv \
            INNER JOIN income i ON inv.`income_id` = i.`id` \
            INNER JOIN `client` c ON i.`client_id` = c.`id` \
            WHERE inv.id = %s" % id

    info = await Invoice.query(sql)

    if not info:
        return returnData(0, '查询')

    res['info'] = obj2str((info))[0]

    return res

@get('/apis/invoice/formInit')
async def formInit(*, id=0):
    """form表单初始化数据加载
    """
    
    # 获得所有收入ID，id,income_id
    income_ids = await Invoice.findCols('income_id')
    if not income_ids:
        income_ids = ['0']

    income_id_str = ','.join(income_ids)
    sql = "SELECT id, income_id FROM income WHERE id NOT IN (%s) and inv_status = 0 and is_delete = 0;" % income_id_str
    incomeIdList = await Income.query(sql)

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
async def form(*, id=0, income_id=''):

    action = '添加'
    income_ids = income_id
    income_id = ''
    if not income_ids:
        return returnData(0, action, '请选择收入ID')

    # 判断该收入ID是否添加过发票信息
    rs = await Invoice.findNumber(selectField="count(*)", where="income_id in (%s)" % income_ids)

    if rs:
        return returnData(0, action, '收入ID已存在')

    # 如果是多个收入ID， 判断是否属于同一家公司
    rs = await Income.findCols("client_id", "id in (%s)" % income_ids, groupBy="client_id")

    if len(rs) > 1:
        return returnData(0, action , '收入ID不属于同一家公司，不能开一张票')

    # 获得收入信息
    
    income_id_arr = income_ids.split(',')
    incomeInfo = None
    for income_id in income_id_arr:
        rs = await income.detail(id=income_id)
        if not incomeInfo:
            incomeInfo = rs['info']
        else:
            incomeInfo['money'] += rs['info']['money']

    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info = Invoice.find(id)
        info['income_id'] = income_ids
        info['inv_money'] = incomeInfo['money']
        info['info'] = incomeInfo['invoice']
    else:
        info = dict(
            income_id = income_ids,
            inv_money = incomeInfo['money'],
            info = incomeInfo['invoice']
        )

    rows = await Invoice(**info).save()

    if rows == 1:
        return returnData(1, action)
    else:
        return returnData(0, action)


@get('/apis/invoice/del')
async def delete(*, id):

    if not id.isdigit() or int(id) <= 0:
        return returnData(0, '删除', '缺少请求参数')

    rows = await Invoice.delete(id)

    return returnData(rows, '删除')


async def getLastDate():
    """获得最后一条数据的月份
    """

    lastDateSql = "select aff_date from invoice inv \
                    inner join income i On inv.`income_id` = i.`id` \
                    where inv.is_delete = 0 \
                    order by i.`aff_date` desc"

    rs = await Invoice.query(lastDateSql)
    if rs and len(rs) > 0:
        return rs[0]['aff_date']

    return None
