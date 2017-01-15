# coding:utf-8

import abc
import iconfig


class Command(object):
    """
    指令基类
    """
    sub_cmd_list = None

    def __init__(self, cmd, args):
        self.cmd = cmd
        self.args = args

    @abc.abstractmethod
    def execute(self):
        raise Exception(u"指令尚未实现")

    @staticmethod
    def real_cmd(cmd, raise_err=True, valid=True):
        """
        默认会检查是否一级指令
        :param cmd:
        :param raise_err:
        :param valid:
        :return:
        """
        config = iconfig.read_config('system')
        alias = config['alias']
        cmd = alias[cmd] if alias.has_key(cmd) else cmd

        if valid and not config['cmd_cls'].has_key(cmd):
            if raise_err:
                raise Exception(u'无效指令')
            else:
                return None

        return cmd

    @staticmethod
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

    def __str__(self):
        return self.cmd + ' ' + ' '.join(self.args)
