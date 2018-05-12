from core.coreweb import get, post
from lib.models import Syslogs,Settlement,Users,Income,Client,Invoice
import math,datetime,time,logging
from lib.common import obj2str
from config import configs

@get("/apis/main/index")
async def apis_main(*,page=1, pageSize=15):
    email = configs.user.name#
    page = int(page)
    pageSize = int(pageSize)
    sql_re = 'select sy.id sys_id,u.name,inc.income_id,sy.operate,sy.add_date,c.name gongsi,inc.name yewu,inc.money,inc.inv_status from  syslog sy  inner join users u on u.email = sy.username inner join income inc on inc.id = sy.affetced_id  inner join client c on c.id = inc.client_id  where sy.`table` in  ("INCOME","SETTLEMENT")  and u.is_delete = 0 and c.is_delete = 0 and inc.is_delete = 0 and sy.is_delete = 0   order by  sy.id desc limit 0,15  '
    try:
        res = await Syslogs.query(sql_re)
    except:
        logging.ERROR("查询income,syslog,数据库错误,url /apis/main/index")
        res = ()
    res = obj2str(res)
    if len(res) < 1:
        total = 0
    else:
        total = len(res)
    wheres = ' status = 0 '
    wherei = ' finished = 0 '
    try:
        settle = await Settlement.findAll(where=wheres)
        settle = len(settle)
        income = await  Invoice.findAll(where=wherei)
        invoice = len(income)
    except:
        logging.ERROR("查询数据错误 数据库表 settlement invoice")
        return dict(total=total, page=(0, 0), list=res,other=({"settle":"error","invoice":"error"}))
    other = dict(settle=settle, invoice=invoice)

    for i in res:
        if i["inv_status"] == 0:
            i["inv_status"] = "未开票"
        elif i["inv_status"] == 1:
            i["inv_status"] = "不开票"
        elif i["inv_status"] == 2:
            i["inv_status"] = "已开票"
        else:
            i["inv_status"] = "状态错误"


    return {
        "total":1,
        "page":(1,1),
        "list":res,
        "other":other
    }

#datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@get("/apis/main_operate/index")
async def apis_main_operate(*,page=1,pageSize=15):
    email = configs.user.name  #
    page = int(page)
    pageSize = int(pageSize)
    sql_re = 'select sy.id sys_id,u.name,inc.income_id,sy.operate,sy.add_date,c.name gongsi,inc.name yewu,inc.money,inc.inv_status from  syslog sy  inner join users u on u.email = sy.username inner join income inc on inc.id = sy.affetced_id  inner join client c on c.id = inc.client_id  where sy.`table` in  ("INCOME","SETTLEMENT")  and u.is_delete = 0 and c.is_delete = 0 and inc.is_delete = 0 and sy.is_delete = 0   order by  sy.id desc limit 0,15  '
    try:
        res = await Syslogs.query(sql_re)
    except:
        logging.ERROR("查询income,syslog,数据库错误,url /apis/main/index")
        res = ()
    res = obj2str(res)
    if len(res) < 1:
        total = 0
    else:
        total = len(res)
    wheres = ' status = 0 '
    wherei = ' finished = 0 '
    try:
        settle = await Settlement.findAll(where=wheres)
        settle = len(settle)
        income = await  Invoice.findAll(where=wherei)
        invoice = len(income)
    except:
        logging.ERROR("查询数据错误 数据库表 settlement invoice")
        return dict(total=total, page=(0, 0), list=res, other=({"settle": "error", "invoice": "error"}))
    week_ago = (datetime.datetime.now() - datetime.timedelta(hours=24 * 7)).strftime('%Y-%m-%d')
    week_sql = "SELECT * FROM `client` WHERE indate_end < '{}'".format(week_ago)
    clients = await Client.query(week_sql)
    expire_ = len(clients)

    other = dict(settle=settle, invoice=invoice,expire_=expire_)

    for i in res:
        if i["inv_status"] == 0:
            i["inv_status"] = "未开票"
        elif i["inv_status"] == 1:
            i["inv_status"] = "不开票"
        elif i["inv_status"] == 2:
            i["inv_status"] = "已开票"
        else:
            i["inv_status"] = "状态错误"



    return {
        "total": 1,
        "page": (1, 1),
        "list": res,
        "other": other
    }