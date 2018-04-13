from core.coreweb import get, post
from lib.models import Income, Client,Invoice
import math,datetime
from lib.common import obj2str

#keyword 用处
@get('/apis/invoiceApply_index/index')
async def invoiceApply_index(*, keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    where = '1 = 1'
    if keyword:
        where = "name like '%%{}%%'".format(keyword)

    total = await Income.findNumber('count(id)',where)
    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=p, list=())
    incomes = await Income.findAll(orderBy='id desc',where=where,limit=limit)
    clients = await Client.findAll(orderBy='id desc', where=where, limit=limit)
    invoices = await Invoice.findAll(orderBy='id desc',where=where,limit=limit)
    incomes = obj2str(incomes)
    clients = obj2str(clients)
    invoices = obj2str(invoices)
    d = {}
    rs = []

    for income in incomes:
        d = {"id":income["id"],"date":income["aff_date"],"money":income["money"]}
        for client in clients:
            if  income.client_id == client.id:
                d["client"] = client["name"]
                d["info"] = client["invoice"]
        for invoice in invoices:
            if income['id'] == invoice["income_id"]:
                d["finished"] = invoice["finished"]
                d['finished_time'] = invoice['finished_time']
        rs.append(d)

    return {
        'total':total,
        'page':p,
        'list':rs
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
                'msg':'确认成功'
            }
        else:
            return {
                'msg':'确认失败'
            }
    else:
        return {
            'msg':'没有此发票或者此发票有多个'
        }
