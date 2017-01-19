# coding:utf-8

import os
import isprint
import ihelper
import iconfig
import exception
import iglobal
from command import Command
import iprint
import icommand
import igit
import exception


class Extra(Command):
    def execute(self):
        try:
            eval('self.' + self.cmd)(list(self.args))
        except exception.FlowException, e:
            raise Exception(unicode(str(e), 'utf-8'))
        except Exception, e:
            raise Exception(e.message)

    @staticmethod
    def sprint(args):
        """
        切换到某个迭代
        :param args:
        """
        sprint = isprint.get_sprint(None if not args else args[0])
        if not sprint:
            raise exception.FlowException(u'版本号格式错误')

        iglobal.SPRINT = sprint
        ihelper.write_runtime('sprint', sprint)

    @staticmethod
    def cd(args):
        """
        进入项目目录
        :param args:
        """
        if not args:
            raise exception.FlowException(u'指令格式不正确，请键入help查看该指令使用方式')

        proj_name = args[0]
        proj = iconfig.read_config('project', proj_name)

        if not proj or not proj.has_key('dir'):
            raise exception.FlowException(u'未配置项目' + proj_name + u'信息，请进入config/project.json中正确配置')

        if not os.path.isdir(proj['dir']):
            raise exception.FlowException(u'该项目git根目录配置不正确，请进入config/project.json中正确配置')

        iglobal.PROJECT = proj_name
        ihelper.write_runtime('project', proj_name)
        os.chdir(proj['dir'])

    @staticmethod
    def pwd(args=None):
        print os.getcwd()

    @staticmethod
    def help(args):
        cmd = args[0] if args else None
        cmd = cmd and icommand.real_cmd(cmd)

        import readme

        helps = readme.help
        if cmd:
            the_one = helps[cmd] if cmd in helps else None
            if not the_one:
                return
            if isinstance(the_one, str) and the_one in helps:
                the_one = helps[the_one]

            if isinstance(the_one, dict):
                helps = {cmd: the_one}

        for key, info in helps.items():
            if isinstance(info, str):
                continue
            iprint.yellow(info['title'], True)
            if 'desc' in info:
                iprint.sky_blue(info['desc'], True)
            iprint.info(info['content'])
            print

    @staticmethod
    def alias(args=None):
        cfg = iconfig.read_config('system', 'alias')
        arr = []
        for key, val in cfg.items():
            if key != val:
                print "%3s%12s"%(key, val)

    @staticmethod
    def exit(args=None):
        ihelper.goodbye()

    @staticmethod
    def sql(args=None):
        """
        获取项目下面的所有sql
        :param args:
        :return:
        """
        dirs = []
        old_proj = iglobal.PROJECT
        for proj, info in iconfig.read_config('project').items():
            if 'ignore_sql_file' in info and info['ignore_sql_file']:
                continue

            # 需要先将项目切换到相应的分支
            sql_branch = info['branch']['sql_branch'] if 'sql_branch' in info['branch'] else iconfig.read_config('system', 'branch')['sql_branch']

            # 进入项目
            if iglobal.PROJECT != proj:
                Extra.cd([proj])

            curr_branch = igit.current_branch()
            if curr_branch != sql_branch:
                if not igit.workspace_is_clean():
                    raise exception.FlowException(u'项目的工作空间有尚未保存的修改，请先执行git commit提交或git reset --hard丢弃。处理后请再次执行sql指令')
                # 切换分支
                ihelper.system('git checkout %s' % sql_branch)

            # 拉取
            igit.pull()

            base_dir = info['dir']

            if 'sql_dir' in info:
                rel_dir = info['sql_dir']
            else:
                rel_dir = iconfig.read_config('system', 'sql_dir')

            dirs.append((proj, ihelper.real_path(str(base_dir).rstrip('/') + '/' + rel_dir)))

        if iglobal.PROJECT != old_proj:
            Extra.cd([old_proj])

        sql_file_suffixes = [ele.lstrip('.') for ele in str(iconfig.read_config('system', 'sql_file_suffix')).split('|')]

        if not dirs:
            return

        files = []
        for proj, sql_path in dirs:
            if not sql_path or not os.path.exists(sql_path):
                continue

            # 获取文件夹下所有的sql文件
            for f in os.listdir(sql_path):
                f = sql_path + f
                if not os.path.isfile(f):
                    continue

                if f.split('.')[-1] in sql_file_suffixes:
                    files.append(f)

        if not files:
            iprint.info(u'本次迭代没有sql需要执行')
            return

        # 排序
        def __isort(x, y):
            """
            :type x: str
            :type y: str
            :return:
            """
            sp_date = isprint.get_date_from_sprint(iglobal.SPRINT).split('-')
            year = sp_date[0]
            month = sp_date[1]

            x = os.path.basename(x)
            y = os.path.basename(y)

            if month == '12' and x.startswith('01'):
                x = str(int(year) + 1) + x
            else:
                x = year + x

            if month == '12' and y.startswith('01'):
                y = str(int(year) + 1) + y
            else:
                y = year + y

            if x < y:
                return -1

            return 1 if x > y else 0

        files.sort(__isort)

        print
        iprint.warn(u'以下sql需要发布：')
        for f in files:
            iprint.info('  ' + os.path.basename(f))
        print

        out_file = iglobal.BASE_DIR + '/runtime/' + iglobal.SPRINT + '.sql'
        if ihelper.confirm(u'是否导出sql？') == 'y':
            out_handler = open(out_file, 'w')
            out_handler.write('set names utf8;\n')
            for f_name in files:
                f_handler = open(f_name, 'r')
                out_handler.write('\n\n-- ----------------------------------- %s -----------------------------------\n' % os.path.basename(f_name))
                out_handler.write(f_handler.read())
                f_handler.close()
            out_handler.close()
            print
            iprint.ok(u'已写入到%s中' % out_file)
        else:
            return









