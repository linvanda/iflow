# coding:utf-8

import abc
import iconfig
import ihelper
import iprint


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

    @staticmethod
    def exec_hook(flag, position, proj=None, branch=None):
        """
        执行钩子指令
        :param flag:  标识，如product
        :param position: 位置，如post（主指令后）,pre(主指令前)
        :param proj:  所在的项目
        :param branch: 所在的分支
        :return: None
        """
        hook_cfg = iconfig.read_config('system', "hook")

        if not hook_cfg or not hook_cfg.has_key(flag) or not isinstance(hook_cfg[flag], dict):
            return None

        hook_cfg = hook_cfg[flag]

        if not hook_cfg.has_key(position) or not isinstance(hook_cfg[position], list) or not hook_cfg[position]:
            return None

        for cfg in hook_cfg[position]:
            if not cfg or not isinstance(cfg, dict) or not cfg.has_key('cmd'):
                continue

            # 项目限制
            if proj and cfg.has_key("proj") \
                    and isinstance(cfg["proj"], list) \
                    and cfg["proj"] \
                    and proj not in cfg["proj"]:
                continue

            # 分支限制
            if branch and cfg.has_key("branch") \
                    and isinstance(cfg["branch"], list) \
                    and cfg["branch"] \
                    and branch not in cfg["branch"]:
                continue

            # 执行钩子
            if cfg.has_key("desc") and cfg["desc"]:
                iprint.ok(u"执行 %s..." % cfg["desc"])
            ihelper.execute(cfg["cmd"])

    def __str__(self):
        return self.cmd + ' ' + ' '.join(self.args)
