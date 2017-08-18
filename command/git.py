# coding:utf-8

import re
from CVS import CVS
from iprint import *
import exception
import ihelper
import igit
import iglobal


class Git(CVS):
    """
    git相关指令
    """
    parameters = {
        'commit': ['-p'],
        'tag': ['-a', '-m'],
        'delete': ['--no-remote']
    }

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

    def tag(self):
        """
        在生产分支上打标签
        :return:
        """
        if not self.args:
            return ihelper.execute('git tag')

        #将要在该分支上打标签
        tag_branch = igit.product_branch()

        # 当前工作空间是否干净
        if igit.current_branch() != tag_branch and not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未保存的内容')

        tag_name = None
        comment = ''

        while self.args:
            c = self.args.pop(0)
            if c == '-a':
                tag_name = self.args.pop(0)
            elif c == '-m':
                while self.args:
                    if self.args[0].startswith('-'):
                        break

                    comment += self.args.pop(0) + ' '

        if not comment:
            raise exception.FlowException(u'请输入标签注释')

        if not tag_name:
            tag_name = igit.tag_name()

        if not tag_name:
            raise exception.FlowException(u'未设置tag name')

        if ihelper.confirm(u'将在分支 %s 上打tag：%s, ok?' % (tag_branch, tag_name)) != 'y':
            warn(u'取消操作')
            return

        c_branch = igit.current_branch()

        try:
            #切换分支
            if c_branch != tag_branch:
                info(u'切换到分支 %s:' % tag_branch)
                ihelper.execute('git checkout %s' % tag_branch)

            #打tag
            print igit.tag(tag_name, comment)
        except exception.FlowException, e:
            error(u'操作失败：')
            raise e
        finally:
            if c_branch != igit.current_branch():
                info(u'切换回 %s' % c_branch)
                ihelper.execute('git checkout %s' % c_branch)

        ok(u'操作成功!')

    def delete(self):
        """
        删除本地匹配模式的多个分支，并删除远程相应分支
        :return:
        """
        if not self.args:
            raise exception.FlowException(u'指令格式错误，请输入help查看使用说明')

        tag_pattern = None
        del_remote  = True
        del_branches = []

        while self.args:
            c = self.args.pop(0)
            if c == '--no-remote':
                del_remote = False
            else:
                tag_pattern = c

        if not tag_pattern:
            raise exception.FlowException(u'请指定需要删除的分支匹配模式')

        for branch in igit.local_branches():
            if branch == igit.product_branch():
                continue
            if re.match(tag_pattern, branch):
                del_branches.append(branch)

        if not del_branches:
            warn(u'没有符合条件的分支')
            return

        #打印出将要删除的分支列表
        warn(u'将要删除以下分支%s：' % ('(以及其对应的远程分支)' if del_remote else ''))
        for del_branch in del_branches:
            ok(del_branch)

        print

        if (ihelper.confirm(u'确定删除吗%s？' % ('(同时删除远程分支，删除后不可恢复)' if del_remote else ''), 'n') != 'y'):
            return

        #删除分支
        for del_branch in del_branches:
            try:
                igit.delete_branch(del_branch, del_remote)
            except exception.FlowException, e:
                warn(str(e))

    def commit(self):
        """
        提交
        :return:
        """
        comment = ''
        push = False

        if not self.args:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        while self.args:
            c = self.args.pop(0)
            if c == '-p':
                push = True
            else:
                comment += ' %s' % c

        comment = comment.strip()

        if not comment:
            raise exception.FlowException(u'请填写提交说明')

        curr_branch = igit.current_branch()

        # 提交
        ihelper.execute('git add .')
        ihelper.execute('git commit -m "' + igit.comment(comment, curr_branch.split('/')[0]).decode('utf-8').encode(iglobal.FROM_ENCODING) + '"')

        if push:
            igit.push(curr_branch)

        ok(u'提交' + (u'并推送到远程仓库' if push else '') + u'成功!')