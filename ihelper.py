# coding:utf-8
# 该模块提供一些助手方法

import subprocess
import time
import os
import iconfig
import isprint
import iglobal
import igit
import exception
from iprint import *


def goodbye(*args):
    print args[0] if args and args[0] else "good bye!"
    # time.sleep(1)
    sys.exit(0)


def error_exit(msg):
    error(msg)
    raw_input()
    sys.exit(1)


def required_check():
    """
    必须进行的检查
    """
    # 检查project.json有没有配置以及路径是否正确
    proj_cfg = iconfig.read_config('project', use_cache=False)
    if not proj_cfg:
        raise Exception(u'请配置项目信息(config/project.json文件，具体格式参见readme.md文件)')

    curr_dir = os.getcwd()
    for proj_name, info in proj_cfg.items():
        if not info['dir'] or not os.path.exists(info['dir']) or not os.path.isdir(info['dir']):
            raise Exception(u'项目' + proj_name + u'的目录配置不正确')
        # 检测目录是否有效的git仓库
        os.chdir(info['dir'])
        proccess = subprocess.Popen('git branch', stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        err = proccess.stderr.read()
        if err and err.find('Not a git repository') != -1:
            raise Exception(u'目录' + info['dir'] + '不是有效的git仓库')

    os.chdir(curr_dir)

    # 版本号检测
    return isprint.check_sprint()


def init():
    """
    初始化
    """
    # 进入项目目录
    proj = read_runtime('project')
    if proj:
        pinfo = iconfig.read_config('project', proj)
        if pinfo.has_key('dir'):
            os.chdir(pinfo['dir'])


def write_runtime(key, val):
    """
    写入运行时信息
    """
    if not key and not val:
        return True

    info = iconfig.read_config(iglobal.BASE_DIR + '/runtime')
    info[key] = val
    iconfig.write_config(iglobal.BASE_DIR + '/runtime', info)

    return True


def read_runtime(key = None):
    """
    读取运行时信息
    """
    info = iconfig.read_config(iglobal.BASE_DIR + '/runtime', use_cache=False)

    if key:
        return info[key] if info.has_key(key) else None
    else:
        return info


def headline():
    """
    页眉：linvanda@1612s1/vmember/master
    """
    username = igit.get_config('user.name') or 'nobody'
    sprint = read_runtime('sprint') or 'none'
    project = read_runtime('project') or 'global'
    real_path = os.getcwd() if project == 'global' else iconfig.read_config('project', project)['dir']
    branch = igit.get_current_branch() if project != 'global' else None

    pink(username), sky_blue( '@'), green(sprint), sky_blue('/'), yellow(project + '(' + real_path + ')')
    if branch:
        sky_blue('/' + branch)
    print 


def execute(cmd, print_out=True, raise_err=False):
    # 不关心异常且需要输出时，直接调用os.system
    if print_out and not raise_err:
        return os.system(cmd)
    else:
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        err = p.stderr.read()
        out = p.stdout.read()

        if err:
            if raise_err:
                # 将错误抛出由外界处理
                raise exception.FlowException(err)
            else:
                out = err

        if print_out:
            print out

        return p


def log(msg, type='cmd'):
    file_name = iglobal.BASE_DIR + '/log/' + type + '-' + time.strftime('%Y%m') +  '.log'
    f = open(file_name, 'a')
    f.write(msg + "\n")
    f.close()

