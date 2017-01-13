# coding:utf-8

from CVS import CVS
import git
import exception
import ihelper
import isprint
import igit
import iconfig
import iglobal
from iprint import info, ok


class Transform(CVS):
    """
    分支转换
    -n|--next：下个迭代
    -s|--sprint：指定迭代名称
    """
    parameters = ['--next', '--sprint']

    def execute(self):
        try:
            eval('self.' + self.cmd)(list(self.args))
        except exception.FlowException, e:
            raise Exception(unicode(str(e), 'utf-8'))
        except Exception, e:
            raise Exception(e.message)

    def h2f(self, args):
        """
        修复分支转特性分支，默认转本迭代
        :param args:
        :return:
        """
        b_info = self.__branch_and_sprint(args)
        if not b_info['branch']:
            raise exception.FlowException(u'未指定分支名称')

        old_branch = igit.real_branch(b_info['branch'], iconfig.read_config('system', 'branch')['hotfix_prefix'])
        new_branch = igit.real_branch('%s/%s' % (b_info['sprint'], b_info['branch']), iconfig.read_config('system', 'branch')['feature_prefix'])

        if not old_branch or not new_branch:
            raise exception.FlowException(u'分支名称不合法')

        if old_branch not in igit.local_branches():
            raise exception.FlowException(u'分支不存在：%s' % old_branch)

        if ihelper.confirm(u'确定将修复分支%s转为特性分支%s吗？' % (old_branch, new_branch)) == 'y':
            git.Git('rename', [old_branch, new_branch]).execute()
            ok()
        else:
            ok(u'取消操作')

    def f2h(self, args):
        """
        本迭代的特性分支转修复分支
        :return:
        """
        branch = None
        while args:
            branch = args.pop(0)

        if not branch:
            raise exception.FlowException(u'未指定分支名称')

        old_branch = igit.real_branch(branch, iconfig.read_config('system', 'branch')['feature_prefix'])
        new_branch = igit.real_branch(branch, iconfig.read_config('system', 'branch')['hotfix_prefix'])

        if not old_branch or not new_branch:
            raise exception.FlowException(u'分支名称不合法')

        if old_branch not in igit.local_branches():
            raise exception.FlowException(u'分支不存在：%s' % old_branch)

        if ihelper.confirm(u'确定将特性分支%s转为修复分支%s吗？' % (old_branch, new_branch)) == 'y':
            git.Git('rename', [old_branch, new_branch]).execute()
            ok()
        else:
            ok(u'取消操作')

    def f2f(self, args):
        """
        修复分支转修复分支，默认转到下个迭代
        :param list args:
        :return:
        """
        if '-n' not in args and '-s' not in args:
            args.append('-n')

        b_info = self.__branch_and_sprint(args)
        if not b_info['branch']:
            raise exception.FlowException(u'未指定分支名称')

        old_branch = igit.real_branch(b_info['branch'], iconfig.read_config('system', 'branch')['feature_prefix'])
        new_branch = igit.real_branch('%s/%s' % (b_info['sprint'], b_info['branch']), iconfig.read_config('system', 'branch')['feature_prefix'])

        if not old_branch or not new_branch:
            raise exception.FlowException(u'分支名称不合法')

        if old_branch not in igit.local_branches():
            raise exception.FlowException(u'分支不存在：%s' % old_branch)

        if ihelper.confirm(u'确定将特性分支%s转为特性分支%s吗？' % (old_branch, new_branch)) == 'y':
            git.Git('rename', [old_branch, new_branch]).execute()
            ok()
        else:
            ok(u'取消操作')

    def __branch_and_sprint(self, args):
        sprint = branch = None
        while args:
            c = args.pop(0)
            if c == '-s' or c == '--sprint':
                sprint = isprint.get_sprint(args.pop(0))
            elif c == '-n' or c == '--next':
                sprint = isprint.next_sprint()
            else:
                branch = c

        sprint = sprint or iglobal.SPRINT

        return {'branch': branch, 'sprint': sprint}
