from core.coreweb import get, post
<<<<<<< HEAD
from lib.common import obj2str,returnData,user2cookie,cookie2user
from lib.models import Syslog,Client,Income,Settlement,Business,curr_datetime,next_id,Users
import hashlib,asyncio,json,time,re,logging,datetime,math
=======
from lib.common import obj2str
from lib.models import Syslogs,Client,Income,Settlement,Business,curr_datetime,next_id,Users
import hashlib,asyncio,json,time,re,logging
>>>>>>> 87514535d1e44cb26540d1a0e9aca698f4b5bc63
from aiohttp import web

COOKIE_NAME = 'business'
_COOKIE_KEY = 'business'


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
    if not email:
        raise ValueError('email', 'Invalid email.')
    if not passwd:
        raise ValueError('passwd', 'Invalid password.')
    whereu = "email = '%s'" % (email)
    users = await Users.findAll(where=whereu)
    users = obj2str(users)
    if len(users) != 1:
        logging.info("no such user or more than one")
        return returnData(0, "密码错误，")
    user = users[0]
    if user.passwd != passwd:
        return returnData(0,"密码错误，")
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = "******"
    user.msg = "登陆成功"
    user.status = 1
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    print(r)
    return r

#后续在处理，目前密码正确 返回成功

#role处理，下拉选择框
@post("/apis/manager/form")
async  def useradd(*,phone=None,email=None,passwd=None,role=None,name=None,id=None):
    # if not phone or not email or not passwd or not name:
    #     return returnData(0,"缺少请求参数，")
    if id :
        where = " id = %s " %(id)
        users = await  Users.findAll(where = where)
        if not users:
            return returnData(0, "编辑")
        user = dict(
            id = int(id),
            phone=phone.strip(),
            email=email.strip(),
            passwd=passwd.strip(),
            role=role,
            created_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            name=name.strip(),
        )
        rows = await  Users(**user).update()
        if rows == 1:
            return returnData(1, "管理or用户员编辑，")
        else:
            return returnData(0, "添加")
    else:

        user = dict(
            phone = phone.strip(),
            email = email.strip(),
            passwd = passwd.strip(),
            role = role,
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


# @post("/api/manager/del")
# async  def userdel(*,email=None):
#     # if not phone or not email or not passwd or not name:
#     #     return returnData(0,"缺少请求参数，")
#     if not email:
#         return returnData(0, '删除', '缺少请求参数')
#     email = str(email)
#     where = "email = '%s' " %(email)
#     user = await  Users.findAll(where=where)
#     id = user[0]["id"]
#     try:
#         rows = await Users.delete(id)
#         if rows == 1:
#             return  returnData(1,"删除，")
#         else:
#             return returnData(0, "删除，")
#     except Exception as e:
#         return returnData(0, "请求错误")
#修改,邮箱不能修改，想修改邮箱只能新建
# @post("/api/manager/modify")
# async  def usermodify(*,phone=None,email=None,passwd=None,role=None,name=None,admin=None):
#     admin = int(admin)
#     email = str(email)
#     where = "email = '%s' " % (email)
#     user = await  Users.findAll(where=where)
#     user_modify = dict(
#             id=10,
#             phone=phone.strip(),
#             email=email.strip(),
#             passwd=passwd.strip(),
#             role=role,
#             created_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             name=name.strip(),
#             admin=admin
#         )
#     user[0] = user_modify
#     print(user[0])
#     rows = await  Users(**user[0]).update()
#     if rows == 1 and admin == 1:
#         return returnData(1, "管理员信息修改，")
#     elif rows == 1 and admin == 0:
#         return returnData(1, "用户信息修改，")
#     else:
#         return returnData(0, "修改")

# @get("/api/manager/look")
# async def user_look(*,email):
#     if email:
#         email = str(email.strip())
#         where = "email = '%s' " % (email)
#         print(where)
#         user = await  Users.findAll(where=where)
#         user = obj2str(user)
#         return {
#             "list" : user
#         }

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