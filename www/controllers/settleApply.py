from core.coreweb import get, post
from lib.models import Income, Settlement,Client,Invoice
import math,datetime
from lib.common import obj2str

@get('/apis/settleApply_index/index')
async def settleApply_index(*,keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    where = ' where 1 = 1 and inc.status = 2 and settle.is_delete = 0 and inc.is_delete = 0 and c.is_delete = 0 '
    #if search
    # if keyword:
    #     where = "name like '%%{}%%'".format(keyword)

    # count_id = '%s' %("settle.id")
    sql_total = 'select count(*) co  from settlement settle left join income inc on settle.income_id = inc.id inner join client c  on settle.client_id = c.id %s ' %(where)
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
    sql_res = 'select inc.id,inc.income_id,c.name,inc.aff_date,inc.money,inc.status,settle.balance,settle.status sstatus from settlement settle left join income inc on settle.income_id = inc.id inner join client c  on settle.client_id = c.id where settle.is_delete = 0 and inc.is_delete = 0 and inc.status = 2 and c.is_delete = 0  order by settle.id desc limit %s,%s' %(limit[0],limit[1])
    try:
        res = await Settlement.query(sql_res)
    except:
        raise ValueError("查询数据库错误,/apis/settleApply_index/index")
    res = obj2str(res)
    try:
        for i in range(len(res)):
            res[i]["percentage"] = '%5.2f' %(res[i]["balance"]/res[i]["money"]*100)
            res[i]["percentage"] = str(res[i]["percentage"]) + "%"
        for j in range(len(res)):
            if res[j]["sstatus"] == 1:
                t = res[j]
                res.pop(j)
                res.append(t)
    except:
        return dict(total=total, page=p, list=())
    return {
        "total":total,
        "page":p,
        "list":res
    }



#keyword 就是 income.id
@get('/apis/settleApply_look/look')
async def settleApply_formIndex(*,keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    income_id = int(keyword)


    total = 1
    p = (1, 1)

    where = " income_id = %s" %(income_id)
    try:
        res = await Invoice.findAll(where=where)
        res = obj2str(res)
    except:
        raise ValueError("/apis/settleApply_look/look  数据出现错误")
    for info in res:
        info["info"] = info["info"].replace("\n","</br>")

    return {
        "total": total,
        "page": p,
        "list": res
    }
    # wherei = " id = %s " %(income_id)
    # try:
    #     incomes = await Income.findAll(where=wherei)
    #     incomes = obj2str(incomes)
    # except:
    #     raise ValueError("/apis/settleApply_look/look查询数据库失败")
    # client_id = incomes[0]["client_id"]
    #
    #
    # sql_total = 'select count(*) co from settlement settle inner join income inc on settle.income_id = inc.id  inner join client c on inc.client_id = c.id where settle.income_id = %s and c.is_delete = 0 and inc.is_delete = 0 and settle.is_delete = 0 and settle.client_id = c.id ' %(income_id)
    # re = await  Client.query(sql_total)
    # try:
    #     reL = await  Client.query(sql_total)
    #     total = reL[0]["co"]
    #     if total == 0:
    #         return dict(total=total, page=(0,0), list=())
    # except:
    #     raise ValueError("查询数据库错误,/apis/settleApply_look/look")
    # p = (math.ceil(total / pageSize), page)
    #
    # limit = ((page - 1) * pageSize, pageSize)
    # sql_res = ' select c.name,settle.balance,inc.status,inc.add_date from settlement settle inner join income inc on settle.income_id = inc.id  inner join client c on inc.client_id = c.id where settle.income_id = %s and c.is_delete = 0 and inc.is_delete = 0 and settle.is_delete = 0 and settle.client_id = c.id order by inc.id desc  limit %s,%s' %(income_id,limit[0],limit[1])
    # try:
    #     res = await  Client.query(sql_res)
    #     res = obj2str(res)
    # except:
    #     raise ValueError("查询数据库错误,/apis/settleApply_look/look")


#id是收入id
@get('/settleApply_identify')
async def settleApply_identify(*,id):
    wheres = " income_id=%s " %(id)
    try:
        settles = await Settlement.findAll(where=wheres)
        settles = obj2str(settles)
    except:
        ValueError("sql error:Income.findAll(where=wheres)")
        return {
            'msg': '操作失败'
        }
    settles[0]["status"] = 1
    settles[0]["finished_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rs = await Settlement(**settles[0]).update()
    if rs == 1:
        return {
            'msg':'操作成功',
            'status':'1'
        }
    else:
        return {
            'msg':'操作失败'
        }
