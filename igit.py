# coding:utf-8

import os
import re
import time
import datetime
import subprocess
import iconfig
import isprint
import ihelper
import iglobal
import exception
from iprint import *
import command

__sub_cmd_list = None


def get_config(key=None):
    """
    获取git配置列表
    :param key:
    :return:
    """
    config = dict(map(lambda x:x.split('='), ihelper.popen('git config -l').splitlines()))
    return config[key] if key and config.has_key(key) else config


def current_branch():
    """
    获取当前分支
    :return:
    """
    branch = filter(lambda x:x.find('*') != -1, ihelper.popen('git branch').splitlines())
    return branch[0].replace('*', '').strip() if branch else None


def local_branches():
    """
    所有的本地分支列表
    :return list
    """
    return map(lambda x:str(x).lstrip('*').strip(), ihelper.popen('git branch').splitlines())


def remote_branches(refresh=True):
    """
    远程分支列表
    :param refresh:
    """
    # 先拉一下最新的远程分支
    if refresh:
        ihelper.execute('git fetch')

    return map(lambda x:str(x).replace('origin/HEAD -> ', '').replace('origin/', '').strip(),
               ihelper.execute('git branch -r', print_out=False, return_result=True).splitlines())


def dir_is_repository(path=None):
    """
    检查目录是不是git仓库
    :param path:
    :return:
    """
    path = path or os.getcwd()
    if not os.path.isdir(path):
        return False

    curr_dir = os.getcwd()
    os.chdir(path)
    result = True

    out = ihelper.popen('git branch')
    if out.find('Not a git repository') != -1:
        result = False

    os.chdir(curr_dir)

    return result


def workspace_is_clean():
    """
    检查当前分支的工作区是否是清洁的
    工作区、暂存区都必须是清洁的才返回True，即用git status -s查看结果为空
    """
    return workspace_status() & iglobal.GIT_CLEAN


def real_branch( branch, prefix):
    """
    获取完整的分支名
    :param str prefix:
    :param str branch:
    :return: str
    """
    if not branch:
        raise Exception(u'参数错误')

    if branch.find(':') != -1:
        branch = branch.split(':')[1]

    original_branch = branch
    branch = filter(lambda x:x != '', branch.split('/'))
    config = iconfig.read_config('system', 'branch')

    if len(branch) > 2 and branch[0] != config['feature_prefix']:
        raise Exception(u'分支格式不合法')

    if len(branch) == 3:
        branch[1] = isprint.get_sprint(branch[1])
        if not branch[1]:
            raise Exception(u'分支格式不合法')
        return '/'.join(branch)

    if len(branch) == 2:
        if isprint.check_sprint_format(branch[0], True):
            # 迭代号开始的,此时prefix只能是feature
            if prefix != config['feature_prefix']:
                raise Exception(u'分支格式不合法')

            branch[0] = isprint.get_sprint(branch[0])
            branch.insert(0, config[prefix + '_prefix'])
        else:
            # 看是否以feature或hotfix开头
            if branch[0] != config['feature_prefix'] and branch[0] != config['hotfix_prefix']:
                raise Exception(u'分支格式不合法')

        return '/'.join(branch)

    if original_branch.find('/') == 0:
        return config[prefix + '_prefix'] + original_branch
    else:
        return config[prefix + '_prefix'] + ('/' + iglobal.SPRINT if prefix == 'feature' else '') + '/' + branch[0]


def simple_branch(branch):
    """
    获取分支精简名称
    :param str branch:
    :return: str
    """
    if not branch:
        raise exception.FlowException(u'请输入分支名称')

    if branch.startswith('/') and branch.count('/') == 1:
        return branch

    return branch.split('/').pop()


def product_branch():
    """
    获取项目的生产分支
    :return:
    """
    project = iglobal.PROJECT

    if project != 'global':
        proj_cfg = iconfig.read_config('project', project)
        if proj_cfg.has_key('branch') and dict(proj_cfg['branch']).has_key('product'):
            return proj_cfg['branch']['product']

    config = iconfig.read_config('system', 'branch')
    if config.has_key('product'):
        return config['product']
    else:
        return 'master'


def test_branch():
    """
    获取项目的测试分支
    :return:
    """
    project = iglobal.PROJECT

    if project != 'global':
        proj_cfg = iconfig.read_config('project', project)
        if proj_cfg.has_key('branch') and dict(proj_cfg['branch']).has_key('test'):
            return proj_cfg['branch']['test']

    config = iconfig.read_config('system', 'branch')
    if config.has_key('test'):
        return config['test']
    else:
        return 'sp-dev'


