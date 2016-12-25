# coding:utf-8
# 入口

import subprocess
import sys
import iconfig
import ihelper
import command
from iprint import *
import time
import signal

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    cfg = iconfig.read_config('system')
    proj_cfg = iconfig.read_config('project')

    blue(u'=========================***=========================', True)
    blue(cfg['name'], True)
    blue(u'版本:' + cfg['version'], True)
    blue(u'作者:' + cfg['author'], True)
    blue(cfg['desc'], True)
    blue(u'=========================***=========================', True)

    try:
        ihelper.init_check()
    except Exception, e:
        ihelper.error_exit(unicode(str(e), 'utf-8'))

    # 检查是否设置了迭代号，如果没有设置，或者迭代号过期了，则提示设置
    try:
        ihelper.check_sprint()
    except Exception, e:
        warn(unicode(str(e), 'utf-8'))

    # 中断处理
    def ctr_c_handler(*args):
        ihelper.goodbye()

    signal.signal(signal.SIGINT, ctr_c_handler)

    while True:
        try:
            cmd = raw_input('').strip().lower()

            if cmd == 'exit':
                ihelper.goodbye()

            cmd = cmd.split(' ')
            print cmd
        except Exception, e:
            ihelper.goodbye(str(e))















p = subprocess.Popen('git var', stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

raw_input()