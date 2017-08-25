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

    custom_path = __real_path('custom') if path == 'system' else None
    path = __real_path(path)

    if use_cache and __CONFIG.has_key(path):
        config =  __CONFIG[path]
    else:
        config = __load_json(path)
        custom_config = __load_json(custom_path)

        config = __merge(config, custom_config)

        __CONFIG[path] = config

    if key:
        return config[key] if config.has_key(key) else {}
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


def __load_json(path):
    if not path or not os.path.exists(path):
        return {}

    cfg_f = open(path, 'r')
    str = cfg_f.read().replace('\\', '/').replace('\'', '"').strip()
    cfg_f.close()

    if not str:
        str = '{}'
    str = re.compile('^\s*(("[^"]*?"[^"]*?)*)//.*$', re.M).sub(r'\1', str)

    try:
        return json.loads(str)
    except Exception:
        raise Exception('json file load error,pls check your json file:%s' % path)


def __merge(dict1, dict2):
    if not dict2:
        return dict1

    for key, val in dict2.items():
        if key not in dict1 or not isinstance(val, dict):
            dict1[key] = val
        else:
            dict1[key] = __merge(dict1[key], dict2[key])

    return dict1