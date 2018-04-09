#! /usr/bin/env python3
# -*- coding:utf-8 -*-

'配置文件，读取合并用户配置文件和默认配置文件, 应用程序一般读取这个文件获得配置信息'

import config_default


class Dict(dict):
    '''
    Simple dict but support access x.y style
    '''

    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v
        
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(r"Dict object has no attribute %s" % key)
    
    def __setattr__(self, key, val):
        self[key] = val
    

def merge(defaults, override):
    """合并两个dict
    """

    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

def toDict(d):
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D


configs = config_default.configs

try:
    import config_override
    configs = merge(configs, config_override.configs)
except ImportError as e:
    pass

configs = toDict(configs)