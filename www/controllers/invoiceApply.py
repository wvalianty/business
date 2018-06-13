from core.coreweb import get, post
from lib.models import Income, Client,Invoice
import math,datetime,time
from lib.common import obj2str,returnData,exportExcel

async def export(lists):
    """导出execl表格
    """
    fields = {
        'income_id':"收入ID",
        'name': '公司名称',
        'aff_date': '归属时间',
        'money': '开票金额',
        'info': '开票信息',
        'income_company': '开票公司',
        'comments': '备注',
       'finished':"是否已开票"
    }
    return exportExcel('发票申请表', fields, lists)


#keyword 用处
@get('/apis/invoiceApply_index/index')
async def invoiceApply_index(*, keyword=None,rangeDate=None,isExport=None,isSearch=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)

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
    sql_res1 = 'select inv.income_id income_id_ids,inv.id invid,inv.info,inv.finished,inv.finished_time,inv.comments from invoice  inv where is_delete = 0  order by inv.id desc limit %s,%s '  %(limit[0],limit[1])
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
                sql_res2 = 'SELECT c.name,inc.aff_date,inc.income_id,inc.money,inc.income_company FROM income inc INNER JOIN `client` c ON inc.`client_id` = c.id where inc.id = %s' %(income_ids[0])
                try:
                    res2 = await  Income.query(sql_res2)
                except:
                    raise ValueError("/apis/invoiceApply_index/index，二次查询错误")
                if i["comments"]:
                    i["comments"] = i["comments"].replace('\n', '<br/>')
                i["show"] = 1
                i["rowspan"] = 1
                i["name"] = res2[0]["name"]
                i["aff_date"] = res2[0]["aff_date"]
                i["income_id"] = res2[0]["income_id"]
                i["money"] = res2[0]["money"]
                i["income_company"] = res2[0]["income_company"]
                if i["finished"] == 0:
                    res.insert(0,i)
                else:
                    res.append(i)
        else:
            for j in income_ids:
                sql_res2 = 'SELECT c.name,inc.aff_date,inc.income_id,inc.money,inc.income_company FROM income inc INNER JOIN `client` c ON inc.`client_id` = c.id where inc.id = %s' % (j)
                try:
                    res2 = await Income.query(sql_res2)
                except:
                    raise ValueError("/apis/invoiceApply_index/index，二次查询错误")
                tmp = {}
                tmp["invid"] = i["invid"]
                tmp["info"] = i["info"]
                tmp["finished"] = i["finished"]
                tmp["finished_time"] = i["finished_time"]
                if i["comments"]:
                    tmp["comments"] = i["comments"].replace('\n', '<br/>')
                tmp["name"] = res2[0]["name"]
                tmp["aff_date"] = res2[0]["aff_date"]
                tmp["income_id"] = res2[0]["income_id"]
                tmp["money"] = res2[0]["money"]
                tmp["income_company"] = res2[0]["income_company"]
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

    if keyword  and isSearch:
        search_res = []
        search_total = 0
        cname = keyword.strip()
        for sear in res:
            if sear["name"] == cname:
                search_res.append(sear)
        search_total = len(search_res)
        p = (math.ceil(search_total / pageSize), page)
        if isExport == 1:
            for item in search_res:
                if item["finished"] == 0:
                    item["finished"] = "否"
                if item["finished"] == 1:
                    item["finished"] = "是"
            return await export(res)

        return {
            'total': search_total,
            'page': p,
            'list': search_res
        }
    if rangeDate or (keyword and isSearch):
        search_res = []
        search_total = 0
        start_date = rangeDate.split(" - ")[0]
        start_date = time.strptime(start_date,'%Y-%m')
        end_date = rangeDate.split(" - ")[1]
        end_date = time.strptime(end_date,'%Y-%m')
        for search_date in res:
            if time.strptime(search_date["aff_date"],'%Y-%m') >= start_date and time.strptime(search_date["aff_date"],'%Y-%m') <= end_date:
                search_res.append(search_date)
        search_total = len(search_res)
        p = (math.ceil(search_total / pageSize), page)
        if isExport == 1:
            for item in search_res:
                if item["finished"] == 0:
                    item["finished"] = "否"
                if item["finished"] == 1:
                    item["finished"] = "是"
            return await export(res)
        return {
            'total': search_total,
            'page': p,
            'list': search_res
        }

    if isExport:
        for item in res:
            if item["finished"] == 0:
                item["finished"] = "否"
            if item["finished"] == 1:
                item["finished"] = "是"
        return await export(res)

    return {
        'total':total,
        'page':p,
        'list':res
    }


@post("/apis/invoice_finish/form")
async def apis_finish(*,id,finished,finished_time):
    row_income = {}
    if id and finished_time and  finished and int(finished) == 1:
        invoice = await Invoice.find(int(id))
        invoice["finished"] = 1
        invoice["finished_time"] = finished_time
        rows_f = await Invoice(**invoice).update()
        if rows_f == 1:
            income_ids = invoice["income_id"]
            for inc in income_ids.split(","):
                income = await Income.find(int(inc))
                income["inv_status"] = 2
                rows = await Income(**income).update()
                row_income[inc] = rows
            for k,v in row_income.items():
                if v != 1:
                    return returnData(0,"开票")
        else:
            return returnData(0, "开票")
        return returnData(1,"开票")
    else:
        return returnData(0,"确定不开票或没有发票")

@get("/apis/invoice_finish/info")
async  def invoice_finish(*,id):
    id = int(id)
    invoice = await Invoice.find(id)
    #存在问题存在数据库里面的时间为什么是下面这个格式的
    # isinstance(item[field], datetime.date):
    # item[field] = item[field].strftime("%Y-%m-%d")
    res = dict(
        id = invoice["id"],
        finished = invoice["finished"],
        # finished_time = invoice["finished_time"].strftime("%Y-%m-%d")
    )
    return {
        "info": res
    }


@get("/apis/invoiceApply_comment/info")
async  def invoiceApply_comment(*,id):
    id = int(id)
    where = " id = %s " %(id)
    re_sql = await Invoice.findOne(where=where)
    res = {}
    res["comments"] = re_sql["comments"]
    res["id"] = re_sql["id"]
    return {
        "info":res
    }

@post("/apis/invoiceApply_comment/form")
async def invoiceApply_comment_form(*,id,comments):
    id = int(id)
    invoice = await Invoice.find(id)
    invoice["comments"] = comments.strip()
    rows = await Invoice(**invoice).update()
    if rows == 1:
        return returnData(1,"备注")
    else:
        return returnData(0,"备注")

