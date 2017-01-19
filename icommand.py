# coding:utf-8

import command
import iconfig


def real_cmd(cmd, raise_err=True, valid=True, top_cmd=None):
    """
    valid=True时，如果不指定top_cmd，则认为cmd是一级指令，否则认为是top_cmd的二级指令
    :param str top_cmd:
    :param cmd:
    :param raise_err:
    :param valid:
    :return:
    """
    config = iconfig.read_config('system')
    alias = config['alias']
    cmd = alias[cmd] if alias.has_key(cmd) else cmd

    if valid:
        error = False
        if top_cmd:
            top_cmd = alias[top_cmd] if top_cmd in alias else top_cmd
            cls = config['cmd_cls'][top_cmd] if top_cmd in config['cmd_cls'] else None

            if not cls:
                error = True
            else:
                if cmd not in dir(eval('command.%s' % cls)):
                    error = True
        elif not config['cmd_cls'].has_key(cmd):
            error = True

        if error:
            if raise_err:
                raise Exception(u'无效指令')
            else:
                return None

    return cmd


def top_cmd_list():
    """
    获取所有的一级指令列表
    返回：字典：指令->别名列表
    :return:
    """
    cmds = iconfig.read_config('system', 'cmd_cls').keys()
    alias = iconfig.read_config('system', 'alias')
    lst = {}
    for cmd in cmds:
        if cmd not in lst:
            lst[cmd] = []
        for al, c in alias.items():
            if cmd == c:
                lst[cmd].append(al)

    return lst