#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging, asyncio, aiomysql

'''
res = await conroutin or res = yield from coroutine
1. yield 作用于一个生成器
2. coroutine的实现是基于生成器的，在操作协程时， yield from = await

'''

def log(sql, args = ()):
    """记录sql语句
    """

    logging.info('SQL:%s' % sql)

async def create_pool(loop, **kw):
    """数据库连接池
    
    Arguments:
        loop {[type]} -- [description]
        **kw {[type]} -- [description]
    """

    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        user = kw.get('user', 'root'),
        password=kw.get('password', 'root'),
        db = kw['db'],
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize', 10),
        minsize = kw.get('minsize', 1),
        loop = loop
    )

async def select(sql, args, size = None):
    """数据查询
    """
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
           
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
        return rs


async def execute(sql, args, autocommit = True):
    """数据修改
    """
    log(sql, args)
    # 从连接池里获取一个数据库链接
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            # 获得操作数据库的游标对象
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args or ())
                affetced = cur.rowcount
                if not autocommit:
                    await cur.commit()
        except BaseException as e:
            if not autocommit:
                await cur.commit
            raise
        return affetced  # 返回受影响的行数


def create_args_string(num):
    """创建参数占位符
    
    Arguments:
        num {[type]} -- [占位符的个数]
    """
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)


class Field(object):
    """数据表字段基类
    """


    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
    """字符串类
    """

    def __init__(slef, name=None, primary_key=False, default=None, ddl="varchar(50)"):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):
    """布尔类
    """
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):
    """整数类
    """
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'int', primary_key, default)

class FloatField(Field):
    def __init__(self, name=None, default=0.0):
        super().__init__(name, 'real', False, default)

class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

class ModelMetaClass(type):
    """这是一个元类，用来创建类的类， 闯将model的子类时，自动增加以下参数信息到类中
    """
    def __new__(cls, name, bases, attrs):
        """创建类时自动调用，相当于是new关键字的操作
            第一个参数cls，相当于是类函数中的self
        
        Arguments:
            name {[type]} -- [类名]
            bases {[type]} -- [继承类]
            attrs {[type]} -- [属性]
        
        Raises:
            RuntimeError -- [description]
            StandardError -- [description]
        
        Returns:
            [type] -- [返回一个类]
        """

        # 排除model类本身
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        
        # 获得table名称
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        # 获取所有Field的主键名
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise StandardError('Primary key not found')    

        for k in mappings.keys():
            attrs.pop(k)

        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__fields__'] = fields # 除主键外所有的属性名
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s`(`%s`, %s) values(%s)' % (
            tableName, primaryKey, ', '.join(escaped_fields), create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s` = ?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(r"Model object has no attribute %s" % key)
    
    def __setattr__(self, key, val):
        self[key] = val

    def getValue(self, key):
        return getattr(self, key, None)
    
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s:%s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        '查询所有值'
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        'find number by select and where'
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']
    
    @classmethod
    async def find(cls, pk=None):
        'find object by primary key'
        rs = await select('%s where `%s` = ?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])
    
    @classmethod
    async def findOne(cls, selectField="*", where=None, args=None):
        'find one by select and where'
        sql = ['select %s from `%s`' % (selectField, cls.__table__) ]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.insert(0,self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record:affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows：%s' % rows)
        
    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)

        if rows != 1:
            logging.warn('failed to remove by primary key : affected rows: %s' % rows)
