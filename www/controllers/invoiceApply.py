from core.coreweb import get, post
from lib.models import Income, Client,Invoice
import math,datetime
from lib.common import obj2str

#keyword 用处
@get('/apis/invoiceApply_index/index')
async def invoiceApply_index(*, keyword=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

    #where = 'where 1 = 1 and inv.is_delete = 0 and inc.is_delete = 0 and c.is_delete = 0 '
    # 发票申请，发票，收入，客户，一者删除，发票就不显示了
    sql_total = 'select count(*)  co  from invoice where is_delete = 0'

    try:
        rs = await Invoice.query(sql_total)
        if rs[0]["co"] == 0:
            return dict(total=0, page=(0, 0), list=())
    except:
        raise ValueError("查询数据库错误,/apis/invoiceApply_index/index")
    total = rs[0]["co"]

    limit = ((page - 1) * pageSize, pageSize)
    p = (math.ceil(total / pageSize), page)
    sql_res1 = 'select inv.income_id income_id_ids,inv.id invid,inv.info,inv.finished,inv.finished_time from invoice  inv where is_delete = 0 order by inv.id desc limit %s,%s '  %(limit[0],limit[1])
    try:
        res1 = await Invoice.query(sql_res1)
    except:
        raise ValueError("/apis/invoiceApply_index/index,应该是表字段有变化,total查询已经通过了")
    res1 = obj2str(res1)
    for i in res1:
        income_ids = i["income_id_ids"].split(",")
        for j in income_ids:
            sql_res2 = 'SELECT c.name,inc.aff_date,inc.income_id,inc.money FROM income inc INNER JOIN CLIENT c ON inc.`client_id` = c.id where inc.id = %s' %(j)
            try:
                res2 = await  Income.query(sql_res2)
            except:
                raise ValueError("/apis/invoiceApply_index/index，二次查询错误")
            i["name"] = res2[0]["name"]
            i["aff_date"] = res2[0]["aff_date"]
            i["income_id"] = res2[0]["income_id"]
            i["money"] = res2[0]["money"]
    for j in range(len(res2)):
        if res2[j]["finished"] == 0:
            t = res2[j]
            res2.pop(j)
            res2.insert(0,t)
    print(res2)
    return {
        'total':total,
        'page':p,
        'list':res2
    }

#inv.id
@get('/apis/finish')
async def apis_finish(*,id):
    if not id.isdigit() or int(id) <= 0:
        return {
            'msg': '确认失败,缺少请求参数'
        }
    where = "id = %s" %(id)
    invoices = await Invoice.findAll(where)
    invoices = obj2str(invoices)

    if len(invoices) == 1:
        invoiceId = invoices[0]["id"]
        income_id = invoices[0]["income_id"]
        wherei = " id = %s " %(income_id)
        incomes = await  Income.findAll(where=wherei)
        incomes[0]["status"] = 1
        r_status = await  Income(**incomes[0]).save()
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

