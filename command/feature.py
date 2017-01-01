# coding:utf-8

import sys
import os
from CVS import CVS
import exception
import extra
import igit
import ihelper
import iglobal
from iprint import *


class Feature(CVS):
    """
    特性分支指令类
    """
    def __init__(self, cmd, args, log=True):
        CVS.__init__(self, cmd, args, log)
        # 二级指令
        self.sub_cmd_list = ('create', 'test', 'product', 'tag', 'show', 'delete',"checkout")

    def execute(self):
        if not len(self.args):
            return extra.Extra('help', [self.cmd], log=False).execute()

        sub_cmd = self.real_cmd(self.args.pop(0), valid=False)
        if sub_cmd not in self.sub_cmd_list:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        # 调用相应的二级指令处理方法
        eval('self.' + sub_cmd)()

    def checkout(self):
        """
        切换到某个特性分支并拉取最新代码（如果工作空间是干净的）
        :return:
        """
        if not self.args:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        # 检查当前分支下工作区状态
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未提交的内容，请先用commit提交或用git stash保存到Git栈中')

        branch = None
        no_pull = False

        while self.args:
            c = self.args.pop(0)
            if c == '--np' or c == '--no-pull':
                no_pull = True
            else:
                branch = igit.real_branch(c, self.cmd)

        __error = False
        if branch != igit.current_branch():
            out = ihelper.execute('git checkout ' + branch, return_result=True)
            # git的checkout指令输出在stderr中
            if out.find('Switched to branch') == -1:
                __error = True

        if not no_pull and not __error and igit.workspace_is_clean():
            igit.pull()

    def create(self):
        """
        创建特性分支。一次只能创建一个，会推到远端，且切换到此分支
        :return:
        """
        if not self.args:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        if len(self.args) > 2:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        branch = None
        auto_create_from_remote = False

        while self.args:
            c = self.args.pop(0)
            if c == '-y':
                auto_create_from_remote = True
            else:
                branch = c

        if not branch:
            raise exception.FlowException(u'请输入分支名称')

        branch = igit.real_branch(branch, self.cmd)

        # 检查当前分支下工作区状态
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未提交的内容，请先用git commit提交或用git stash保存到Git栈中')

        # 分支名称重复性检查
        info(u'检查本地分支...')
        if branch in igit.local_branches():
            raise exception.FlowException(u'该分支名称已经存在')

        # 本地没有但远程有
        create_from_remote = False
        info(u'检查远程分支...')
        if branch in igit.remote_branches():
            if not auto_create_from_remote and ihelper.confirm(u'远程仓库已存在%s，是否基于该远程分支创建本地分支？' % branch) != 'y':
                return
            else:
                create_from_remote = True

        say(('white', u'正在创建分支'), ('sky_blue', branch), ('white', '...'))

        if create_from_remote:
            # 基于远程分支创建本地分支，会自动追踪该远程分支
            ihelper.execute('git checkout -b ' + branch + ' origin/' + branch)
        else:
            # 切换到生产分支
            p_branch = igit.product_branch()
            ihelper.execute('git checkout ' + p_branch)
            igit.pull()

            # 基于本地生产分支创建新分支
            ihelper.execute('git checkout -b ' + branch)

            # 推送到远程
            ihelper.execute('git push -u origin ' + branch + ':' + branch)

        if igit.workspace_is_clean():
            ok(u'创建成功!已进入分支：' + branch)
        else:
            raise exception.FlowException(u'创建分支失败')

    def test(self):
        """
        发布到测试分支，只允许单个分支发布
        :return:
        """
        if len(self.args) > 1:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        # 当前工作空间是否干净
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未提交的内容')

        if not self.args:
            branch = igit.current_branch()
        else:
            branch = self.args.pop(0)

        branch = igit.real_branch(branch, self.cmd)

        if branch != igit.current_branch():
            # 切换分支
            info(u'切换到分支%s' % branch)
            ihelper.execute('git checkout ' + branch)

            # 当前工作空间是否干净
            if not igit.workspace_is_clean():
                raise exception.FlowException(u'工作区中尚有未提交的内容')

        # 推到远程仓库
        info(u'推送到远程仓库...')
        igit.push(branch)

        # 切换到test分支
        test_branch = igit.test_branch()
        info(u'切换到分支%s' % test_branch)
        ihelper.execute('git checkout ' + test_branch)

        # 当前工作空间是否干净
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未提交的内容')

        # 合并
        info(u'正在将%s合并到%s上...' % (branch, test_branch))
        igit.merge(branch)

        # 正常执行后，工作空间应该是干净的
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'合并失败,请用git status查看工作空间详情')

        # 切换到原来的分支
        info(u'切换回%s' % branch)
        ihelper.execute('git checkout ' + branch)

        ok(u'合并到' + test_branch + u'成功!')

    def delete(self):
        """
        删除分支
        :return:
        """
        if not self.args:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        branch = igit.real_branch(self.args.pop(0), self.cmd)

        # if branch == igit.current_branch():
        #     raise exception.FlowException(u'不能删除当前分支')

        if ihelper.confirm(u'确定删除分支 %s 吗?' % branch, default='n') == 'y':
            info(u'删除本地分支...')
            ihelper.execute('git branch -D %s' % branch, raise_err=True)
            # 删除远程分支
            info(u'删除远程分支...')
            ihelper.execute('git push --delete origin %s' % branch)
            ok(u'删除成功!')

    def product(self):
        """
        发布到生产分支
        :return:
        """
        pass
    

























