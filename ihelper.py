# coding:utf-8
# 该模块提供一些助手方法

import subprocess
import platform
import os
import iconfig
import isprint
import igit
import exception
import iprint
import sys
import iglobal
try:
    import readline
except ImportError:
    import pyreadline as readline

def goodbye(*args):
    print args[0] if args and args[0] else "good bye!"
    sys.exit(0)


def error_exit(msg):
    iprint.error(msg)
    raw_input()
    sys.exit(1)


def disable_readline():
    iglobal.READLINE = False


def enable_readline():
    iglobal.READLINE = True


def required_check():
    """
    必须进行的检查
    """
    iprint.info(u'正在进行工作环境检查...')

    # 检查project.json有没有配置以及路径是否正确
    proj_cfg = iconfig.read_config('project', use_cache=False)
    if not proj_cfg:
        raise Exception(u'请配置项目信息(config/project.json文件，具体格式参见readme.md文件)')

    for proj_name, info in proj_cfg.items():
        if proj_name == 'global':
            raise Exception(u'项目名称不能叫global，请使用别的名称')

        if not info['dir'] or not os.path.exists(info['dir']) or not os.path.isdir(info['dir']):
            raise Exception(u'项目' + proj_name + u'的目录配置不正确')

        # 检测目录是否有效的git仓库
        if not igit.dir_is_repository(info['dir']):
            raise Exception(u'目录' + info['dir'] + u'不是有效的git仓库')

    # 版本号检测
    return isprint.check_sprint()


def init():
    """
    初始化
    """
    # 检查必要目录
    check_dir()

    # 进入项目目录
    proj = read_runtime('project')
    iglobal.PROJECT = proj or 'global'

    if proj:
        pinfo = iconfig.read_config('project', proj)
        if pinfo.has_key('dir'):
            os.chdir(pinfo['dir'])

    iglobal.SPRINT = read_runtime('sprint') or 'none'

    # 设置Git参数
    execute('git config --global push.default simple')


def check_dir():
    runtime_dir = iglobal.BASE_DIR + '/runtime/'
    config_dir = iglobal.BASE_DIR + '/config/'
    log_dir = iglobal.BASE_DIR + '/log/'
    config_file = config_dir + 'system.json'
    project_file = config_dir + 'project.json'

    if not os.path.exists(config_dir):
        raise exception.FlowException(u'目录缺失：%s' % config_dir)
    if not os.path.exists(config_file):
        raise exception.FlowException(u'文件缺失：%s' % config_file)
    if not os.path.exists(project_file):
        raise exception.FlowException(u'文件缺失：%s' % project_file)
    if not os.path.isdir(runtime_dir):
        os.mkdir(runtime_dir)
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    return True

def write_runtime(key, val=None):
    """
    写入运行时信息
    :param val:
    :param key:
    """
    if not key and not val:
        return True

    info = iconfig.read_config(iglobal.BASE_DIR + '/runtime')

    if val:
        info[key] = val
    else:
        info.has_key(key) and info.pop(key)

    iconfig.write_config(iglobal.BASE_DIR + '/runtime', info)

    return True


def read_runtime(key=None):
    """
    读取运行时信息
    :param key:
    """
    info = iconfig.read_config(iglobal.BASE_DIR + '/runtime', use_cache=False)

    if key:
        return info[key] if info.has_key(key) else None
    else:
        return info


def system_type():
    """
    操作系统类型
    :return:
    """
    stype = platform.system()

    if stype == 'Windows':
        return iglobal.PLATFORM_WINDOWS

    if stype == 'Linux':
        return iglobal.PLATFORM_LINUX

    return None


def headline():
    """
    页眉
    """
    print
    project = iglobal.PROJECT
    curr_proj_info = iconfig.read_config('project', project)
    branch = igit.current_branch() if project != 'global' else None
    real_path = os.getcwd() if (project == 'global'
                                or not project
                                or not curr_proj_info
                                or not curr_proj_info.has_key('dir')) \
        else curr_proj_info['dir']

    if real_path.count('/') > 2:
        path_arr = real_path.split('/')
        real_path = '/'.join([path_arr[0], path_arr[1], '...', path_arr[len(path_arr) - 1]])

    iprint.green(iglobal.SPRINT), iprint.sky_blue('/'), iprint.yellow(project + '(' +  real_path + ')')
    if branch:
        status = igit.workspace_status(text=True)
        iprint.sky_blue('[ ' + branch + ('(' + status + ')' if status else '') + ' ]')
    print
    sys.stdout.flush()


def popen(cmd):
    return execute(cmd, print_out=False, return_result=True)


def system(cmd):
    execute(cmd)


def execute(cmd, print_out=True, raise_err=False, return_result=False):
    # 不关心异常且需要输出且不需要返回时，直接调用os.system
    if print_out and not raise_err and not return_result:
        if iglobal.SILENCE:
            p = os.popen(cmd)
            out = p.read()
            p.close()
            return out
        else:
            sys.stdout.flush()
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
                out = err + out

        if print_out and not iglobal.SILENCE:
            print out

        del p

        return out


def confirm(ask_msg,default='y', tick=0):
    if not ask_msg:
        return 'cancel'

    disable_readline()

    n = 0
    choice = ['y', 'n', 'c']
    map = {'yes':'y', 'no':'n', 'cancel':'c'}
    result = 'c'
    while not tick or n < tick:
        n += 1
        c = raw_input('%s(Yes|No|Cancel)[%s]: ' % (ask_msg.decode('utf-8').encode(iglobal.FROM_ENCODING), default)).strip().lower()
        if not c:
            result = default
            break

        if map.has_key(c):
            c = map[c]

        if c in choice:
            result = c
            break

    enable_readline()

    return result


def projects():
    """
    项目名称列表
    :return:
    """
    return dict(iconfig.read_config('project')).keys()


def real_path(path):
    """
    :type path: str
    """
    if not path:
        return None

    return path.replace('{sprint}', iglobal.SPRINT).replace('\\', '/').rstrip('/') + '/'



