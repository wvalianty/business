from core.coreweb import get, post
from lib.models import Income, Settlement,Client
import math,datetime
from lib.common import obj2str

@get('/apis/settleApply_index/index')
async def settleApply_index(*,keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    where = '1 = 1'
    #if search
    if keyword:
        where = "name like '%%{}%%'".format(keyword)

    count_id = '%s' %("settle.id")
    sql_total = 'select count(%s) c  from settlement settle inner join income inc on settle.income_id = inc.id inner join client c  on settle.client_id = c.id' %(count_id)
    re = await Settlement.query(sql_total)
    total = re[0]["c"]
    if total == 0:
        return dict(total=total, page=p, list=())
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=p, list=())
    sql_res = 'select inc.id,inc.income_id,c.name,inc.aff_date,inc.money,inc.status,settle.balance,settle.status sstatus from settlement settle inner join income inc on settle.income_id = inc.id inner join client c  on settle.client_id = c.id order by settle.id desc limit %s,%s' %(limit[0],limit[1])
    res = await Settlement.query(sql_res)
    res = obj2str(res)
    for i in range(len(res)):
        res[i]["percentage"] = '%3.3f' %(res[i]["balance"]/res[i]["money"])

    return {
        "total":total,
        "page":p,
        "list":res
    }



#keyword 就是lookid  income.id
@get('/apis/settleApply_look/look')
async def settleApply_formIndex(*,keyword=None,action=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    income_id = int(keyword)
    sql_total = 'select count(*) co  from client c inner join settlement settle on c.id = settle.client_id inner join income inc on c.id = inc.client_id where c.id in (select client_id  cid from income where id =%s)' %(income_id)
    re = await  Client.query(sql_total)
    total = re[0]["co"]
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=p, list=())
    limit = ((page - 1) * pageSize, pageSize)
    sql_res = ' select c.name,settle.balance,inc.status,inc.add_date from client c inner join settlement settle on c.id = settle.client_id inner join income inc on c.id = inc.client_id where c.id in (select client_id from income where id =%s) order by inc.id desc  limit %s,%s' %(income_id,limit[0],limit[1])
    res = await  Client.query(sql_res)
    res = obj2str(res)
    return {
        "total": total,
        "page": p,
        "list": res
    }

#id是收入id
@get('/settleApply_identify')
async def settleApply_identify(*,id):
    wheres = "income_id=%s" %(id)
    try:
        settles = await Settlement.findAll(where=wheres)
    except:
        ValueError("sql error:Income.findAll(where=wherei)")
        return {
            'msg': '操作失败'
        }
    settles[0]["status"] = 1
    settles= obj2str(settles)
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
