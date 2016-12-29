# coding:utf-8

import sys
import abc
import iconfig
import ihelper
import isprint


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

    def real_branch(self, branch, prefix=None):
        """
        获取完整的分支名
        :param str prefix:
        :param str branch:
        :return: str
        """
        if not branch:
            return None

        prefix = prefix or self.cmd

        if branch.find(':') != -1:
            branch = branch.split(':')[1]

        original_branch = branch
        branch = filter(lambda x:x != '', branch.split('/'))
        config = iconfig.read_config('system', 'branch')

        if len(branch) > 2 and branch[0] != config['feature_prefix']:
            raise Exception('分支名称不合法')

        if len(branch) == 3:
            branch[1] = isprint.get_sprint(branch[1])
            if not branch[1]:
                raise Exception('分支名称不合法')
            return '/'.join(branch)

        if len(branch) == 2:
            if isprint.check_sprint_format(branch[0], True):
                # 迭代号开始的,此时prefix只能是feature
                if prefix != config['feature_prefix']:
                    raise Exception('分支名称不合法')

                branch[0] = isprint.get_sprint(branch[0])
                branch.insert(0, config[prefix + '_prefix'])
            else:
                # 看是否以feature或hotfix开头
                if branch[0] != config['feature_prefix'] and branch[0] != config['hotfix_prefix']:
                    raise Exception('分支格式不合法')

            return '/'.join(branch)

        if original_branch.find('/') == 0:
            return config[prefix + '_prefix'] + original_branch
        else:
            return config[prefix + '_prefix'] + ('/' + ihelper.read_runtime('sprint') if prefix == 'feature' else '') + '/' + branch[0]

    def __str__(self):
        return self.cmd + ' ' + ' '.join(self.args)
