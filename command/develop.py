# coding:utf-8
from CVS import CVS
import extra
import exception
import igit
import ihelper
import iconfig
from iprint import *
import icommand


class Develop(CVS):
    """
    test和feature分支指令基类
    """
    sub_cmd_list = ('create', 'test', 'product', 'delete',"checkout")
    parameters = {
        'delete': ['--no-push', '-y'],
        'product': ['--continue', '--abort'],
        'create': ['-y', '--no-push'],
        'checkout': ['-r']
    }

    def __init__(self, cmd, args):
        CVS.__init__(self, cmd, args)

    def execute(self):
        # 如果没有提供二级指令，默认为checkout
        if not self.args:
            self.args.insert(0, 'checkout')

        sub_cmd = icommand.real_cmd(self.args[0], raise_err=False, top_cmd=self.cmd)

        if not sub_cmd or sub_cmd not in self.sub_cmd_list:
            self.args.insert(0, 'checkout')
            sub_cmd = 'checkout'

        # 调用相应的二级指令处理方法
        eval('self.' + sub_cmd)(self.args[1:])

    def checkout(self, args):
        """
        切换到某个特性/修复分支并拉取最新代码（如果工作空间是干净的）
        :return:
        """
        branch = None
        sync_remote = False
        while args:
            c = args.pop(0)
            if c == '-r' or c == '--remote':
                sync_remote = True
            else:
                branch = igit.real_branch(c, self.cmd)

        current_branch = igit.current_branch()

        if not branch:
            branch = current_branch

        if branch == current_branch:
            sync_remote = True

        __error = False
        if branch != current_branch:
            # 检查当前分支下工作区状态
            if not igit.workspace_is_clean():
                raise exception.FlowException(u'工作区中尚有未提交的内容，请先用commit提交或用git stash保存到Git栈中')

            out = ihelper.execute('git checkout ' + branch, return_result=True)
            # git的checkout指令输出在stderr中
            if 'Switched to branch' not in out:
                __error = True

        if __error:
            warn(u'checkout失败')
            return

        if sync_remote:
            info('fetch from remote...')
            igit.fetch()

        status = igit.workspace_status()
        if status & iglobal.GIT_BEHIND or status & iglobal.GIT_DIVERGED:
            warn(u'远程仓库已有更新，请执行 git rebase 获取最新代码')

    def create(self, args):
        """
        创建特性/修复分支。一次只能创建一个，会推到远端，且切换到此分支
        :return:
        """
        if not args:
            raise exception.FlowException(u'指令格式错误，请输入h %s查看使用说明' % self.cmd)

        branch = None
        auto_create_from_remote = False
        push_to_remote = True

        while args:
            c = args.pop(0)
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

    def test(self, args):
        """
        发布到测试分支，只允许单个分支发布
        :param args:
        :return:
        """
        # 当前工作空间是否干净
        if not igit.workspace_is_clean():
            raise exception.FlowException(u'工作区中尚有未保存的内容')

        if not args:
            branch = igit.current_branch()
        else:
            branch = args.pop(0)

        branch = igit.real_branch(branch, self.cmd)

        if branch != igit.current_branch():
            # 切换分支
            info(u'切换到分支%s' % branch)
            ihelper.execute('git checkout ' + branch)

            # 当前工作空间是否干净
            if not igit.workspace_is_clean():
                raise exception.FlowException(u'工作区中尚有未保存的内容')

        igit.sync_branch()

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

        # 将test推到远程
        igit.push()

        # 切换到原来的分支
        info(u'切换回%s' % branch)
        ihelper.execute('git checkout ' + branch)

        ok(u'合并到' + test_branch + u'成功!')

    def delete(self, args):
        """
        删除分支
        :return:
        """
        if not args:
            raise exception.FlowException(u'指令格式错误，请输入h %s查看使用说明' % self.cmd)

        branch = None
        delete_remote = True
        auto_delete = False

        while args:
            c = args.pop(0)
            if c == '--np' or c == '--no-push':
                delete_remote = False
            elif c == '-y':
                auto_delete = True
            else:
                branch = igit.real_branch(c, self.cmd)

        if not branch:
            raise exception.FlowException(u'请输入分支名称')

        if auto_delete or ihelper.confirm(u'确定删除分支 %s 吗?' % branch, default='n') == 'y':
            igit.delete_branch(branch, del_remote=delete_remote)


    def product(self, args):
        """
        发布到生产分支
        :param list args:
        :return:
        """
        continue_p = False
        abort_p = False
        branch_alias = {}
        tick = 1

        line_branches = []
        while args:
            c = args.pop(0)

            if c == '--abort':
                abort_p = True
            elif c == '--continue':
                continue_p = True
            else:
                if c.endswith(':'):
                    c += '*'
                line_branches.append(c)

        if abort_p:
            # 清除runtime后退出
            ok(u'取消发布')
            ihelper.write_runtime('publish_branches')
            ihelper.write_runtime('publish_tags')
            return

        if continue_p:
            # 继续上次的发布
            self.publish_to_master()
            return

        if ihelper.read_runtime('publish_branches'):
            error(u'上次发布尚未完成，请执行 ft p --continue 继续，或执行 ft p --abort 结束')
            return

        branches = self.__resolve_branches(line_branches)
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
        info(u'1. 输入 "in 分支简称列表(f1 f2...，多个分支用空格隔开)" 告知系统要发布的分支。或者')
        info(u'2. 输入 "ex 分支简称列表" 告知系统要排除的分支。或者')
        info(u'3. 输入 all 发布以上列出的所有项目分支。或者')
        info(u'4. 输入 cancel 取消发布')
        print

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
        curr_p_branch = None
        tag_list = []

        if not branches:
            #接着上次的继续发布
            branches = ihelper.read_runtime('publish_branches')
            tag_list = ihelper.read_runtime('publish_tags') or []

        if not branches:
            info(u'没有需要发布的分支')
            return

        orig_branches = list(branches)

        try:
            curr_proj = None
            for index, item in enumerate(branches):
                curr_p_branch = item
                proj, branch = tuple(item)

                if iglobal.PROJECT != proj:
                    info(u'进入项目%s' % proj)
                    extra.Extra('cd', [proj]).execute()

                if not igit.workspace_is_clean():
                    raise exception.FlowException(u'项目%s工作空间有未提交的更改，请先提交(或丢弃)后执行 ft p --continue 继续' % proj)

                #首次进入项目执行fetch获取本地和远程分支差异
                if curr_proj != proj:
                    info('fetch...')
                    igit.fetch(useCache=False)

                # 切换到将要合并的分支(如果不存在本地分支则会自动创建)
                ihelper.execute('git checkout %s' % branch)

                # 同步当前本地和远程分支(此处可能会出现冲突)
                igit.sync_branch()

                # 切换到master分支
                ihelper.execute('git checkout %s' % igit.product_branch())

                is_last_branch = index >= len(branches) - 1 or proj != branches[index + 1][0]

                # 合并
                info(u'合并%s...' % branch)
                igit.merge(branch, need_pull=proj != curr_proj, need_push=is_last_branch)
                info(u'合并完成：%s' % branch)

                # 完成
                orig_branches.remove(curr_p_branch)

                if proj != curr_proj:
                    curr_proj = proj

                # 打标签
                if is_last_branch:
                    info(u'项目 %s 发布完成，打标签：' % proj)
                    proj_tag = self.__tag()

                    if proj_tag:
                        tag_list.append((proj, proj_tag))

            ok(u'发布完成！tag：')

            #打印tag信息
            for (proj_name, tag_name) in tag_list:
                info(' %s  %s' % (proj_name, tag_name))

            #清空tag list
            tag_list = []
        except Exception, e:
            error(e.message)
            warn(u'合并%s的分支%s时出现冲突' % (proj, curr_p_branch[1]))
            warn(u'解决冲突后执行 ft p --continue 继续。或执行 ft p --abort 结束')
        finally:
            #持久化发布状态
            ihelper.write_runtime('publish_branches', orig_branches)
            ihelper.write_runtime('publish_tags', tag_list)

    def __tag(self):
        """
        发布到生产需要强制打标签
        :return:
        """
        default_tag = igit.tag_name()
        while 1:
            input_tag = raw_input((u'标签 %s (回车确认，或输入自定义标签。输入n不打标签)：' % (default_tag if default_tag else ''))
                                  .decode('utf-8').encode(iglobal.FROM_ENCODING)).lower().strip()
            if not input_tag:
                if default_tag:
                    input_tag = default_tag
                else:
                    continue

            if input_tag == 'n':
                return None

            info(u'打标签...')
            try:
                print igit.tag(input_tag, 'normal publish')
            except exception.FlowException, e:
                error(u'该标签已存在')
                continue

            return input_tag

    @staticmethod
    def __choose_branch_dialog(branch_alias):
        all = False
        in_branches = ex_branches = []

        ihelper.disable_readline()

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
                ihelper.enable_readline()
                return 'cancel'
            elif word.startswith('in '):
                in_branches = [ele.strip() for ele in word.lstrip('in ').split(' ')]
            elif word.startswith('ex '):
                ex_branches = [ele.strip() for ele in word.lstrip('ex ').split(' ')]
            elif word == 'all':
                all = True

            if set(in_branches + ex_branches).difference(set(branch_alias.keys())):
                error(u'无效的输入')
                continue

            break

        ihelper.enable_readline()

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

    def __resolve_branches(self, line_branches):
        """
        分支解析
        vmember,member-center
        vmember:/weigao,membercenter:order
        order-manager
        :param list line_branches:
        :return:dict
        """
        if not line_branches:
            # 所有项目
            line_branches = map(lambda x:str(x) + ':*', ihelper.projects())

        line_branches = map(lambda x: x.replace('：', ':'), line_branches)

        branches = {}
        only_this_sprint = True if self.cmd == iconfig.read_config('system', 'branch')['feature_prefix'] else False
        for br in line_branches:
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
                igit.sync(proj, self.cmd, only_this_sprint=self.cmd == iconfig.read_config('system', 'branch')['feature_prefix'])
                # 获取该项目下的所有相关分支
                branch = igit.project_branches(self.cmd, proj, only_this_sprint)
            else:
                branch = [igit.real_branch(branch, self.cmd)]

            if not branches.has_key(proj):
                branches[proj] = []

            branches[proj] += branch

        # 去重
        for key, val in branches.items():
            branches[key] = list(set(val))

        return branches