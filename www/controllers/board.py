from core.coreweb import get, post
from lib.models import Income,Client
import math,datetime,time
from lib.common import obj2str,exportExcel

# 结算状态
statusMap = (
    '待开票',
    '未回款',
    '已回款'
)

@get('/apis/board/index')
async def board_index(*,isExport=None,keyword=None, month=None, status=None, page=1, pageSize=10):
    page = int(page)
    pageSize = int(pageSize)
    year = time.strftime('%Y')

    where = "where 1=1"
    numOrstr = None

    if keyword:
        where = "{} and inc.income_id like '%%{}%%' or c.name like '%%{}%%'".format(where, keyword, keyword)

    if status and status.isdigit():
        where = "{} and status = {}".format(where, status)
    if month and month.isdigit():
        month = month.zfill(2)
    else:
        lastDate = await Income.findNumber('aff_date', orderBy='aff_date desc')
        month = lastDate.split('-')[1] if lastDate else time.strftime('%m')

    where = "{} and aff_date like '%%{}-{}%%'".format(where, year, month)

    limit = "%s,%s" % ((page - 1) * pageSize, pageSize)
    sql_total = 'select count(*) cc from income inc inner join client c on inc.client_id = c.id %s' %(where)
    print(sql_total)
    re = await Income.query(sql_total)
    total = re[0]["cc"]
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total = total, page = (0,0), list = ())
    sql_re = 'select inc.income_id,c.name,inc.name cname,inc.aff_date,inc.money,inc.status,inc.media_type from income inc inner join client c on inc.client_id = c.id ' + where + 'order by inc.income_id desc limit %s' %(limit)
    print(sql_re)
    res = await Income.query(sql_re)
    res = obj2str(res)
    print(res)
    return {
        'total':total,
        'page':p,
        'list':res,
        'other':{
            'statusMap': statusMap,
        }
    }