# coding:utf-8

import os
import subprocess
import iconfig
import isprint
import ihelper
import iglobal


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
        os.popen('git stash')
        os.popen('git pull --rebase')
        os.popen('git stash pop')

    return map(lambda x:str(x).replace('origin/HEAD -> ', '').replace('origin/', '').strip(),
               os.popen('git branch -r').read().splitlines())


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

    process = subprocess.Popen('git branch', stderr=subprocess.PIPE,stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    err = process.stderr.read()
    if err and err.find('Not a git repository') != -1:
        result = False

    os.chdir(curr_dir)

    return result


def workspace_is_clean():
    """
    检查当前分支的工作区(包括暂存区)是否是清洁的
    """
    return workspace_status() == iglobal.GIT_CLEAN


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
        if proj_cfg.has_key('branch') and list(proj_cfg['branch']).has_key('product'):
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
        if proj_cfg.has_key('branch') and list(proj_cfg['branch']).has_key('test'):
            return proj_cfg['branch']['test']

    config = iconfig.read_config('system', 'branch')
    if config.has_key('test'):
        return config['test']
    else:
        return 'sp-dev'


def comment(msg, btype=None):
    return '<' + btype + '>' + msg if btype else msg


def workspace_status():
    """
    工作空间状态
    :return:
    """
    out = os.popen('git status').read()
    if out.find('working directory clean') != -1:
        return iglobal.GIT_WORKSPACE_CLEAN
    elif out.find('Unmerged paths') != -1:
        return iglobal.GIT_WORKSPACE_CONFLICT
    elif out.find('Changes to be committed') != -1:
        return iglobal.GIT_UNCOMMITED
    elif out.find('Changes not staged for commit'):
        return iglobal.GIT_UNSTAGED


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

    # 合并
    ihelper.execute('git merge --no-ff ' + branch, raise_err=True)

    # 推送到远程仓库
    ihelper.execute('git push')

