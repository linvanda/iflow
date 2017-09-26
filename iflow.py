# coding:utf-8
# 入口

import os
import traceback
import iconfig
import ihelper
import command
from iprint import *
import iglobal
import igit
import icompleter
import icommand
import exception


reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    iglobal.BASE_DIR = os.getcwd().replace('\\', '/')

    # git检测
    if not ihelper.has_git():
        ihelper.show_error_and_exit(u'未找到git。请将git路径设置到系统PATH中')

    # 初始化
    try:
        ihelper.init()
    except exception.FlowException, e:
        ihelper.show_error_and_exit(e.message)

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
            # 必须项是否正确（此处为条件检查，因此种检查比较耗时）
            if not checked_ok:
                try:
                    ihelper.required_check()
                    checked_ok = True
                except Exception, e:
                    warn(unicode(traceback.format_exc(), 'utf-8'))

            if iglobal.PROJECT != 'global':
                # 检查工作区状态是否健康
                igit.check_workspace_health()
                # 检查生产分支更新情况
                igit.check_product_branch_has_new_update()

            args = raw_input('$ ').strip().replace('\n', '').decode(iglobal.FROM_ENCODING).encode('utf-8')
            args = [ele for ele in args.split(' ') if ele.strip()]

            if args:
                # 执行具体的指令
                try:
                    main_cmd = icommand.real_cmd(args.pop(0))
                    eval('command.' + cfg['cmd_cls'][main_cmd])(main_cmd, args).execute()
                except Exception, e:
                    error(unicode(traceback.format_exc(), 'utf-8'))
        except KeyboardInterrupt:
            print
        except exception.FlowException, e:
            print traceback.format_exc()
        except Exception, e:
            ihelper.show_error_and_exit(traceback.format_exc())
