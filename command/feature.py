# coding:utf-8

from command import Command


class Feature(Command):
    """
    特性分支指令类
    """
    def execute(self):
        if not len(self.args):
            raise Exception(u'无效参数')

        if not Command.real_cmd(self.args[0]):
            self.args.insert(0, 'c')


