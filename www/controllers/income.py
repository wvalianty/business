#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"收入管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Income, Client, Business, IncomeNo, Invoice, Company
from lib.common import obj2str, exportExcel, totalLimitP, returnData, addAffDateWhere


# 结算状态
moneyStatusMap = (
    '未回款',
    '已回款',
)

# 开票状态
invStatusMap = (
    '未开票',
    '不开票',
    '已开票'
)

# 媒体类型
mediaTypeMap = (
    '自媒体',
    '外媒'
)

@get('/apis/income/index')
async def index(*, keyword=None, rangeDate=None, moneyStatus=None,invStatus=None, mediaType=None, isExport=None, isSearch=None, year=None, page=1, pageSize=50):

    page = int(page)
    pageSize = int(pageSize)

    # 合计金额, 只统计当前页面显示数据
    totalMoney = 0

    where = baseWhere = await addAffDateWhere(rangeDate, isSearch, 'i.is_delete')
    if keyword:
        where = "{} and (income_id like '%%{}%%' or c.name like '%%{}%%')".format(where, keyword, keyword)
    if moneyStatus and moneyStatus.isdigit():
        where = "{} and money_status = {}".format(where, moneyStatus)
    if invStatus and invStatus.isdigit():
        where = "{} and inv_status = {}".format(where, invStatus)
    if mediaType and mediaType.isdigit():
        where = "{} and media_type = {}".format(where, mediaType)
    
    sql = "SELECT count(*) c FROM income i INNER JOIN `client` c ON i.`client_id` = c.`id` where {}".format(where)
    rs = await Income.query(sql)

    total, limit, p = totalLimitP(rs, page, pageSize)
    if total == 0:
        return dict(total = total, page = p, list = (), other = {
            'moneyStatusMap': moneyStatusMap,
            'invStatusMap': invStatusMap,
            'mediaTypeMap': mediaTypeMap,
            'totalMoney': round(totalMoney, 2)
        })

    sql = "SELECT i.*,c.name company_name FROM income i INNER JOIN `client` c ON i.`client_id` = c.`id` where %s order by %s" % (where, 'income_id desc')

    if not isExport or int(isExport) != 1:
        sql = '%s limit %s' % (sql, limit)

    lists = await Income.query(sql)

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    for item in lists:
        item['money_status_text'] = moneyStatusMap[item['money_status']]
        item['inv_status_text'] = invStatusMap[item['inv_status']]
        item['media_type_text'] = mediaTypeMap[item['media_type']]
        totalMoney += item['money']

    if isExport and int(isExport) == 1:
        return await export(lists)

    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'moneyStatusMap': moneyStatusMap,
            'invStatusMap': invStatusMap,
            'mediaTypeMap': mediaTypeMap,
            'totalMoney': round(totalMoney, 2)
        }
    }

@get('/apis/income/info')
async def info(*,id):

    action = '查询'
    id = int(id)

    if not id:
        return returnData(0, action, 'ID不存在')

    info = await Income.find(id)
    if not info:
        return returnData(0, action)

    res = returnData(1, action)
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

    # 获得所有收款公司, id, company_name
    companyList = await Company.findAll(field='id, company_name', orderBy='sort desc')

    res = {
        'moneyStatusMap': moneyStatusMap,
        'invStatusMap': invStatusMap,
        'mediaStatusMap': mediaTypeMap,
        'clientList': clientList,
        'typeList': typeList,
        'companyList': companyList
    }

    return res

