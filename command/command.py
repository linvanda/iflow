# coding:utf-8

import abc
import iconfig


class Command(object):
    """
    指令基类
    """
    def __init__(self, cmd, args):
        self.cmd = cmd
        self.args = args

    @abc.abstractmethod
    def execute(self):
        raise Exception(u"指令尚未实现")

    @staticmethod
    def real_cmd(cmd):
        alias = iconfig.read_config('system', 'cmd')
        return alias[cmd] if alias.has_key(cmd) else None

    def __str__(self):
        return self.cmd + ' ' + ' '.join(self.args)
