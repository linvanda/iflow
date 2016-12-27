# coding:utf-8

import os
import isprint
import ihelper
import iconfig
import exception
from command import Command


class Extra(Command):
    def execute(self):
        try:
            eval('self.' + self.cmd)()
        except exception.FlowException, e:
            raise Exception(unicode(str(e), 'utf-8'))
        except Exception:
            raise Exception(u'无效的指令')

    def sprint(self):
        """
        切换到某个迭代
        """
        sprint = isprint.get_sprint(None if not self.args else self.args[0])
        if not sprint:
            raise exception.FlowException(u'版本号格式错误')

        ihelper.write_runtime('sprint', sprint)

    def cd(self):
        """
        进入项目目录
        """
        if not self.args:
            raise exception.FlowException(u'指令格式不正确，请键入help查看该指令使用方式')

        proj_name = self.args[0]
        proj = iconfig.read_config('project', proj_name)

        if not proj or not proj.has_key('dir'):
            raise exception.FlowException(u'未配置项目' + proj_name + u'信息，请进入config/project.json中正确配置')

        if not os.path.isdir(proj['dir']):
            raise exception.FlowException(u'该项目git根目录配置不正确，请进入config/project.json中正确配置')

        ihelper.write_runtime('project', proj_name)
        os.chdir(proj['dir'])

    def rename(self):
        """
        分支重命名
        """
        if len(self.args) < 2:
            raise exception.FlowException('指令格式错误')

        old = self.args[0]
        new = self.args[1]

        # 重命名本地分支
        ihelper.execute('git branch -m ' + old + ' ' + new)
        # 删除远程分支
        ihelper.execute('git push --delete origin ' + old)
        # 上传新分支
        ihelper.execute('git push origin ' + new + ':' + new)

    def git(self):
        ihelper.execute('git ' + (' '.join(self.args) if self.args else ''))




