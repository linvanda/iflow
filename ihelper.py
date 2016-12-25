# coding:utf-8
# 该模块提供一些助手方法

import time
import datetime
import os
import re
import iconfig
from iprint import *


def goodbye(*args):
    print args[0] if args and args[0] else "good bye!"
    time.sleep(1)
    sys.exit(0)


def error_exit(msg):
    error(msg)
    raw_input()
    sys.exit(1)


def check_sprint_format(sprint):
    return re.compile('[0-9]{4}s[12]').match(sprint)


def format_sprint(sprint):
    if len(sprint) == 4:
        sprint = time.strftime('%Y')[2:] + sprint
    return sprint


def get_date_from_sprint(sprint):
    sprint = format_sprint(sprint)

    year = sprint[:2]
    month = sprint[2:4]

    return '20' + year + '-' + month + '-01'


def init_check():
    """
    入口初始化检查
    """
    # 检查project.json有没有配置以及路径是否正确
    proj_cfg = iconfig.read_config('project')
    if not proj_cfg:
        raise Exception(u'请配置项目信息(dist/config/project.json文件，具体格式参见readme.md文件)')

    for proj_name, info in proj_cfg.items():
        if not info['dir'] or not os.path.exists(info['dir']) or not os.path.isdir(info['dir']):
            raise Exception(u'项目' + proj_name + u'的目录配置不正确')

    return True


def check_sprint():
    try:
        runtime = iconfig.read_config('runtime')
    except IOError:
        iconfig.write_config('runtime', {})
        runtime = iconfig.read_config('runtime')

    if not runtime.has_key('sprint'):
        raise Exception(u'尚未设置迭代版本号，请使用sp指令设置正确的迭代版本号')
    else:
        sp_date = get_date_from_sprint(runtime['sprint']).split('-')
        now = time.strftime('%Y-%m-' + '01').split('-')
        d1 = datetime.datetime(int(sp_date[0]), int(sp_date[1]), int(sp_date[2]))
        d2 = datetime.datetime(int(now[0]), int(now[1]), int(now[2]))
        diff = abs((d1 - d2).days)

        if diff >= 60:
            raise Exception(u'迭代版本号(' + runtime['sprint'] + ')过旧，请使用sp指令重新设置正确的迭代版本号')

    return True



