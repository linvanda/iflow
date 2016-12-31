# coding:utf-8

import os
import ConfigParser
import re
import isprint
import ihelper
import iconfig
import exception
import iglobal
from command import Command
import iprint


class Extra(Command):
    def execute(self):
        try:
            eval('self.' + self.cmd)()
        except exception.FlowException, e:
            raise Exception(unicode(str(e), 'utf-8'))
        except Exception, e:
            raise Exception(e.message)

    def sprint(self):
        """
        切换到某个迭代
        """
        sprint = isprint.get_sprint(None if not self.args else self.args[0])
        if not sprint:
            raise exception.FlowException(u'版本号格式错误')

        iglobal.SPRINT = sprint
        ihelper.write_runtime('sprint', sprint)

    def cd(self):
        """
        进入项目目录
        """
        if not self.args:
            raise exception.FlowException(u'指令格式不正确，请键入help查看该指令使用方式')

        proj_name = self.args[0]
        proj = iconfig.read_config('project', proj_name)

        if not proj or not proj.has_key('dir'):
            raise exception.FlowException(u'未配置项目' + proj_name + u'信息，请进入config/project.json中正确配置')

        if not os.path.isdir(proj['dir']):
            raise exception.FlowException(u'该项目git根目录配置不正确，请进入config/project.json中正确配置')

        iglobal.PROJECT = proj_name
        ihelper.write_runtime('project', proj_name)
        os.chdir(proj['dir'])

    @staticmethod
    def pwd():
        print os.getcwd()

    @staticmethod
    def version():
        cfg = iconfig.read_config('system')
        print cfg['name'] + ' ' + cfg['version']

    def help(self):
        cmd = self.args[0] if self.args else None
        cmd = cmd and Command.real_cmd(cmd)

        cf = ConfigParser.ConfigParser()
        cf.read(iglobal.BASE_DIR + '/config/help.conf')

        for sec in cf.sections():
            if sec and (not cmd or cmd == sec):
                iprint.yellow(unicode(cf.get(sec, 'title'), 'utf-8'), True)
                print unicode(cf.get(sec, 'content'), 'utf-8')
                print

    @staticmethod
    def alias():
        cfg = iconfig.read_config('system', 'alias')
        arr = []
        for key, val in cfg.items():
            if key != val:
                print "%3s%12s"%(key, val)






