# coding:utf-8

import os
import subprocess
import iconfig
import isprint
import ihelper
import iglobal
import exception


def get_config(key=None):
    """
    获取git配置列表
    :param key:
    :return:
    """
    config = dict(map(lambda x:x.split('='), os.popen('git config -l').read().splitlines()))
    return config[key] if key and config.has_key(key) else config


def current_branch():
    """
    获取当前分支
    :return:
    """
    branch = filter(lambda x:x.find('*') != -1, os.popen('git branch').read().splitlines())
    return branch[0].replace('*', '').strip() if branch else None


def local_branches():
    """
    所有的本地分支列表
    """
    return map(lambda x:str(x).lstrip('*').strip(), os.popen('git branch').read().splitlines())


def remote_branches(refresh=True):
    """
    远程分支列表
    :param refresh:
    """
    # 先拉一下最新的远程分支
    if refresh:
        ihelper.execute('git stash', print_out=False)
        ihelper.execute('git pull --rebase', print_out=False)
        ihelper.execute('git stash pop', print_out=False)

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

    out = ihelper.execute('git branch', print_out=False, return_result=True)
    if out.find('Not a git repository') != -1:
        result = False

    os.chdir(curr_dir)

    return result


def workspace_is_clean():
    """
    检查当前分支的工作区(包括暂存区)是否是清洁的
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
        return config[prefix + '_prefix'] + ('/' + ihelper.read_runtime('sprint') if prefix == 'feature' else '') + '/' + branch[0]


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

    out = os.popen('git status').read()

    if out.find('working directory clean') != -1:
        __status |= iglobal.GIT_CLEAN
    if out.find('Unmerged paths') != -1:
        __status |= iglobal.GIT_CONFLICT
    if out.find('Changes to be committed') != -1:
        __status |= iglobal.GIT_UNCOMMITED
    if out.find('Changes not staged for commit') != -1:
        __status |= iglobal.GIT_UNSTAGED
    if out.find('branch is ahead of') != -1:
        __status |= iglobal.GIT_AHEAD
    if out.find('branch is behind of') != -1:
        __status |= iglobal.GIT_BEHIND

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

def push(branch):
    """
    将当前分支推到远程仓库
    :param branch:
    :return:
    """
    if not branch:
        return

    # 先拉远程分支(如果报错则需要手工处理)
    ihelper.execute('git pull --rebase', raise_err=True)
    # push
    ihelper.execute('git push origin ' + branch + ':' + branch)


def merge(branch, push=True):
    """
    将branch合并到当前分支
    :param push:
    :param branch:
    :return:
    """
    # 从远程仓库拉最新代码
    ihelper.execute('git pull --rebase', raise_err=True)

    # 合并(git合并冲突信息在stdout中)
    ihelper.execute('git merge --no-ff ' + branch)
    if workspace_status() & iglobal.GIT_CONFLICT:
        ihelper.execute('git status -s')
        raise exception.FlowException(u'合并失败：发生冲突。请手工解决冲突后用git add . && git commit && git push手工提交')

    # 推送到远程仓库
    ihelper.execute('git push')

