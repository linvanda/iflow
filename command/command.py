# coding:utf-8

import abc
import iconfig
import ihelper


class Command(object):
    """
    指令基类
    """
    def __init__(self, cmd, args, log=True):
        self.cmd = cmd
        self.args = args
        log and ihelper.log(cmd + ' ' + ' '.join(self.args))

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

    def __str__(self):
        return self.cmd + ' ' + ' '.join(self.args)
