# coding:utf-8

import sys
from command import Command
import exception
import extra


class Feature(Command):
    """
    特性分支指令类
    """
    def __init__(self, cmd, args):
        Command.__init__(self, cmd, args)
        # 二级指令
        self.sub_cmd_list = ('create', 'test', 'publish', 'tag', 'show', 'delete')

    def execute(self):
        if not len(self.args):
            return extra.Extra('help', [self.cmd], log=False).execute()

        sub_cmd = Command.real_cmd(self.args.pop(0), valid=False)
        if sub_cmd not in self.sub_cmd_list:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        # 调用相应的二级指令处理方法
        eval('self.' + sub_cmd)()

    def create(self):
        """
        创建特性分支。一次只能创建一个，会推到远端，且切换到此分支
        :return:
        """
        if not self.args:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        # 目前固定是三个参数
        if len(self.args) != 3:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        branch = comment = None
        while self.args:
            arg = self.args.pop(0)
            if arg == '-m':
                comment = unicode(self.args.pop(0), 'utf-8')
            else:
                branch = arg

        print comment












