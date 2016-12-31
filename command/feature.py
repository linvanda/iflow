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
        self.sub_cmd_list = ('create', 'test', 'publish', 'tag', 'show', 'delete')

    def execute(self):
        if not len(self.args):
            return extra.Extra('help', [self.cmd], log=False).execute()

        sub_cmd = self.real_cmd(self.args.pop(0), valid=False)
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

        if len(self.args) > 1:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        branch = self.args.pop(0)

        if not branch:
            raise exception.FlowException(u'请输入分支名称')

        branch = igit.real_branch(branch, self.cmd)

        # 分支名称重复性检查
        if branch in igit.local_branches() or branch in igit.remote_branches(False):
            raise exception.FlowException(u'该分支名称已经存在')

        # 检查当前分支下工作区状态
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未提交的内容，请先用git commit提交或用git stash保存到Git栈中，或丢弃掉')

        white(u'正在创建分支'),sky_blue(branch), white('...', True)

        # 切换到生产分支
        p_branch = igit.product_branch()
        ihelper.execute('git checkout ' + p_branch)
        ihelper.execute('git pull --rebase', raise_err=True)

        # 创建新分支
        ihelper.execute('git checkout -b ' + branch)

        # 推送到远程
        ihelper.execute('git push -u origin ' + branch + ':' + branch)

        ok(u'创建成功!已进入分支：' + branch)

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

        branch = igit.real_branch(branch)

        if branch != igit.current_branch():
            # 切换分支
            ihelper.execute('git checkout ' + branch)

            # 当前工作空间是否干净
            if not igit.workspace_is_clean():
                raise exception.FlowException(u'工作区中尚有未提交的内容')

        # 推到远程仓库
        igit.push(branch)

        # 切换到test分支
        test_branch = igit.test_branch()
        ihelper.execute('git checkout ' + test_branch)

        # 当前工作空间是否干净
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未提交的内容')

        # 合并
        igit.merge(branch)

        ok(u'合并到' + test_branch + u'成功!已进入分支：' + test_branch)

























