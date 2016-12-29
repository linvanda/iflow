# coding:utf-8

import os
from command import Command
import exception
import ihelper


class Git(Command):
    """
    git相关指令
    """
    def execute(self):
        try:
            eval('self.' + self.cmd)()
        except exception.FlowException, e:
            raise Exception(unicode(str(e), 'utf-8'))
        except Exception, e:
            raise Exception(e.message)

    def rename(self):
        """
        分支重命名
        """
        if len(self.args) < 2:
            raise exception.FlowException('指令格式错误')

        old = self.args[0]
        new = self.args[1]

        # 重命名本地分支
        ihelper.execute('git branch -m ' + old + ' ' + new, raise_err=True)
        # 删除远程分支(如果有的话)
        ihelper.execute('git push --delete origin ' + old)
        # 上传新分支到远程
        ihelper.execute('git push -u origin ' + new + ':' + new)

    def git(self):
        """
        git原生指令
        """
        os.system('git ' + (' '.join(self.args) if self.args else ''))