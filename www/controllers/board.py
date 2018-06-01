from core.coreweb import get, post
from lib.models import Income,Client
import math,datetime,time
from lib.common import obj2str,exportExcel,addAffDateWhere,returnData

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


async def export(lists):
    """导出execl表格
    """
    fields = {
        'income_table_id':"收入表id",
        'income_id': '收入ID',
        'name': '公司名称',
        'business_type': '业务类型',
        'cname': '业务名称',
        'aff_date': '归属时间',
        'money': '收入金额',
        'money_status':"回款状态",
        'inv_status':"开票状态",
        'media_type': '媒体类型',
        'income_company':'收款公司',
        'cost':'渠道成本',
    }
    return exportExcel('业务报表', fields, lists)

@get('/apis/board/index')
async def board_index(*, keyword=None, rangeDate=None, moneyStatus=None,invStatus=None, mediaType=None, isExport=None,  page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    totalMoney = 0
    affField = "aff_date"
    where = "where  inc.is_delete = 0 and c.is_delete = 0 "

    if keyword:
        where = "{}  and inc.income_id like '%%{}%%' or c.name like '%%{}%%'".format(where, keyword, keyword)

    localtimes = time.localtime()
    currYear = localtimes[0]
    currMonth = localtimes[1]
    if not rangeDate or rangeDate.find(' - ') != 7:
        endYear = currYear
        endMonth = currMonth + 1
        if currMonth == 13:
            endMonth = 1
            endYear += 1

        startDate = "%s-%s" % (currYear, str(currMonth).zfill(2))
        endDate = "%s-%s" % (endYear, str(endMonth).zfill(2))
    if rangeDate:
        startDate, endDate = rangeDate.split(' - ')
        if startDate == endDate:
            where = " {} and {} = '{}' ".format(where, affField, startDate)
        else:
            where = " {} and {} >= '{}' and {} <= '{}' ".format(where, affField, startDate, affField, endDate)
    if invStatus:
        where = "{} and inv_status={} " .format(where,int(invStatus))
    if mediaType:
        where = "{} and media_type={} " .format(where,int(mediaType))
    if moneyStatus:
        where = "{} and money_status={} " .format(where,int(moneyStatus))


    # if not isExport or int(isExport) != 1:
    #     sql = '%s limit %s' % (sql, limit)


    limit = "%s,%s" % ((page - 1) * pageSize, pageSize)
    sql_total = 'select count(*) cc from income inc inner join client c on inc.client_id = c.id %s' %(where)
    re = await Income.query(sql_total)
    total = re[0]["cc"]
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=(0,0), list=(), other={
            'totalMoney': round(totalMoney, 2)
        })

    sql_re = 'SELECT inc.cost,inc.income_id,c.name,inc.business_type,inc.name cname,inc.aff_date,inc.money,inc.money_status,inc.inv_status,inc.media_type,inc.id income_table_id,inc.income_company,inc.return_money_date from income inc inner join client c on inc.client_id = c.id ' + where + 'order by  inc.income_id  desc limit %s' %(limit)
    res = await Income.query(sql_re)
    res = obj2str(res)
    for item in res:
        # item['status'] = statusMap[item['status']]
        item['media_type'] = mediaTypeMap[item['media_type']]
        totalMoney = totalMoney + item['money']


    if isExport and int(isExport) == 1 and rangeDate:
        startDate, endDate = rangeDate.split(' - ')
        if startDate == endDate:
            where_t = " {} and {} = '{}' ".format(where, affField, startDate)
        else:
            where_t = " {} and {} >= '{}' and {} <= '{}' ".format(where, affField, startDate, affField, endDate)
        sql_re_t = 'SELECT inc.cost,inc.income_id,c.name,inc.business_type,inc.name cname,inc.aff_date,inc.money,inc.money_status,inc.inv_status,inc.media_type,inc.id income_table_id,inc.income_company,inc.return_money_date from income inc inner join client c on inc.client_id = c.id ' + where_t + 'order by  inc.income_id  desc'
        res_t = await Income.query(sql_re_t)
        res_t = obj2str(res_t)
        for item in res_t:
            if item["money_status"] == 0:
                item["money_status"] = "未回款"
            if item["money_status"] == 1:
                item["money_status"] = "已回款"
            if item["inv_status"] == 0:
                item["inv_status"] = "未开票"
            if item["inv_status"] == 1:
                item["inv_status"] = "不开票"
            if item["inv_status"] == 2:
                item["inv_status"] = "已开票"
        return await export(res_t)

    if isExport and int(isExport) == 1:
        for item in res:
            if item["money_status"] == 0:
                item["money_status"] = "未回款"
            if item["money_status"] == 1:
                item["money_status"] = "已回款"
            if item["inv_status"] == 0:
                item["inv_status"] = "未开票"
            if item["inv_status"] == 1:
                item["inv_status"] = "不开票"
            if item["inv_status"] == 2:
                item["inv_status"] = "已开票"
        return await export(res)

    return {
        'total':total,
        'page':p,
        'list':res,
        'other':{
            'moneyStatusMap': moneyStatusMap,
            'invStatusMap': invStatusMap,
            'mediaTypeMap': mediaTypeMap,
            'totalMoney': round(totalMoney, 2)
        }
    }


@get("/apis/board/info")
async def  board_info(*,id):
    income_id = int(id)
    income = await  Income.find(income_id)
    res = dict(
        id = income["id"],
        return_money_date = income["return_money_date"],
        # return_money_date = "2018-08-08",
        money_status = income["money_status"]
    )
    return {
        "info":res
    }
# return returnData(1,"失败")
@post("/apis/board/form")
async def board_form(*,return_money_date,money_status,id):
    if money_status and int(money_status) != 1:
        return returnData(0,"选择未回款不能提交")
    if return_money_date and money_status and id:
        income = await  Income.find(id)
        income["return_money_date"] = return_money_date
        income["money_status"] = money_status
        rows = await Income(**income).update()
        if rows == 1:
            return returnData(1,"回款")
        else:
            return returnData(0,"回款")
    else:
        return returnData(0,"回款")

#/board/invoice_identify?id=68
@get("/board/invoice_identify")
async def invoice_identify(*,id):
    if id:
        income = await Income.find(int(id))
        income["inv_status"] = 2
        rows = await Income(**income).update()
        if rows == 1:
            return returnData(1,"已开票操作")
        else:
            return returnData(0,"已开票操作")
    else:
        return returnData(0,"请求")