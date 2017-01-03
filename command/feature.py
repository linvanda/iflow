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
        branch = None
        while self.args:
            branch = igit.real_branch(self.args.pop(0), self.cmd)

        if not branch:
            branch = igit.current_branch()

        __error = False
        if branch != igit.current_branch():
            # 检查当前分支下工作区状态
            if not igit.workspace_is_clean():
                raise exception.FlowException(u'工作区中尚有未提交的内容，请先用commit提交或用git stash保存到Git栈中')

            out = ihelper.execute('git checkout ' + branch, return_result=True)
            # git的checkout指令输出在stderr中
            if 'Switched to branch' not in out:
                __error = True

        if not __error:
            ihelper.execute('git fetch')

        status = igit.workspace_status()
        if status & iglobal.GIT_BEHIND or status & iglobal.GIT_DIVERGED:
            warn(u'远程仓库已有更新，请执行 git rebase 获取最新代码')

    def create(self):
        """
        创建特性分支。一次只能创建一个，会推到远端，且切换到此分支
        :return:
        """
        if not self.args:
            raise exception.FlowException(u'指令格式错误，请输入h ft查看使用说明')

        branch = None
        auto_create_from_remote = False
        push_to_remote = True

        while self.args:
            c = self.args.pop(0)
            if c == '-y':
                auto_create_from_remote = True
            elif c == '--np' or c == '--no-push':
                push_to_remote = False
            else:
                branch = c

        if not branch:
            raise exception.FlowException(u'请输入分支名称')

        # 分支简称不可与项目、迭代名称相同(防止一些指令出现歧义)
        simple_branch = igit.simple_branch(branch)
        if simple_branch == iglobal.SPRINT or simple_branch in ihelper.projects():
            raise exception.FlowException(u'分支简称不可与项目或迭代名同名')

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
            if push_to_remote:
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
            raise exception.FlowException(u'工作区中尚有未保存的内容')

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
                raise exception.FlowException(u'工作区中尚有未保存的内容')

        # 推到远程仓库
        info(u'推送到远程仓库...')
        igit.push(branch)

        # 切换到test分支
        test_branch = igit.test_branch()
        info(u'切换到分支%s' % test_branch)
        ihelper.execute('git checkout ' + test_branch)

        # 当前工作空间是否干净
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未保存的内容')

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

        branch = None
        delete_remote = True

        while self.args:
            c = self.args.pop(0)
            if c == '--np' or c == '--no-push':
                delete_remote = False
            else:
                branch = igit.real_branch(c, self.cmd)

        if not branch:
            raise exception.FlowException(u'请输入分支名称')

        if branch == igit.current_branch():
            raise exception.FlowException(u'不能删除当前分支')

        if ihelper.confirm(u'确定删除分支 %s 吗?' % branch, default='n') == 'y':
            info(u'删除本地分支...')
            ihelper.execute('git branch -D %s' % branch, raise_err=True)
            # 删除远程分支
            if delete_remote:
                info(u'删除远程分支...')
                ihelper.execute('git push --delete origin %s' % branch)
                ok(u'删除成功!')

    def product(self):
        """
        发布到生产分支
        未完成
        :return:
        """
        create_tag = False
        continue_p = False
        abort_p = False
        branches = None
        branch_alias = {}
        tick = 1

        branch_str = None
        while self.args:
            c = self.args.pop(0)

            if c == '--abort':
                abort_p = True
            elif c == '--continue':
                continue_p = True
            elif c == '-t':
                create_tag = True
            else:
                branch_str = c

        if abort_p:
            # 清除runtime后退出
            ihelper.write_runtime('publish_branches')
            return

        if continue_p:
            # 继续上次的发布
            self.publish_to_master()
            return

        branches = self.__resolve_branches(branch_str)
        for key, val in branches.items():
            if not val:
                branches.pop(key)

        if not branches:
            warn(u'没有需要发布的分支')
            return

        # 打印列表，并为分支设置别名
        warn(u'待发布分支列表：')
        for proj, p_brs in branches.items():
            ok(proj + u'：')
            for pbr in p_brs:
                alias = 'f%s' % tick
                say(('white', ' [ '), ('green', alias), ('white', ' ] %s' % pbr))
                branch_alias[alias] = (proj, pbr)
                tick += 1

        print
        info(u'1. 输入 "in 分支简称列表(f1,f2...，多个分支用英文逗号隔开)" 告知系统要发布的分支。或者')
        info(u'2. 输入 "ex 分支简称列表" 告知系统要排除的分支。或者')
        info(u'4. 输入 all 发布以上列出的所有项目分支。或者')
        info(u'5. 输入 cancel 取消发布')
        print

        in_branches = []
        ex_branches = []
        all = False

        retr = True
        while retr:
            retr = False

            final_branches = self.__choose_branch_dialog(branch_alias)

            if final_branches == 'cancel':
                return

            print
            warn(u'将发布以下分支到生产环境：')

            the_proj = None
            for ele in final_branches:
                if the_proj != ele[0]:
                    the_proj = ele[0]
                    ok(ele[0] + ':')
                info('  ' + ele[1])

            print
            confirm = ihelper.confirm(u'请确认')
            if confirm == 'c':
                return
            elif confirm == 'n':
                # 返回分支选择
                info(u'请重新选择待发布分支...')
                retr = True
            elif confirm == 'y':
                # 开始执行发布，发布前先持久化待发布列表
                ihelper.write_runtime('publish_branches', final_branches)
                info(u'正在发布...')
                self.publish_to_master(final_branches)

    def publish_to_master(self,branches=None):
        """
        发布分支到生产环境
        :param branches: 待发布分支列表：[(proj_name, branch)]
        """
        if not branches:
            branches = ihelper.read_runtime('publish_branches')

        if not branches:
            info(u'没有需要发布的分支')
            return

        orig_branches = branches
        try:
            the_proj = None
            for index, item in enumerate(branches):
                proj, branch = tuple(item)
                if iglobal.PROJECT != proj:
                    extra.Extra('cd', [proj], log=False)

                if not igit.workspace_is_clean():
                    raise exception.FlowException(u'项目%s工作空间有未提交的更改，请先提交(或丢弃)后执行 ft p --continue 继续' % proj)

                if the_proj != proj:
                    ihelper.execute('git fetch')

                ihelper.execute('git checkout %s' % branch)

                if igit.workspace_status() & iglobal.GIT_BEHIND:
                    # 此处可能会抛异常中断执行
                    igit.pull()

                # 切换到master分支
                if proj != the_proj:
                    ihelper.execute('git checkout %s' % igit.product_branch())
                # 合并
                igit.merge(branch, need_pull=proj != the_proj, need_push= index >= len(branches) - 1 or proj != branches[index + 1][0])

                orig_branches.remove(item)
        except Exception, e:
            error(e)
            warn(u'解决后执行 ft p --continue 继续。或执行 ft p --abort 结束')
        finally:
            ihelper.write_runtime('publish_branches', orig_branches)

    @staticmethod
    def __choose_branch_dialog(branch_alias):
        all = False
        in_branches = ex_branches = []

        while True:
            word = raw_input('$ 请选择: '.decode('utf-8')
                             .encode(iglobal.FROM_ENCODING))\
                             .replace('，', ',').strip()
            if not word:
                continue

            if word != 'all' and word != 'cancel' and not word.startswith('in ') and not word.startswith('ex '):
                error(u'无效的输入')
                continue

            if word == 'cancel':
                return 'cancel'
            elif word.startswith('in '):
                in_branches = [ele.strip() for ele in word.lstrip('in ').split(',')]
            elif word.startswith('ex '):
                ex_branches = [ele.strip() for ele in word.lstrip('ex ').split(',')]
            elif word == 'all':
                all = True

            if set(in_branches + ex_branches).difference(set(branch_alias.keys())):
                error(u'无效的输入')
                continue

            break

        # in_branches和ex_branches只用一个
        final_branches = []

        if all:
            final_branches = branch_alias.values()
        elif in_branches:
            for key, val in branch_alias.items():
                if key in in_branches:
                    final_branches.append(val)
        elif ex_branches:
            for key, val in branch_alias.items():
                if key not in ex_branches:
                    final_branches.append(val)

        final_branches.sort(key=lambda ele: ele[0])

        return final_branches

    def __resolve_branches(self, branch_str):
        """
        分支解析
        vmember,member-center
        vmember:/weigao,membercenter:order
        order-manager
        :param str branch_str:
        :return:dict
        """
        if not branch_str:
            # 所有项目
            branch_str = ','.join(map(lambda x:str(x) + ':*', ihelper.projects()))

        branch_str.strip().replace('，', ',').replace('：', ':')
        arr = branch_str.split(',')

        branches = {}
        for br in arr:
            if ':' not in br:
                # 判断是项目名还是分支名
                if br in ihelper.projects():
                    br += ':*'
                else:
                    br = iglobal.PROJECT + ':' + br

            br = br.split(':')
            proj = br[0]
            branch = br[1]

            if branch == '*':
                # 同步该项目下的本地和远程分支
                igit.sync(proj, self.cmd)
                # 获取该项目下的所有相关分支
                branch = igit.project_branches(self.cmd, proj)
            else:
                branch = [igit.real_branch(branch, self.cmd)]

            if not branches.has_key(proj):
                branches[proj] = []

            branches[proj] += branch

        # 去重
        for key, val in branches.items():
            branches[key] = list(set(val))

        return branches























