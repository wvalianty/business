from core.coreweb import get, post
from lib.models import Syslogs,Settlement,Invoice
import math,datetime,time,logging
from lib.common import obj2str


@get("/apis/main/index")
async def apis_main(*,page=1, pageSize=15):
    page = int(page)
    pageSize = int(pageSize)

    sql_re = 'select u.name,inc.income_id,sys.operate,sys.add_date,c.name gongsi,inc.name yewu,inc.money,inc.status from  syslog sys  inner join income inc  on sys.affetced_id = inc.id inner join users u on u.name = sys.username inner join client c  on inc.client_id = c.id   where  sys.module = "INCOME"  order by  sys.id desc limit 0,15 '

    try:
        res = await Syslogs.query(sql_re)
    except:
        total = 0
        return dict(total=total, page=(0,0), list=())
    if len(res) < 1:
        total = 0
        return dict(total=total, page=(0, 0), list=())
    res = obj2str(res)
    for i in res:
        if i["status"] == 0:
            i["status"] = "代开票"
        elif i["status"] == 1:
            i["status"] = "未回款"
        elif i["status"] == 2:
            i["status"] = "已回款"
        else:
            i["status"] = "状态错误"

    wheres = ' status = 0 '
    wherei = ' finished = 0 '
    try:
        settle = await Settlement.findAll(where = wheres)
        settle = len(settle)
        invoice = await  Invoice.findAll(where = wherei)
        invoice = len(invoice)
    except:
        logging.ERROR("查询需要处理的发票数错误")
        settle = 0
        invoice = 0
    other=dict(settle=settle,invoice=invoice)
    return {
        "total":1,
        "page":(1,1),
        "list":res,
        "other":other
    }