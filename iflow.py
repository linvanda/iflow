# coding:utf-8
# 入口

import signal
import os
import sys
import iconfig
import ihelper
import command
from iprint import *
import iglobal
import igit
import icompleter

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    iglobal.BASE_DIR = os.getcwd().replace('\\', '/')

    # tab键自动补全
    icompleter.tab()

    cfg = iconfig.read_config('system')

    blue(u'=========================***=========================', True)
    blue(cfg['name'], True)
    blue(u'版本:' + cfg['version'], True)
    blue(u'作者:' + cfg['author'], True)
    blue(cfg['desc'], True)
    blue(u'=========================***=========================', True)

    # 初始化
    ihelper.init()

    checked_ok = False

    while True:
        ihelper.headline()
        try:
            # 必须项是否正确（此处为条件检查，因此种检查比较耗时可能）
            if not checked_ok:
                try:
                    ihelper.required_check()
                    checked_ok = True
                except Exception, e:
                    ihelper.warn(unicode(str(e), 'utf-8'))

            # 检查工作区状态是否健康
            igit.check_workspace_health()

            args = raw_input('$ ').strip().lower().decode(iglobal.FROM_ENCODING).encode('utf-8')
            args = [ele for ele in args.split(' ') if ele.strip()]

            if args:
                # 执行具体的指令
                try:
                    main_cmd = command.Command.real_cmd(args.pop(0))
                    eval('command.' + cfg['cmd_cls'][main_cmd])(main_cmd, args).execute()
                except Exception, e:
                    error(unicode(str(e), 'utf-8'))
        except KeyboardInterrupt:
            print
        except Exception, e:
            print e
