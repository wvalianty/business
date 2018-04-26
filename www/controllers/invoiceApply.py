from core.coreweb import get, post
from lib.models import Income, Client,Invoice
import math,datetime
from lib.common import obj2str

#keyword 用处
@get('/apis/invoiceApply_index/index')
async def invoiceApply_index(*, keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    where = '1 = 1 and inv.is_delete = 0 and inc.is_delete = 0 and c.is_delete = 0 '

    sql_total = 'select count(inv.id) c  from invoice inv inner join income inc on inv.income_id = inc.id inner join client c on c.id = inc.client_id'
    rs = await Invoice.query(sql_total)
    try:
        total = rs[0]["c"]
    except:
        return dict(total=total, page=(0,0), list=())
    if total == 0:
        return dict(total=total, page=(0,0), list=())
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=p, list=())
    sql_res = 'select inc.income_id,c.name,inc.aff_date,inc.money,inv.id invid,inv.info,inv.finished,inv.finished_time from invoice inv inner join income inc on inv.income_id = inc.id inner join client c on c.id = inc.client_id where inv.is_delete = 0 and inc.is_delete = 0 and c.is_delete = 0  order by inc.id desc limit %s,%s '  %(limit[0],limit[1])
    res = await Invoice.query(sql_res)
    res = obj2str(res)

    return {
        'total':total,
        'page':p,
        'list':res
    }


@get('/apis/finish')
async def apis_finish(*,id):
    if not id.isdigit() or int(id) <= 0:
        return {
            'msg': '确认失败,缺少请求参数'
        }
    where = "income_id = %s" %(id)
    invoices = await Invoice.findAll(where)
    invoices = obj2str(invoices)
    if len(invoices) == 1:
        invoiceId = invoices[0]["id"]
        if invoices[0]["finished"] == 1:
            return {
                'msg': '已经确认过了！'
            }
        invoices[0]["finished"] = 1
        invoices[0]["finished_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rs = await Invoice(**invoices[0]).update()
        if rs == 1:
            return {
                'msg':'确认成功',
                'status':1
            }
        else:
            return {
                'msg':'确认失败'
            }
    else:
        return {
            'msg':'没有此发票或者此发票有多个'
        }
