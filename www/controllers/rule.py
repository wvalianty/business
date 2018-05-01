#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"收入管理模块"
import math, datetime, time
from core.coreweb import get, post
from lib.models import Rule
from lib.common import obj2str, totalLimitP, returnData, ruleTree

# 菜单状态
menuStatusMap = (
    '隐藏',
    '显示'
)

# 权限状态
authopenMap = (
    '无需验证',
    '需要验证'
)

@get('/apis/rule/index')
async def index(*, keyword=None, page=1, pageSize=10):

    page = int(page)
    pageSize = int(pageSize)

    where = "1=1"
    if keyword:
        where = "{} and title like '%%{}%%'".format(where, keyword)

    total = await Rule.findNumber('count(*)', where)

    total, limit, p = totalLimitP(total, page, pageSize, True)
    if total == 0:
        return dict(total = total, page = p, list = ())

    lists = await Rule.findAll(where=where, orderBy="sort desc, id asc")

    # 将获得数据中的日期转换为字符串
    lists = obj2str(lists)

    for item in lists:
        item['menustatus_text'] = menuStatusMap[item['menustatus']]
        item['authopen_text'] = authopenMap[item['authopen']]

    lists = ruleTree(lists)

    return {
        'total': total,
        'page': p,
        'list': lists
    }

@get('/apis/rule/info')
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

@get('/apis/rule/formInit')
async def formInit(*, id):
    """form表单初始化数据加载
    """

    # 获得所有规则列表
    lists = await Rule.findAll(field="id, pid, title",orderBy='sort desc')
    lists = ruleTree(lists)

    res = {
        'ruleList': lists
    }

    return res

@post('/apis/rule/form')
async def form(**kw):

    action = '添加'
    info = dict(
        pid = kw.get('pid', 0),
        title = kw.get('title', ''),
        route = kw.get('route', ''),
        icon = kw.get('icon', 0),
        menustatus = kw.get('menustatus', 0),
    )

    if info['title'] == '':
        return returnData(0, action, '权限名称或路由不能为空')

    id = kw.get('id', 0)
    if id.isdigit() and int(id) > 0:
        action = '编辑'
        oldInfo = await Rule.find(id)
        info = dict(oldInfo, info)

    rows = await Rule(**info).save()

    return returnData(rows, action)

@get('/apis/rule/del')
async def delete(*, id):

    action = '删除'
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, action, '缺少请求参数')

    try:
        rows = await Income.delete(id)
    except Exception as e:
        return returnData(0, action, '请先删除发票管理中该收入ID条目')

    try:
        # 删除对应的发票单
        inv_rows = await Invoice.delete(where="%s in (income_id) and finished = 0" % id)
    except Exception as e:
        return returnData(0, action , '删除发票单失败')

    return returnData(rows, action)

@get('/apis/rule/getIncomeId')
async def getIncomeId(*, aff_date=None):

    income_id = await getIncomeNo(aff_date)

    return {
        'status': 1,
        'income_id': income_id
    }

@get('/apis/rule/detail')
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


@get('/apis/rule/getSumMoney')
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
