# coding:utf-8
# 入口

import os
import time
import iconfig
import ihelper
import command
from iprint import *
import iglobal
import igit
import icompleter
import icommand
import exception

#目前仅支持windows系统
if ihelper.system_type() != iglobal.PLATFORM_WINDOWS:
    error(u'仅支持windows操作系统')
    time.sleep(5)
    sys.exit(0)

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    iglobal.BASE_DIR = os.getcwd().replace('\\', '/')

    # 初始化
    try:
        ihelper.init()
    except exception.FlowException, e:
        print e.message.decode('utf-8').encode(iglobal.FROM_ENCODING)
        raw_input()

    cfg = iconfig.read_config('system')

    # 操作系统命令行编码
    if 'console_encoding' in cfg:
        iglobal.FROM_ENCODING = cfg['console_encoding']

    blue(u'=========================***=========================', True)
    blue(cfg['name'], True)
    blue(u'作者:' + cfg['author'], True)
    blue(cfg['desc'], True)
    blue(cfg['more_info'], True)
    blue(u'=========================***=========================', True)

    # tab键自动补全
    icompleter.tab()

    checked_ok = False

    while True:
        try:
            ihelper.headline()
            # 必须项是否正确（此处为条件检查，因此种检查比较耗时可能）
            if not checked_ok:
                try:
                    ihelper.required_check()
                    checked_ok = True
                except Exception, e:
                    ihelper.warn(unicode(str(e), 'utf-8'))

            # 检查工作区状态是否健康
            if iglobal.PROJECT != 'global' and igit.dir_is_repository():
                igit.check_workspace_health()

            args = raw_input('$ ').strip().lower().decode(iglobal.FROM_ENCODING).encode('utf-8')
            args = [ele for ele in args.split(' ') if ele.strip()]

            if args:
                # 执行具体的指令
                try:
                    main_cmd = icommand.real_cmd(args.pop(0))
                    eval('command.' + cfg['cmd_cls'][main_cmd])(main_cmd, args).execute()
                except Exception, e:
                    error(unicode(str(e), 'utf-8'))
        except KeyboardInterrupt:
            print
        except exception.FlowException, e:
            print e
