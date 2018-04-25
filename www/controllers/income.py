#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"收入管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Income, Client, Business, IncomeNo
from lib.common import obj2str, exportExcel, totalLimitP, returnData, addAffDateWhere


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
async def index(*, keyword=None, month=None, status=None, mediaType=None, isExport=None, isSearch=None, page=1, pageSize=10):
    
    page = int(page)
    pageSize = int(pageSize)
    
    # 合计金额
    totalMoney = 0

    where = '1=1'
    if keyword:
        where = "{} and income_id like '%%{}%%' or c.name like '%%{}%%'".format(where, keyword, keyword)
    if status and status.isdigit():
        where = "{} and status = {}".format(where, status)
    if mediaType and mediaType.isdigit():
        where = "{} and media_type = {}".format(where, mediaType)
    
    where = await addAffDateWhere(where, month, isSearch)

    sql = "SELECT count(*) c FROM income i INNER JOIN `client` c ON i.`client_id` = c.`id` where {}".format(where)
    rs = await Income.query(sql)
    
    total, limit, p = totalLimitP(rs, page, pageSize)
    if total == 0:
        return dict(total = total, page = p, list = (), other = {
            'statusMap': statusMap,
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
        item['status_text'] = statusMap[item['status']]
        item['media_type'] = mediaTypeMap[item['media_type']]
        totalMoney += item['money']

    if isExport and int(isExport) == 1:
        return await export(lists)

    return {
        'total': total,
        'page': p,
        'list': lists,
        'other': {
            'statusMap': statusMap,
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

    res = {
        'clientList': clientList,
        'typeList': typeList
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
        status = kw.get('status', 0),
        media_type = kw.get('media_type', 0),
        cost = kw.get('cost', ''),
        aff_date = kw.get('aff_date')
    )

    if info['client_id'] == 0 or info['business_type'] == '':
        return returnData(0, action, '公司名称或业务类型不能为空')

    id = kw.get('id', 0)
    if id.isdigit() and int(id) > 0:
        action = '编辑'
        info['id'] = id
        info['income_id'] = kw.get('income_id', '')
    else:
        # 获得收入编号
        info['income_id'] = await getIncomeNo(info['aff_date'])
        await IncomeNo(income_no=info['income_id'], aff_date=info['aff_date']).save()
    
    rows = await Income(**info).save()

    return returnData(rows, action)

@get('/apis/income/del')
async def delete(*, id):

    action = '删除'
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, action, '缺少请求参数')

    try:
        rows = await Income.delete(id)
    except Exception as e:
        return returnData(0, action, '删除失败,请先删除发票管理中该收入ID条目')

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


    sql = "SELECT i.income_id, i.`aff_date`, i.`money`, i.status, \
            c.`name` company_name, c.`invoice` FROM income i \
            INNER JOIN `client` c ON i.`client_id` = c.`id` \
            where i.id = %s" % id

    info = await Income.query(sql)

    if not info:
        return returnData(0, '查询')
    
    res['info'] = obj2str((info))[0]

    res['info']['status_text'] = statusMap[res['info']['status']]
    
    return res

async def export(lists):
    """导出execl表格
    """
    fields = {
        'income_id': '收入ID',
        'company_name': '公司名称',
        'name': '业务名称',
        'aff_date': '归属时间',
        'money': '收入金额',
        'status': '结算进度',
        'media_type': '媒体类型',
        'cost': '渠道成本'
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