def comment(msg, btype=None):
    return '<' + btype + '>' + msg if btype else msg


def workspace_status(text=False):
    """
    工作空间状态
    :param text:
    :return:
    :return:
    """
    __status = 0

    out = ihelper.popen('git status')

    if 'working directory clean' in out:
        __status |= iglobal.GIT_CLEAN
    if 'Unmerged paths' in out:
        __status |= iglobal.GIT_CONFLICT
    if 'Changes to be committed' in out:
        __status |= iglobal.GIT_UNCOMMITED
    if 'Changes not staged for commit' in out or 'untracked files present' in out:
        __status |= iglobal.GIT_UNSTAGED
    if 'branch is ahead of' in out:
        __status |= iglobal.GIT_AHEAD
    if 'Your branch is behind' in out:
        __status |= iglobal.GIT_BEHIND
    if 'rebase in progress' in out:
        __status |= iglobal.GIT_REBASING
    if 'You are currently cherry-picking commit' in out:
        __status |= iglobal.GIT_CHERRING
    if 'You have unmerged paths' in out:
        __status |= iglobal.GIT_MERGING
    if 'All conflicts fixed but you are still merging' in out:
        __status |= iglobal.GIT_MERGING
    if 'have diverged' in out:
        __status |= iglobal.GIT_DIVERGED

    if not text:
        return __status
    else:
        return __status_code_to_text(__status)


def __status_code_to_text(code):
    if not code:
        return None

    text = []
    for c, t in iglobal.GIT_STATUS_MAP.items():
        if code & c:
            text.append(t)

    return '|'.join(text)


def push(branch=None):
    """
    将当前分支推到远程仓库
    :param branch:
    :return:
    """
    if not branch:
        branch = current_branch()

    status = workspace_status()
    if not branch or (not status & iglobal.GIT_AHEAD and not status & iglobal.GIT_DIVERGED):
        return

    # 先拉远程分支(如果报错则需要手工处理)
    pull()
    ihelper.execute('git push origin ' + branch + ':' + branch)


def sync_branch():
    if not workspace_is_clean():
        return

    pull()
    push()


def pull():
    """
    拉取当前分支
    :return:
    """
    status = workspace_status()
    if not status & iglobal.GIT_BEHIND or not status & iglobal.GIT_DIVERGED:
        return

    info(u'拉取远程分支...')
    ihelper.execute('git pull --rebase')
    status = workspace_status()
    if status & iglobal.GIT_CONFLICT:
        raise exception.FlowException(u'拉取远程分支出错：冲突。请手工解决冲突后执行git add . && git rebase --continue，然后再重新执行命令')


def merge(branch, need_push=True, need_pull=True):
    """
    将branch合并到当前分支
    :param need_pull:
    :param need_push:
    :param branch:
    :return:
    """
    # 从远程仓库拉最新代码
    if need_pull:
        pull()

    # 合并(git合并冲突信息在stdout中)
    ihelper.execute('git merge --no-ff ' + branch)
    if workspace_status() & iglobal.GIT_CONFLICT:
        ihelper.execute('git status -s')
        raise exception.FlowException(u'合并失败：发生冲突。请手工解决冲突后执行git add . && git commit，然后重新执行命令')

    # 推送到远程仓库
    if need_push:
        ihelper.execute('git push')


def project_branches(prefix=None, project=None, only_this_sprint=True):
    """
    获取项目下的所有符合prefix前缀的本地分支列表
    :param str project: 项目名
    :param str prefix: 前缀
    :param bool only_this_sprint:是否限制在本迭代
    :return: list
    """
    if not project:
        project = iglobal.PROJECT

    old_project = iglobal.PROJECT

    # 进入该项目目录
    if project != iglobal.PROJECT:
        command.Extra('cd', [project], log=False).execute()

    if prefix and only_this_sprint:
        prefix = '%s/%s' % (prefix.rstrip('/'), iglobal.SPRINT)

    branches = local_branches()

    if prefix:
        branches = filter(lambda x:str(x).startswith(prefix), branches)

    # 切换回原来的项目
    if iglobal.PROJECT != old_project:
        command.Extra('cd', [old_project], log=False).execute()

    return branches


