# coding:utf-8

import os
from CVS import CVS
import exception
import ihelper
import igit
from iprint import *
import iglobal


class Git(CVS):
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
        分支重命名。old和new需要时绝对分支名
        """
        if len(self.args) < 2:
            raise exception.FlowException('指令格式错误，请输入help查看使用说明')

        old = self.args[0]
        new = self.args[1]

        local_branches = igit.local_branches()

        if old not in local_branches:
            raise exception.FlowException(u'分支名称不存在：%s' % old)

        remote_branches = igit.remote_branches()

        # 名称重复性检测
        if new in local_branches or new in remote_branches:
            raise exception.FlowException(u'该分支已经存在：%s' % new)

        info(u'重命名分支：%s -> %s...' % (old, new))

        # 重命名本地分支
        ihelper.execute('git branch -m ' + old + ' ' + new, raise_err=True)
        # 删除远程分支(如果有的话)
        if old in remote_branches:
            ihelper.execute('git push --delete origin ' + old)
        # 上传新分支到远程
        ihelper.execute('git push -u origin ' + new + ':' + new)

    def git(self):
        """
        git原生指令
        """
        ihelper.execute('git ' + (' '.join(self.args) if self.args else ''))

    def commit(self):
        """
        提交
        ft commit -p 去掉类型限制
        ft commit 去掉类型限制
        :return:
        """
        comment = None
        push = False

        if not self.args or len(self.args) > 2:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        while self.args:
            c = self.args.pop(0)
            if c == '-p':
                push = True
            else:
                comment = c

        if not comment:
            raise exception.FlowException(u'请填写提交说明')

        curr_branch = igit.current_branch()

        # 提交
        ihelper.execute('git add .')
        ihelper.execute('git commit -m "' + igit.comment(comment, curr_branch.split('/')[0]).decode('utf-8').encode(iglobal.FROM_ENCODING) + '"')

        if push:
            igit.push(curr_branch)

        ok(u'提交' + (u'并推送到远程仓库' if push else '') + u'成功!')