@post('/apis/income/form')
async def form(**kw):

    action = '添加'
    info = dict(
        client_id = kw.get('client_id', 0),
        business_type = kw.get('business_type', ''),
        name = kw.get('name', ''),
        money = kw.get('money', 0),
        income_company = kw.get('income_company', ''),
        money_status=0,
        inv_status=kw.get('inv_status', 0),
        media_type = kw.get('media_type', 0),
        cost = kw.get('cost', ''),
        cost_detail=kw.get('cost_detail', ''),
        aff_date = kw.get('aff_date')
    )

    if info['client_id'] == 0 or info['business_type'] == '':
        return returnData(0, action, '公司名称或业务类型不能为空')

    id = kw.get('id', 0)
    if id.isdigit() and int(id) > 0:
        action = '编辑'
        # 如果是已回款状态，则只能编辑 渠道成本
        oldInfo = await Income.find(id)
        if oldInfo['money_status'] == 1:
            oldInfo['cost'] = info['cost']
            oldInfo['cost_detail'] = info['cost_detail']
            info = oldInfo
        else:
            info['id'] = id
            info['money_status'] = oldInfo['money_status'] # 运营端不能编辑回款进度
            info['income_id'] = kw.get('income_id', '')
        
        # 检查开票状态，如果已开票，则不能修改开票属性，否则开票属性可以为0,1
        if oldInfo['inv_status'] == 2 or int(info['inv_status']) >= 2:
            info['inv_status'] = oldInfo['inv_status']

    else:
        # 获得收入编号
        info['income_id'] = await getIncomeNo(info['aff_date'])
        # 新增的时候，发票状态不能为已开票
        if int(info['inv_status']) >= 2:
            return returnData(0, action)
        await IncomeNo(income_no=info['income_id'], aff_date=info['aff_date']).save()

    rows = await Income(**info).save()

    return returnData(rows, action)

@get('/apis/income/del')
async def delete(*, id):
    # 1. 已回款收入单不能删除
    # 2. 未回款收入单不可以删除
    # 3. 待开票收入单可删除，但要删除未处理的发票信息
    action = '删除'
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, action, '缺少请求参数')

    try:
        where = "money_status<1 and inv_status<2 and id = %s" % id
        rows = await Income.delete(None, where=where)
    except Exception as e:
        return returnData(0, action)
    
    # 删除对应的未处理的发票单
    if rows:
        await Invoice.delete(where="%s in (income_id) and finished = 0" % id)

    return returnData(rows, action)

@get('/apis/income/getIncomeId')
async def getIncomeId(*, aff_date=None):

    income_id = await getIncomeNo(aff_date)

    return {
        'status': 1,
        'income_id': income_id
    }

@get('/apis/income/detail')
async def detail(*, id=0):
    """获得收入报表详情
    """

    res = {
        'status': 1,
        'msg': '查询成功',
        'info': []
    }

    if not id:
        return returnData(0, '查询', '收入ID不存在')


    sql = "SELECT i.income_id, i.`aff_date`, i.`money`, i.money_status,i.inv_status,i.cost, \
            c.`name` company_name, c.`invoice` FROM income i \
            INNER JOIN `client` c ON i.`client_id` = c.`id` \
            where i.id = %s" % id

    info = await Income.query(sql)

    if not info:
        return returnData(0, '查询')

    res['info'] = obj2str((info))[0]

    res['info']['money_status_text'] = moneyStatusMap[res['info']['money_status']]
    res['info']['inv_status_text'] = invStatusMap[res['info']['inv_status']]

    return res


@get('/apis/income/getSumMoney')
async def getSumMoney(*, ids=None):
    """根据多个收入id，返回总金额

    Keyword Arguments:
        ids {str} -- [收入ID，多个用逗号分隔] (default: {''})
    """
    if not ids:
        return returnData(0, '开票金额获取', '缺少参数')

    totatlMoney = await Income.findNumber('sum(money)', "id in (%s)" % ids)

    return {
        'status': 1,
        'msg': '开票金额获取成功',
        'inv_money': totatlMoney
    }

async def export(lists):
    """导出execl表格
    """
    fields = {
        'income_id': '收入ID',
        'company_name': '公司名称',
        'business_type': '业务类型',
        'name': '业务名称',
        'aff_date': '归属时间',
        'money': '收入金额',
        'money_status_text': '回款进度',
        'inv_status_text': '开票进度',
        'media_type_text': '媒体类型',
        'cost': '渠道成本',
        'cost_detail': '渠道成本明细'
    }

    return exportExcel('收入报表', fields, lists)


async def getIncomeNo(aff_date=None):
    """获得收入编号
    """

    if not aff_date:
        return None

    # 获得收入编号，编号规则 年月比数 180401
    where = "aff_date = '{}'".format(aff_date)
    # count = await Income.findNumber('count(id)', where)
    count = await IncomeNo.findNumber('count(*)', where)
    no = count + 1
    income_no = '%s%s' % (aff_date.replace('-','')[2:], str(no).zfill(2))

    return income_no
