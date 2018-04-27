from core.coreweb import get, post
from lib.models import Syslogs,Settlement,Invoice
import math,datetime,time,logging
from lib.common import obj2str


@get("/apis/main/index")
async def apis_main(*,page=1, pageSize=15):
    page = int(page)
    pageSize = int(pageSize)
    sql_re = 'select u.name,inc.income_id,sy.operate,sy.add_date,c.name gongsi,inc.name yewu,inc.money,inc.status from  syslog sy  inner join users u on u.name = sy.username inner join income inc on inc.id = sy.affetced_id  inner join client c on c.id = inc.client_id  where sy.`table` = "INCOME"  and u.is_delete = 0 and c.is_delete = 0 and inc.is_delete = 0 and sy.is_delete = 0   order by  sy.id desc limit 0,15  '
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
        invoice = await  Invoice.findAll(where=wherei)
        invoice = len(invoice)
    except:
        logging.ERROR("查询数据错误 数据库表 settlement invoice")
        return dict(total=total, page=(0, 0), list=res,other=({"settle":"error","invoice":"error"}))
    other = dict(settle=settle, invoice=invoice)

    for i in res:
        if i["status"] == 0:
            i["status"] = "代开票"
        elif i["status"] == 1:
            i["status"] = "未回款"
        elif i["status"] == 2:
            i["status"] = "已回款"
        else:
            i["status"] = "状态错误"


    return {
        "total":1,
        "page":(1,1),
        "list":res,
        "other":other
    }