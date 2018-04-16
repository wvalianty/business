from core.coreweb import get, post
from lib.common import obj2str
from lib.models import Syslog,Client,Income,Settlement,Business,curr_datetime,next_id
import hashlib,asyncio,json,time
from aiohttp import web
#import datetime

COOKIE_NAME = 'awesession'
_COOKIE_KEY = 'business'

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [str(user.id), expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

@post("/api/login")
async def login(*,account,passwd):
    where = "username = '%s'" %(account)
    accounts = await Syslog.findAll(where=where)
    inaccount = str(accounts[0]["username"])
    inpasswd = accounts[0]["passwd"]
    if passwd == inpasswd:
        ac = accounts[0]
        r = web.Response()
        r.set_cookie(COOKIE_NAME, user2cookie(ac, 86400), max_age=86400, httponly=True)
        r.content_type = 'application/json'
        redata = {"msg": "success", "status": 1}
        r.body = json.dumps(redata, ensure_ascii=False).encode('utf-8')
        return r
        # redata = {"msg": "success", "status": 1}
    else:
        redata = {"msg":"fail","status":0}



    # if user.passwd != sha1.hexdigest():
    #     raise ValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    # r = web.Response()
    # r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    # user.passwd = '******'
    # r.content_type = 'application/json'
    # r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    # return r

#
#
#     print(account)
#     print(passwd)
#     redata = { "msg": "success","status":1}
#     return redata
#
# COOKIE_NAME = 'awesession'
# _COOKIE_KEY = configs.session.secret
#
#
#
#     @post('/api/authenticate')
#     def authenticate(*, email, passwd):
#         if not email:
#             raise APIValueError('email', 'Invalid email.')
#         if not passwd:
#             raise APIValueError('passwd', 'Invalid password.')
#         users = yield from User.findAll('email=?', [email])
#         if len(users) == 0:
#             raise APIValueError('email', 'Email not exist.')
#         user = users[0]
#         # check passwd:
#         sha1 = hashlib.sha1()
#         sha1.update(user.id.encode('utf-8'))
#         sha1.update(b':')
#         sha1.update(passwd.encode('utf-8'))
#         if user.passwd != sha1.hexdigest():
#             raise APIValueError('passwd', 'Invalid password.')
#         # authenticate ok, set cookie:
#         r = web.Response()
#         r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
#         user.passwd = '******'
#         r.content_type = 'application/json'
#         r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
#         return r
#
#     @get('/signout')
#     def signout(request):
#         referer = request.headers.get('Referer')
#         r = web.HTTPFound(referer or '/')
#         r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
#         logging.info('user signed out.')
#         return r
#
#     _RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
#     _RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')