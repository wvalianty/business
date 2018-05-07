from core.coreweb import get, post
from lib.models import Income, Client,Invoice
import math,datetime
from lib.common import obj2str,returnData

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
    #页面大小问题考虑不了
    sql_res1 = 'select inv.income_id income_id_ids,inv.id invid,inv.info,inv.finished,inv.finished_time from invoice  inv where is_delete = 0 order by inv.id desc limit %s,%s '  %(limit[0],limit[1])
    try:
        res1 = await Invoice.query(sql_res1)
    except:
        raise ValueError("/apis/invoiceApply_index/index,应该是表字段有变化,total查询已经通过了")
    res1 = obj2str(res1)
    res = []
    for i in res1:
        i["info"] = i["info"].replace('\n', '<br/>')
        income_ids = i["income_id_ids"].split(",")
        if len(income_ids) == 1:
                sql_res2 = 'SELECT c.name,inc.aff_date,inc.income_id,inc.money FROM income inc INNER JOIN CLIENT c ON inc.`client_id` = c.id where inc.id = %s' %(income_ids[0])
                try:
                    res2 = await  Income.query(sql_res2)
                except:
                    raise ValueError("/apis/invoiceApply_index/index，二次查询错误")
                i["show"] = 1
                i["rowspan"] = 1
                i["name"] = res2[0]["name"]
                i["aff_date"] = res2[0]["aff_date"]
                i["income_id"] = res2[0]["income_id"]
                i["money"] = res2[0]["money"]
                if i["finished"] == 0:
                    res.insert(0,i)
                else:
                    res.append(i)
        else:
            for j in income_ids:
                sql_res2 = 'SELECT c.name,inc.aff_date,inc.income_id,inc.money FROM income inc INNER JOIN CLIENT c ON inc.`client_id` = c.id where inc.id = %s' % (j)
                try:
                    res2 = await Income.query(sql_res2)
                except:
                    raise ValueError("/apis/invoiceApply_index/index，二次查询错误")
                tmp = {}
                tmp["invid"] = i["invid"]
                tmp["info"] = i["info"]
                tmp["finished"] = i["finished"]
                tmp["finished_time"] = i["finished_time"]
                tmp["name"] = res2[0]["name"]
                tmp["aff_date"] = res2[0]["aff_date"]
                tmp["income_id"] = res2[0]["income_id"]
                tmp["money"] = res2[0]["money"]
                if  income_ids.index(j) == 0:
                    tmp["show"] = 1
                    tmp["rowspan"] = len(income_ids)
                    if tmp["finished"] == 0:
                        res.insert(0,tmp)
                    else:
                        res.append(tmp)
                else:
                    tmp["show"] = 0
                    if tmp["finished"] ==0:
                        res.insert(int(income_ids.index(j)),tmp)
                    else:
                        res.append(tmp)

#上面存在一个问题，如果不是用tmp变量，使用i来存储会出现问题。
    #                         #   income_id             在res1中的位置      几行           res1的内容
    #             # key = str(income_ids[j]) + "::" + str(res1.index(i) + j) + "::" + str(len(income_ids))
    #             d_for_insert = {str(income_ids[j]) + "::" + str(res1.index(i) + j) + "::" + str(len(income_ids)): i}
    # for k,v in d_for_insert.items():
    #     income_id,pos,row = k.split("::")
    #     content = v

    #         sql_res2 = 'SELECT c.name,inc.aff_date,inc.income_id,inc.money FROM income inc INNER JOIN CLIENT c ON inc.`client_id` = c.id where inc.id = %s' %(income_ids[j])
    #         try:
    #             res2 = await Income.query(sql_res2)
    #         except:
    #             raise ValueError("/apis/invoiceApply_index/index，二次查询错误")
    #         res1[i + j]["name"] = res2[0]["name"]
    #         res1[i + j]["aff_date"] = res2[0]["aff_date"]
    #         res1[i + j]["income_id"] = res2[0]["income_id"]
    #         res1[i + j]["money"] = res2[0]["money"]
    #         res1[i + j]["show"] = 1
    #         res1[i + j]["rowspan"] = 1
    #
    #由于列表不能边操作，边删除,下面的代码可能有错误
    # for j in range(len(res)):
    #     if res[j]["finished"] == 1:
    #         t = res[j]
    #         res.pop(j)
    #         res.append(t)
    return {
        'total':total,
        'page':p,
        'list':res
    }

#inv.id
@get('/apis/finish')
async def apis_finish(*,id):
    if not id.isdigit() or int(id) <= 0:
        return {
            'msg': '确认失败,缺少请求参数'
        }
    where = "id = %s" %(id)
    try:
        invoices = await Invoice.findAll(where)
    except:
        raise ValueError("/apis/finish，sql错误")
    invoices = obj2str(invoices)
    if len(invoices) == 1:
        income_ids = invoices[0]["income_id"].split(",")
        for i in income_ids:
            wherei = " id = %s " %(i)
            try:
                incomes = await Income.findAll(where=wherei)
                incomes = obj2str(incomes)
                if incomes[0]["status"] != 0:
                    return  returnData(0,"此收入状态有误")
                incomes[0]["status"] = 1
                r_status = await Income(**incomes[0]).update()
            except:
                raise ValueError("/apis/finish，sql错误")
            if r_status != 1:
                return returnData(0,"发票完成错误，/apis/finish")
        invoices[0]["finished"] = 1
        invoices[0]["finished_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            rs = await Invoice(**invoices[0]).update()
        except:
            raise ValueError("/apis/finish，sql错误")
        if rs == 1:
            return returnData(1,"完成")
    else:
        return returnData(0,"完成")


