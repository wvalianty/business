from core.coreweb import get, post

from lib.common import obj2str,returnData,user2cookie,cookie2user
from lib.models import Syslogs,Client,Income,Settlement,Business,curr_datetime,next_id,Users
import hashlib,asyncio,json,time,re,logging,datetime,math
import hashlib,asyncio,json,time,re,logging

from aiohttp import web

from config import configs
COOKIE_NAME = configs.cookie.name
_COOKIE_KEY = configs.session.secret

# @get('/signout')
# def signout(request):
#     referer = request.headers.get('Referer')
#     r = web.HTTPFound(referer or '/')
#     r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
#     logging.info('user signed out.')
#     return r

# _RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
# _RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')



@post("/api/login")
async  def login(*,account,passwd):
    email = account
    passwd = passwd.strip()
    if not email:
        return returnData(0, "认证")
    if not passwd:
        return returnData(0, "认证")
    whereu = "email = '%s'" % (email)
    try:
        users = await Users.findAll(where=whereu)
    except:
        return returnData(0, "认证")
    users = obj2str(users)
    if len(users) == 1:
        user = users[0]
        if user.passwd == passwd:
            r = web.Response()
            r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
            user.passwd = "******"
            user.msg = "登陆成功"
            user.status = 1
            r.content_type = 'application/json'
            r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
            return r
        else:
            return returnData(0, "认证")
    else:
        return returnData(0, "认证")


#后续在处理，目前密码正确 返回成功

#role处理，下拉选择框
@post("/apis/manager/form")
async  def useradd(*,phone=None,email=None,passwd=None,role=None,name=None,id=None):
    # if not phone or not email or not passwd or not name:
    #     return returnData(0,"缺少请求参数，")

    if id :
        user = dict(
            id = int(id),
            phone=phone.strip(),
            email=email.strip(),
            passwd=passwd.strip(),
            role=role,
            created_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            name=name.strip(),
        )
        try:
            rows = await  Users(**user).update()
        except:
            return returnData(0, "管理or用户员编辑")
        if rows == 1:
            return returnData(1, "管理or用户员编辑")
        else:
            return returnData(0, "添加")
    else:
        user = dict(
            phone = phone.strip(),
            email = email.strip(),
            passwd = passwd.strip(),
            role = int(role),
            created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            name = name.strip(),

        )
        rows = await  Users(**user).save()

        if rows == 1 :
            return returnData(1,"管理or用户员添加，")
        else:
            return returnData(0,"添加")

@get("/apis/manager/info")
async def managerInfo(*,id):
    if id :
        where = " id = %s " %(id)
        users = await Users.findAll(where=where)
        users = obj2str(users)
        if len(users) != 1:
            return returnData(0,"编辑");

        return {
            "info":users[0]
        }

@get("/apis/manager/index")
async  def lookAll(*,page=1,pageSize=30):
    page = int(page)
    pageSize = int(pageSize)
    where = '1 = 1'

    total = await Users.findNumber('count(id)', where)
    p = (math.ceil(total / pageSize), page)
    if total == 0:
        return dict(total=total, page=p, list=())
    users = await Users.findAll(orderBy='id desc', where=where, limit=pageSize)


    users = obj2str(users)

    for item in users:
        item["passwd"] = "******"
        if item["role"] == 0:
            item["role"] = "管理员"
        elif item["role"] == 1:
            item["role"] = "运营侧"
        elif item["role"] == 2:
            item["role"] = "财务侧"
        else:
            item["role"] = "角色错误"
    return {
        'total': total,
        'page': p,
        'list': users
    }




@get('/apis/manager/del')
async def delete(*, id):
    if not id.isdigit() or int(id) <= 0:
        return returnData(0, '删除', '缺少请求参数')

    try:
        rows = await Users.delete(id)
        msg = None
    except Exception as e:
        rows = 0
        msg = "删除失败"

    return returnData(rows, '删除', msg)