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
    try:
        total = await Income.findNumber('count(id)', where)
    except:
        ValueError("sql error:Income.findNumber('count(id)', where)")
        return {
            "page": (1,1),
            "list": [{"id":"error"}]
        }
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=p, list=())
    try:
        incomes = await Income.findAll(orderBy='id desc', where=where, limit=limit)
    except:
        ValueError("sql error:Income.findAll(orderBy='id desc', where=where, limit=limit)")
        return {
            "page": (1, 1),
            "list": [{"id": "error"}]
        }
    L = []
    d = {}
    for income in incomes:
        d = {"lookid":income["id"],"date":income["aff_date"],"income":income["money"],"status":income["status"]}
        whereC = "id = %s" %(income["client_id"])
        try:
            clients = await Client.findAll(whereC)
        except:
            ValueError("sql error:Client.findAll(whereC)")
            return {
                "page": (1, 1),
                "list": [{"id": "error"}]
            }
        d['channel'] = clients[0]["name"]


        whereI = "income_id=%s" %(income["id"])
        try:
            settles = await Settlement.findAll(whereI)
        except:
            ValueError("sql error:Settlement.findAll(whereI)")
            return {
                "page": (1, 1),
                "list": [{"id": "error"}]
            }
        d["incomeM"] = settles[0]["balance"]
        d["percentage"] = str("%2.3f" %(d["incomeM"]/income["money"])) + "%"


        L.append(d)
    L = obj2str(L)
    return {
        "total":total,
        "page":p,
        "list":L
    }



#keyword 就是lookid  income.id
@get('/apis/settleApply_look/look')
async def settleApply_formIndex(*,keyword=None,action=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    wherei = "id = %s" % (keyword)
    try:
        incomes = await Income.findAll(where=wherei)
    except:
        ValueError("sql error:Income.findAll(where=wherei)")
        return {
            "page": (1, 1),
            "list": [{"name": "error"}]
        }
    client_id = incomes[0]["client_id"]

    wherec = "id = %s" %(client_id)
    try:
        clients = await Client.findAll(wherec=wherec)
    except:
        ValueError("sql error:Client.findAll(wherec=wherec)")
        return {
            "page": (1, 1),
            "list": [{"name": "error"}]
        }

    name = clients[0]["name"]
    limit = ((page - 1) * pageSize, pageSize)

    wheres = "client_id = %s" % (client_id)
    try:
        settles = await Settlement.findAll(orderBy='id desc',where=wheres,limit=limit)
    except:
        ValueError("sql error:Settlement.findAll(orderBy='id desc',where=wheres,limit=limit)")
        return {
            "page": (1, 1),
            "list": [{"name": "error"}]
        }
    settles = obj2str(settles)
    total = len(settles)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=p, list=())

    d = {}
    L = []
    for settle in settles:
        d = {"name":name,"date":settle["add_date"],"money":settle["balance"]}
        if settle["status"] == 0:
            d["status"] = "待处理"
        if settle["status"] == 1:
            d["status"] = "已处理"
        L.append(d)
    return {
        "total": total,
        "page": p,
        "list": L
    }

#id是收入id
@get('/settleApply_identify')
async def settleApply_identify(*,id):
    wherei = "id=%s" %(id)
    try:
        incomes = await Income.findAll(where=wherei)
    except:
        ValueError("sql error:Income.findAll(where=wherei)")
        return {
            'msg': '操作失败'
        }
    incomes[0]["status"] = 2
    incomes= obj2str(incomes)
    #time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rs = await Income(**incomes[0]).update()
    if rs == 1:
        return {
            'msg':'操作成功'
        }
    else:
        return {
            'msg':'操作失败'
        }
