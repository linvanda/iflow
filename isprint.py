# coding:utf-8
# 迭代模块

import re
import time
import datetime
import iconfig
import ihelper
import iglobal


def check_sprint_format(sprint, loose=False):
    """
    迭代号格式检验
    :param Bool loose:
    """
    return re.compile(iconfig.read_config('system')['sprint_format' if not loose else "sprint_format_loose"]).match(sprint)


def format_sprint(sprint):
    if len(sprint) == 4:
        sprint = time.strftime('%Y')[2:] + sprint
    return sprint


def get_sprint(sprint=None):
    if not sprint:
        year = time.strftime('%y')
        month = time.strftime('%m')
        day = time.strftime('%d')
        s = 's1' if int(day) < 15 else 's2'

        sprint = year + month + s

    sprint = format_sprint(sprint)

    return None if not check_sprint_format(sprint) else sprint


def next_sprint():
    now_sp = iglobal.SPRINT
    if not now_sp:
        return None

    sp_list = [now_sp[:2], now_sp[2:4], now_sp[4:]]
    if sp_list[2][1] == '1':
        return '%s%s%s' % (sp_list[0], sp_list[1], 's2')

    if sp_list[1] == '12':
        sp_list[0] = str(int(sp_list[0]) + 1)
        sp_list[1] = 1
    else:
        sp_list[1] = int(sp_list[1]) + 1

    return '%s%02d%s' % (sp_list[0], int(sp_list[1]), sp_list[2])


def get_date_from_sprint(sprint):
    sprint = format_sprint(sprint)

    year = sprint[:2]
    month = sprint[2:4]

    return '20' + year + '-' + month + '-01'


def check_sprint():
    """
    迭代版本号检查
    """
    sprint = ihelper.read_runtime('sprint')

    if not sprint:
        raise Exception(u'尚未设置迭代版本号，请使用sp指令设置正确的迭代版本号')
    else:
        sp_date = get_date_from_sprint(sprint).split('-')
        now = time.strftime('%Y-%m-' + '01').split('-')
        d1 = datetime.datetime(int(sp_date[0]), int(sp_date[1]), int(sp_date[2]))
        d2 = datetime.datetime(int(now[0]), int(now[1]), int(now[2]))
        diff = abs((d1 - d2).days)

        if diff >= 90:
            raise Exception(u'迭代版本号(' + sprint + u')和当前日期不符，请使用sp指令重新设置正确的迭代版本号')

    return True