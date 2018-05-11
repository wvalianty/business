#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"结算单管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Income, Client, Settlement
from lib.common import obj2str, totalLimitP, addAffDateWhere, returnData, replLineBreak
import client, income


# 结算状态
statusMap = (
    '未处理',
    '已处理',
)

# 结算单类型
stypeMap = (
    '对公',
    '对私'
)

# sql模板
sqlTpl = "SELECT {} FROM settlement s INNER JOIN income i ON s.`income_id`=i.`id` INNER JOIN `client` c ON s.`client_id` = c.`id`  where {}"

# 查询字段
selectField = "s.id,s.balance, s.status,s.stype,s.pay_company, s.add_date,s.finished_time, c.name company_name, c.invoice, i.income_id, i.money, i.aff_date"

@get('/apis/settlement/index')
async def index(*, keyword=None, rangeDate=None, status=None, isSearch=None, page=1, pageSize=10):

    page = int(page)
    pageSize = int(pageSize)
    
    # 合计收入金额
    totalMoney = 0
    # 合计结算金额
    totalBalance = 0

    where = "s.is_delete = 0"
    if keyword:
        where = "{} and i.income_id like '%%{}%%' or c.name like '%%{}%%'".format(where, keyword, keyword)
    if status and status.isdigit():
        where = "{} and s.status = {}".format(where, status)
    if rangeDate:
        startDate, endDate = rangeDate.split(' - ')
        if startDate and endDate:
            where = "{} and aff_date >= '{}' and aff_date < '{}'".format(
                where, startDate, endDate)

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
    where = " %s order by %s limit %s" % (where, 's.status asc, s.id desc', limit)
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
        item['invoice'] = replLineBreak(item['invoice'])
        item['stype_text'] = stypeMap[item['stype']]
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

    sql = "SELECT s.id,s.client_id, s.income_id,s.balance,s.pay_company, s.stype, i.aff_date,i.money,i.money_status,i.cost, i.inv_status, c.invoice,c.name company_name \
            FROM settlement s \
            INNER JOIN income i ON s.`income_id` = i.`id` \
            INNER JOIN `client` c ON s.`client_id` = c.`id` \
            WHERE s.id= %s" % id

    info = await Settlement.query(sql)

    if not info:
        return returnData(0, '查询')
    
    res = returnData(1, '查询')

    res['info'] = obj2str((info))[0]

    # 收入状态
    res['info']['money_status_text'] = income.moneyStatusMap[res['info']['money_status']]
    res['info']['inv_status_text'] = income.invStatusMap[res['info']['inv_status']]

    # 结算比例
    rate = round(res['info']['balance'] / res['info']['money'] * 100, 3)
    res['info']['rate'] = "%s%%" % rate

    return res

@get('/apis/settlement/formInit')
async def formInit(*, id=0):
    """form表单初始化数据加载
    """

    # 当前结算单的income_id
    inIdList = None
    if id and int(id) > 0:
        incomeIds = await Settlement.findNumber('income_id', where="id = %s" % id)
        inIdList = str(incomeIds).split(',')
    
    # 获得所有收入ID，id,income_id
    incomeIdList = await Income.findAll(field="id,income_id,cost", where='media_type=1')

    # 获得所有客户信息, id, name
    clientList = await Client.findAll(field="id, name")
    
    # 判断收入单的结算金额是否以结算完
    # incomeIdList[:] 拷贝incomeIdList, 不直接操作incomeIdList
    for item in incomeIdList[:]:
        if inIdList and str(item['id']) in inIdList:
            continue
        # 已结算金额
        settMoney = await Settlement.findNumber('sum(balance)', where="income_id=%s" % item['id']) or 0
        if float(settMoney) >= float(item['cost']):
            incomeIdList.remove(item)

    res = {
        'incomeIdList': incomeIdList,
        'clientList': clientList,
        'stypeMap': stypeMap
    }

    return res

@post('/apis/settlement/form')
async def form(*, id=0, income_id=0, client_id=0, balance=0, stype=0,pay_company=''):

    action = '添加'
    balance = float(balance)
    if  int(income_id) == 0:
        return returnData(0, action, '请选择收入ID')

    # 获得该收入单的渠道成本
    # 结算的金额不能超过渠道成本
    totalMoney = await Income.findNumber('cost', where="id=%s" % income_id) or 0
    totalMoney = float(totalMoney)

    # 获得已结算的金额
    settMoney = await Settlement.findNumber('sum(balance)', where="income_id=%s" % income_id) or 0
    settMoney = float(settMoney)


    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info = await Settlement.find(id)
        
        if (balance - info['balance'] + settMoney) > totalMoney:
            return returnData(0, action, "结算金额不能超过渠道成本,已结算:%s" % settMoney)

        info['income_id'] = income_id
        info['client_id'] = client_id
        info['stype'] = stype
        info['balance'] = balance
        info['pay_company'] = pay_company
    else:

        if (balance + settMoney) > totalMoney:
            return returnData(0, action, "结算金额不能超过渠道成本,已结算:%s" % settMoney)

        info = dict(
            income_id = income_id,
            client_id = client_id,
            balance = balance,
            pay_company = pay_company
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



async def getLastDate():
    """获得最后一条数据的月份
    """

    lastDateSql = "select aff_date from settlement s \
                    inner join income i On s.`income_id` = i.`id` \
                    where s.is_delete = 0 \
                    order by i.`aff_date` desc"
    
    rs = await Settlement.query(lastDateSql)
    if rs and len(rs) > 0:
        return rs[0]['aff_date']
    
    return None
