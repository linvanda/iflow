# coding:utf-8

import json
import re


def real_path(path):
    path = path.replace('\\', '/')

    if path.find('/') == -1:
        path = 'config/' + path

    if path.find('.json') == -1:
        path += '.json'

    return path


def read_config(path):
    if not path:
        return {}

    path = real_path(path)

    cfg_f = open(path, 'r')
    str = cfg_f.read().replace('\\', '/').replace('\'', '"').strip()
    cfg_f.close()

    if not str:
        str = '{}'
    str = re.compile('//[^"]*$', re.M).sub('', str)

    return json.loads(str)


def write_config(path, json_str):
    if not path:
        return False

    if not isinstance(json_str, str):
        json_str = json.dumps(json_str)

    path = real_path(path)

    cfg_f = open(path, 'w')
    cfg_f.write(json_str)
    cfg_f.close()

    return True
