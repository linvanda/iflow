# coding:utf-8

import json
import re
import os
import iglobal

__CONFIG = {}


def __real_path(path):
    path = path.replace('\\', '/')

    if path.find('/') == -1:
        path = iglobal.BASE_DIR + '/config/' + path

    if path.find('.json') == -1:
        path += '.json'

    return path


def read_config(path, key=None, use_cache=True):
    global __CONFIG

    if not path:
        return {}

    path = __real_path(path)

    config = {}
    if use_cache and __CONFIG.has_key(path):
        config =  __CONFIG[path]
    else:
        if not os.path.exists(path):
            return {}
        else:
            cfg_f = open(path, 'r')
            str = cfg_f.read().replace('\\', '/').replace('\'', '"').strip()
            cfg_f.close()

            if not str:
                str = '{}'
            str = re.compile('//.*$', re.M).sub('', str)
            config = __CONFIG[path] = json.loads(str)

    if key:
        return config[key] if config.has_key(key) else None
    else:
        return config


def write_config(path, json_str):
    global __CONFIG

    if not path:
        return False

    if not isinstance(json_str, str):
        json_str = json.dumps(json_str)

    path = __real_path(path)

    cfg_f = open(path, 'w')
    cfg_f.write(json_str)
    cfg_f.close()

    __CONFIG[path] =  json.loads(json_str)

    return True
