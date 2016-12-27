# coding:utf-8
# 入口

import subprocess
import signal
import os
import iconfig
import ihelper
import command
from iprint import *
import iglobal

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    iglobal.BASE_DIR = os.getcwd()

    cfg = iconfig.read_config('system')
    proj_cfg = iconfig.read_config('project')

    blue(u'=========================***=========================', True)
    blue(cfg['name'], True)
    blue(u'版本:' + cfg['version'], True)
    blue(u'作者:' + cfg['author'], True)
    blue(cfg['desc'], True)
    blue(u'=========================***=========================', True)

    # 必须项检测
    checked_ok = False
    try:
        ihelper.required_check()
        checked_ok = True
    except Exception, e:
        ihelper.warn(unicode(str(e), 'utf-8'))

    # 中断处理
    def ctr_c_handler(*args):
        print

    signal.signal(signal.SIGINT, ctr_c_handler)

    while True:
        ihelper.headline()
        try:
            args = raw_input('$ ').strip().lower()

            if args == 'exit':
                ihelper.goodbye()

            args = [ele for ele in args.split(' ') if ele.strip()]

            if args:
                main_cmd = command.Command.real_cmd(args.pop(0))
                if cfg['cmd_cls'].has_key(main_cmd):
                    # 执行具体的指令
                    try:
                        eval('command.' + cfg['cmd_cls'][main_cmd])(main_cmd, args).execute()
                    except Exception, e:
                        error(unicode(str(e), 'utf-8'))
                else:
                    white(u'无效的指令', True)

            # 每次命令执行后都检查一下必须项是否正确
            if not checked_ok:
                try:
                    ihelper.required_check()
                    checked_ok = True
                except Exception, e:
                    ihelper.warn(unicode(str(e), 'utf-8'))
        except Exception, e:
            continue