def sync(project, prefix=None, only_this_sprint=True, deep=False):
    """
    同步本地和远程分支
    (未完成)
    :param bool deep: 是否深层合并，只有深层合并才会同步本地和远程都存在的分支，否则只是创建本地没有的分支和推远程没有的分支
    :param project:
    :param prefix:
    :param only_this_sprint:
    :return:
    """
    iglobal.SILENCE = True
    old_project = iglobal.PROJECT

    try:
        # 进入该项目目录
        if project != iglobal.PROJECT:
            command.Extra('cd', [project], log=False).execute()

        if prefix and only_this_sprint:
            prefix = '%s/%s' % (prefix.rstrip('/'), iglobal.SPRINT)

        # remote_branches里面已经执行了git fetch了，此处就不再执行了
        l_brs = local_branches()
        r_brs = remote_branches()

        if prefix:
            l_brs = filter(lambda x:str(x).startswith(prefix), l_brs)
            r_brs = filter(lambda x:str(x).startswith(prefix), r_brs)

        local_only = list(set(l_brs).difference(set(r_brs)))
        remote_only = list(set(r_brs).difference(set(l_brs)))
        the_same = list(set(l_brs).intersection(set(r_brs)))

        # 仅在本地存在的，推到远程去
        for l_o_br in local_only:
            ihelper.execute('git push -u origin %s:%s' % (l_o_br, l_o_br))

        # 仅远程存在的，创建本地相关分支
        for r_o_br in remote_only:
            ihelper.execute('git branch %s origin/%s' % (r_o_br, r_o_br))

        # 两边都存在的，同步
        if the_same and deep:
            raise Exception(u'暂未实现')

        if old_project != iglobal.PROJECT:
            command.Extra('cd', [old_project], log=False).execute()
    finally:
        iglobal.SILENCE = False


def tag_name(tag_type='main'):
    if tag_type == 'main':
        # 主版本标签
        return 'v%s.00' % iglobal.SPRINT
    else:
        # 获取最近的tag
        year = time.strftime('%y')
        years = [year, int(year) - 1]
        partten1 = 'v%s*.*' % years[0]
        partten2 = 'v%s*.*' % years[1]
        tag = ihelper.execute('git tag -l "%s" "%s" --sort "version:refname"' % (partten1, partten2), print_out=False, return_result=True).splitlines()
        tag = tag.pop() if tag else None
        if tag:
            tag = tag.split('.')
            tag = '%s.%02d' % (tag[0], int(tag[1]) + 1)

        return tag


def sub_cmd_list():
    """
    获取git二级指令列表
    :return: list
    """
    global __sub_cmd_list

    if __sub_cmd_list:
        return __sub_cmd_list

    git_help = ihelper.popen('git help -a').splitlines()
    lst = []
    flag = False
    for line in git_help:
        if not line:
            continue

        if not flag and line.startswith('available git commands'):
            flag = True
            continue
        elif flag and line.startswith('git commands available from elsewhere'):
            break

        if flag:
            lst += filter(lambda x:x, line.split(' '))

    __sub_cmd_list = lst

    return lst


def check_tag_format(tag):
    """
    暂仅作宽松校验
    :param tag:
    :return:
    """
    return re.compile('^v.*\..*').match(tag)


def check_workspace_health():
    """
    检查工作区是否健康：是否处于conflict、rebasing状态
    :return:
    """
    status = workspace_status()

    if status & iglobal.GIT_CONFLICT:
        if status & iglobal.GIT_REBASING:
            warn(u'rebase出现冲突。请手工解决冲突后执行 git add . && git rebase --continue 继续完成操作。或者执行 git rebase --abort取消操作')
        elif status & iglobal.GIT_CHERRING:
            warn(u'cherry-pick出现冲突。请手工解决冲突后执行 git add . && git cherry-pick --continue 继续完成操作。或者执行git cherry-pick --abort取消操作')
        elif status & iglobal.GIT_MERGING:
            warn(u'merge出现冲突。请手工解决冲突后执行 git add . && git commit 完成合并操作。或者执行 git merge --abort取消操作')
        else:
            warn(u'当前工作区存在冲突，请手工处理冲突后执行 git add . && git commit 解决冲突')
    elif status & iglobal.GIT_REBASING:
        warn(u'工作区正处于rebasing中，请执行 git rebase --continue 完成操作')
    elif status & iglobal.GIT_CHERRING:
        warn(u'工作区正处于cherry picking中，请执行 git cherry-pick --continue 完成操作')
    elif status & iglobal.GIT_MERGING:
        warn(u'工作区正处于merging中，请执行 git commit 完成操作')
    elif ihelper.read_runtime('publish_branches'):
        warn(u'上次发布尚未完成，请解决冲突后执行 ft p --continue 继续完成发布。或者执行 ft p --abort 结束该发布')

