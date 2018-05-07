from core.coreweb import get, post
from lib.models import Income,Client
import math,datetime,time
from lib.common import obj2str,exportExcel,addAffDateWhere

# 结算状态
statusMap = (
    '待开票',
    '未回款',
    '已回款'
)

mediaTypeMap = (
    '自媒体',
    '外媒'
)

async def export(lists):
    """导出execl表格
    """
    fields = {
        'income_id': '收入ID',
        'name': '公司名称',
        'business_type': '业务类型',
        'cname': '业务名称',
        'aff_date': '归属时间',
        'money': '收入金额',
        'status': '结算进度',
        'media_type': '媒体类型',
        'cost':'渠道成本',
    }
    return exportExcel('收入报表', fields, lists)

@get('/apis/board/index')
async def board_index(*,isExport=None,keyword=None, month=None,year=None, status=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    # year = time.strftime('%Y')
    totalMoney = 0
    where = "where 1=1 and inc.is_delete = 0 and c.is_delete = 0 "
    numOrstr = None

    if keyword:
        where = "{}  and inc.income_id like '%%{}%%' or c.name like '%%{}%%'".format(where, keyword, keyword)

    if status and status.isdigit():
        where = "{} and status = {}  ".format(where, status)
    
    if month:
        if int(month) < 10:
            month = "0" + str(month)
    if month and year:
        where = "{} and aff_date = '{}-{}'" .format(where,year,month)
    if month:
        where = "{} and aff_date like '{}-{}'" .format(where, '%%', month)
    if year:
        where = "{} and aff_date like '{}-{}'".format(where, year, '%%')
    limit = "%s,%s" % ((page - 1) * pageSize, pageSize)
    sql_total = 'select count(*) cc from income inc inner join client c on inc.client_id = c.id %s' %(where)

    re = await Income.query(sql_total)
    total = re[0]["cc"]
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=(0,0), list=(), other={
            'totalMoney': round(totalMoney, 2)
        })

    sql_re = 'select inc.cost,inc.income_id,inc.business_type,c.name,inc.name cname,inc.aff_date,inc.money,inc.status,inc.media_type from income inc inner join client c on inc.client_id = c.id ' + where + 'order by  inc.income_id  desc limit %s' %(limit)
    res = await Income.query(sql_re)
    res = obj2str(res)
    for item in res:
        item['status'] = statusMap[item['status']]
        item['media_type'] = mediaTypeMap[item['media_type']]
        totalMoney = totalMoney + item['money']

    if isExport and int(isExport) == 1:
        return await export(res)

    return {
        'total':total,
        'page':p,
        'list':res,
        'other':{
            'statusMap': statusMap,
            'mediaTypeMap': mediaTypeMap,
            'totalMoney': round(totalMoney, 2)
        }
    }


