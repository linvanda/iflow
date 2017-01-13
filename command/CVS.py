# coding:utf-8

"""
版本控制命令基类
"""

import abc
from command import Command
import igit
import exception


class CVS(Command):
    def __init__(self, cmd, args):
        # 检查当前目录是否git仓库
        if not igit.dir_is_repository():
            raise exception.FlowException(u'当前目录不是有效的Git仓库')

        Command.__init__(self, cmd, args)

    @abc.abstractmethod
    def execute(self):
        raise Exception(u"指令尚未实现")



