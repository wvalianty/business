from core.coreweb import get, post
from lib.models import Income, Settlement,Client
import math,datetime,time
from lib.common import obj2str,returnData,exportExcel


async def export(lists):
    """导出execl表格
    """
    fields = {
        'settle_id':"结算表id",
        'income_id': '收入ID',
        'name': '渠道名称',
        'aff_date': '归属时间',
        'money': '收入金额',
        'status':"收入状态",
        'percentage':"结算比例",
        'balance':"结算金额",
        'pay_company': '请款公司',
    }
    return exportExcel('收入报表', fields, lists)

#结算搜索时间  暂时按结算添加时间
@get('/apis/settleApply_index/index')
async def settleApply_index(*, keyword=None, rangeDate=None, isExport=None, isSearch=None,  page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    where = ' where inc.money_status = 1 and settle.is_delete = 0 and inc.is_delete = 0 and c.is_delete = 0 '
    affField = "settle.add_date"

    if not isSearch:
        sql_recentMonth = "select {} add_date from settlement settle order by id desc limit 0,1".format(affField)
        time_ = await Settlement.query(sql_recentMonth)
        if time_:
            time_ = obj2str(time_)
            months_ = time_[0]["add_date"].split(" ")[0].split("-")
            month_ = months_[1]
            year = months_[0]
        else:
            return dict(total=0, page=(0, 0), list=())
        startDate = year + "-" + month_ + "-01" + " 00:00:00"
        endDate = year + "-" + month_ + "-31" + " 24:00:00"
        where = "{} and {} >= '{}' and {} <= '{}'".format(where, affField, startDate, affField, endDate)

    if keyword and not rangeDate:
        settle_id = int(keyword)
        where = " {} and settle.id = {} " .format(where,settle_id)

    if rangeDate and  isSearch:
        startDate, endDate = rangeDate.split(' - ')
        where = "{} and {} >= '{}' and {} <= '{}'".format(where, affField, startDate, affField, endDate)


    totalMoney = 0
    sql_total = 'select count(*) co  from settlement settle left join income inc on settle.income_id = inc.id inner join `client` c  on settle.client_id = c.id %s ' %(where)
    try:
        reL = await Settlement.query(sql_total)
        if reL[0]["co"] == 0:
            return dict(total=0, page=(0, 0), list=())
    except:
        return dict(total=0, page=(0,0), list=())
        raise ValueError("查询数据库错误,/apis/settleApply_index/index")
    total = reL[0]["co"]

    if total == 0:
        return dict(total=total, page=(0,0), list=())
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    sql_res = 'select settle.id settle_id,inc.id,inc.income_id,c.name,c.id cid ,inc.aff_date,inc.money,inc.money_status status,settle.balance,settle.status sstatus,settle.pay_company,settle.finished_time from settlement settle left join income inc on settle.income_id = inc.id inner join `client` c  on settle.client_id = c.id ' + where + 'order by settle.id desc limit %s,%s' %(limit[0],limit[1])
    try:
        res = await Settlement.query(sql_res)
    except:
        raise ValueError("查询数据库错误,/apis/settleApply_index/index")
    res = obj2str(res)
    try:
        for i in range(len(res)):
            res[i]["percentage"] = '%5.2f' %(res[i]["balance"]/res[i]["money"]*100)
            res[i]["percentage"] = str(res[i]["percentage"]) + "%"
            totalMoney = totalMoney + res[i]["balance"]
        for j in range(len(res)):
            if res[j]["sstatus"] == 1:
                t = res[j]
                res.pop(j)
                res.append(t)
    except:
        return dict(total=total, page=p, list=())
    if isExport and int(isExport) == 1:
        for item in res:
            if item["status"] == 0:
                item["status"] = "未回款"
            if item["status"] == 1:
                item["status"] = "已回款"
        return await export(res)

    return {
        "total":total,
        "page":p,
        "list":res,
        "other":{
            "totalMoney":totalMoney
        }
    }



#keyword 就是 cid
@get('/apis/settleApply_look/look')
async def settleApply_formIndex(*,keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    cid = int(keyword)
    try:
        res_tmp = await Client.find(cid)
        total = 1
        p = (1, 1)
        res = {}
        res["invoice"] = res_tmp["invoice"].replace("\n", "</br>")
        return {
            "total": total,
            "page": p,
            "list": res
        }
    except:
        raise ValueError("/apis/settleApply_look/look  数据出现错误")



#id是settle id
@get('/settleApply_identify')
async def settleApply_identify(*,id):
    settle_id = int(id)
    settle = await Settlement.find(settle_id)
    settle["status"] = 1
    settle["finished_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rows = await Settlement(**settle).update()
    if rows == 1:
        return returnData(1,"结算完成")
    else:
        return returnData(0,"结算完成")

    # wheres = " income_id=%s " %(id)
    # try:
    #     settles = await Settlement.findAll(where=wheres)
    #     settles = obj2str(settles)
    # except:
    #     ValueError("sql error:Income.findAll(where=wheres)")
    #     return {
    #         'msg': '操作失败'
    #     }
    # settles[0]["status"] = 1
    # settles[0]["finished_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # rs = await Settlement(**settles[0]).update()
    # if rs == 1:
    #     return {
    #         'msg':'操作成功',
    #         'status':'1'
    #     }
    # else:
    #     return {
    #         'msg':'操作失败'
    #     }
