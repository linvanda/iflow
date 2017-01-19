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
                    if cmd not in dir(eval('%s.%s' % (cls.lower(), cls))):
                        error = True
            elif not config['cmd_cls'].has_key(cmd):
                error = True

            if error:
                if raise_err:
                    raise Exception(u'无效指令')
                else:
                    return None

        return cmd


    def __str__(self):
        return self.cmd + ' ' + ' '.join(self.args)
