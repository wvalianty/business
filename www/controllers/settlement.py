#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"发票管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Income, Client, Settlement
from lib.common import obj2str, totalLimitP, addAffDateWhere, returnData
import client, income


# 结算状态
statusMap = (
    '未处理',
    '已处理',
)

# sql模板
sqlTpl = "SELECT {} FROM settlement s INNER JOIN income i ON s.`income_id`=i.`id` INNER JOIN `client` c ON i.`client_id` = c.`id`  where {}"

# 查询字段
selectField = "s.id,s.balance, s.status, s.add_date,s.finished_time, c.name company_name, c.invoice, i.income_id, i.money, i.aff_date"

@get('/apis/settlement/index')
async def index(*, keyword=None, month=None, status=None, isSearch=None, page=1, pageSize=10):

    page = int(page)
    pageSize = int(pageSize)
    
    # 合计收入金额
    totalMoney = 0
    # 合计结算金额
    totalBalance = 0

    where = '1=1'
    if keyword:
        where = "{} and i.income_id like '%%{}%%' or c.name like '%%{}%%'".format(where, keyword, keyword)
    if status and status.isdigit():
        where = "{} and s.status = {}".format(where, status)
    
    # 添加归属时间参数
    where = await addAffDateWhere(where, month, isSearch)

    # 获得总条数和分页数
    sql = sqlTpl.format('count(*) c', where)
    rs = await Settlement.query(sql)
    total, limit, p = totalLimitP(rs, page, pageSize)
    if total == 0:
        return dict(total = total, page = p, list = (), other = {
            'statusMap': statusMap,
            'totalMoney': 0,
            'totalBalance': 0
        })

    # 查询列表数据
    where = " %s order by %s limit %s" % (where, 'income_id desc', limit)
    sql = sqlTpl.format(selectField, where)
    lists = await Settlement.query(sql)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    for item in lists:
        statusDate = item['add_date']
        item['status_text'] = statusMap[item['status']]
        if int(item['status']) == 1:
            statusDate = item['finished_time']
        
        item['status_text'] = "%s<br/>%s" % (item['status_text'], statusDate)
        item['invoice'] = item['invoice'].replace('\n', '<br/>')
        totalMoney += item['money']
        totalBalance += item['balance']

    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'statusMap': statusMap,
            'totalMoney': round(totalMoney, 2),
            'totalBalance': round(totalBalance, 2),
        }
    }

@get('/apis/settlement/info')
async def info(*,id=0):

    id = int(id)

    if not id:
        return returnData(0, '查询', 'ID不存在')

    sql = "SELECT s.id, s.income_id,s.balance, i.aff_date,i.money,i.status, c.invoice,c.name company_name \
            FROM settlement s \
            INNER JOIN income i ON s.`income_id` = i.`id` \
            INNER JOIN `client` c ON i.`client_id` = c.`id` \
            WHERE s.id= %s" % id

    info = await Settlement.query(sql)

    if not info:
        return returnData(0, '查询')
    
    res = returnData(1, '查询')

    res['info'] = obj2str((info))[0]

    # 收入状态
    res['info']['status_text'] = income.statusMap[res['info']['status']]

    # 结算比例
    rate = round(res['info']['balance'] / res['info']['money'], 2) * 100
    res['info']['rate'] = "%s%%" % rate

    return res

@get('/apis/settlement/formInit')
async def formInit(*, id=0):
    """form表单初始化数据加载
    """

    # 获得所有收入ID，id,income_id
    incomeIdList = await Income.findAll(field="id,income_id")

    res = {
        'incomeIdList': incomeIdList
    }

    return res

@post('/apis/settlement/form')
async def form(*, id=0, income_id=0, balance=0):

    action = '添加'

    if  int(income_id) == 0:
        return returnData(0, action, '请选择收入ID')

    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info = await Settlement.find(id)
        info['income_id'] = income_id
        info['balance'] = balance
    else:
        info = dict(
            income_id = income_id,
            balance = balance
        )

    # 存在id则修改，不能存在id则添加
    rows = await Settlement(**info).save()

    return returnData(rows, action)

@get('/apis/settlement/del')
async def delete(*, id):

    action = '删除'
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, action, '缺少请求参数')

    rows = await Settlement.delete(id)

    return returnData(rows, action)


