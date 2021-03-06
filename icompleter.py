# coding:utf-8
"""
自动补全
"""
import command
import iconfig
import igit
import iglobal
import ihelper
import isprint
import re
import atexit
import icommand

try:
    import readline
except ImportError:
    import pyreadline as readline

__all__ = ["Completer"]

__histfile = None

class Completer:
    def __init__(self):
        self.matches = []
        global __histfile

        __histfile = iglobal.BASE_DIR + '/' + 'log/cmd.log'

        readline.rl.allow_ctrl_c = False
        readline.rl.prompt_color = 2
        readline.rl.set_history_length(100)
        readline.rl.console.title('iflow')
        readline.rl.command_color = 7

        try:
            readline.read_history_file(__histfile)
        except IOError:
            pass

        atexit.register(readline.write_history_file, __histfile)


    def complete(self, text, state):
        if not iglobal.READLINE:
            return None

        if state == 0:
            self.matches = self.match(text)
        try:
            return self.matches[state] if isinstance(self.matches, list) else None
        except IndexError:
            return None


    def match(self, text):
        """
        一级指令 二级指令 参数1 参数2 ...
        :type text: str
        :return:
        """
        line = re.compile('\s+').sub(' ', readline.get_line_buffer())
        line_words = line.split(' ')

        if len(line_words) == 1:
            return self.top_cmd(text)
        else:
            cls = iconfig.read_config('system', 'cmd_cls')
            cmd = icommand.real_cmd(line_words[0], raise_err=False)

            if not cmd:
                return None

            return eval('self.match_%s' % str(cls[cmd]).lower())(text, line_words)


    def match_git(self, text, line_words):
        top_cmd = icommand.real_cmd(line_words[0], raise_err=False)

        if top_cmd in ['delete', 'commit'] and text.startswith('-'):
            return self.match_parameter(top_cmd, command.Git.parameters, text)
        elif top_cmd in ['delete', 'rename']:
            return self.match_branch(None, text)
        elif top_cmd == 'git':
            if not text:
                return None
            elif len(line_words) > 2:
                return self.match_branch(None, text)
            else:
                return [ele + ' ' for ele in iconfig.read_config('system', 'git_common_cmds') if ele.startswith(text)] \
                or [ele + ' ' for ele in igit.sub_cmd_list() if ele.startswith(text)]

        return None


    def match_transform(self, text, line_words):
        if text.startswith('-'):
            return self.match_parameter(None, command.Transform.parameters, text)
        else:
            branch_cfg = iconfig.read_config('system', 'branch')

            prefix = branch_cfg['feature_prefix'] if line_words[0].startswith('f') else branch_cfg['hotfix_prefix']
            if prefix == branch_cfg['feature_prefix']:
                prefix += '/' + iglobal.SPRINT
            return self.match_branch(prefix, text)


    def match_extra(self,text=None, line_words=None):
        if len(line_words) == 1:
            return self.top_cmd(text)

        top_cmd = icommand.real_cmd(line_words[0], raise_err=False)

        if not top_cmd:
            return None

        if top_cmd == 'cd':
            projects = ihelper.projects()
            if not text:
                return projects
            else:
                return filter(lambda x: x.startswith(text), projects)
        elif top_cmd == 'help':
            return [ele for ele in self.top_cmd(text) if ele != 'help']
        elif top_cmd == 'sprint':
            return [isprint.next_sprint()]
        else:
            return None


    def match_develop(self,text, line_words):
        if len(line_words) == 1:
            return self.top_cmd(text)
        elif len(line_words) == 2:
            # 二级指令
            matches = None
            if not line_words[1].startswith('-'):
                matches = self.sub_cmd(command.Develop.sub_cmd_list, text)

            if not matches:
                # 没有匹配上二级指令
                line_words.insert(1, 'checkout')
                return self.match_develop(text, line_words)

            return matches
        else:
            if line_words[1].startswith('-'):
                line_words.insert(1, 'checkout')

            # 分支或其他
            top_cmd = icommand.real_cmd(line_words[0], raise_err=False)
            sub_cmd = icommand.real_cmd(line_words[1], raise_err=False, top_cmd=top_cmd)

            if not sub_cmd:
                return None

            if top_cmd == iconfig.read_config('system', 'branch')['feature_prefix']:
                branch_prefix = top_cmd + '/' + iglobal.SPRINT + '/'
            else:
                branch_prefix = top_cmd

            if text.startswith('-'):
                return self.match_parameter(sub_cmd, command.Develop.parameters, text)

            if sub_cmd == 'create':
                # 创建分支时，提示远程存在而本地不存在的分支
                return self.match_remoteonly_branch(branch_prefix, text)
            elif sub_cmd == 'product':
                # 此时可能是项目或分支名
                return self.match_project_branch(branch_prefix, text)
            elif sub_cmd == 'checkout':
                iglobal.SILENCE = True
                include_remote = '-r' in line_words or '--remote' in line_words
                match = self.match_branch(branch_prefix, text, include_remote)
                iglobal.SILENCE = False
                return match
            else:
                # 提示分支名
                return self.match_branch(branch_prefix, text)


    def match_remoteonly_branch(self, prefix, text=None):
        """
        匹配远程存在而本地不存在的分支
        :param prefix:
        :param text:
        :return:
        """
        remote_only_branches = list(set(igit.remote_branches(True)) - set(igit.local_branches()))
        return self.__match_branch(prefix, text, remote_only_branches)


    def match_branch(self, prefix, text=None, include_remote=False):
        """
        匹配当前项目的本地分支
        :param bool include_remote: 是否包括远程分支
        :type prefix: str|None
        :param text:
        :return:
        """
        branches = igit.local_branches()
        if include_remote:
            branches = list(set(branches + igit.remote_branches()))

        return self.__match_branch(prefix, text, branches)


    def __match_branch(self, prefix, text, branches):
        if not branches:
            return None

        r_branches = []
        if not text:
            r_branches = list(branches)
        else:
            for branch in branches:
                if branch.startswith(text) or branch.split('/')[-1].startswith(text):
                    r_branches.append(branch)

        matches = filter(lambda x: x.startswith(prefix), r_branches) if prefix else r_branches

        if not matches and prefix:
            # 放宽匹配
            pre = prefix.split('/')
            if len(pre) > 1:
                matches = filter(lambda x: x.startswith(pre[0]), r_branches)

        return matches


    def match_project_branch(self, prefix, text=None):
        projects = map(lambda x: x + ':', ihelper.projects())
        if not text:
            return projects
        elif ':' not in text:
            return filter(lambda x: x.startswith(text), projects)
        else:
            t = text.split(':')
            old_proj = iglobal.PROJECT

            if old_proj != t[0]:
                command.Extra('cd', [t[0]]).execute()

            branches = self.match_branch(prefix, t[1], True)

            if old_proj != iglobal.PROJECT:
                command.Extra('cd', [old_proj]).execute()

            return map(lambda x: t[0] + ':' + x, branches)


    def match_parameter(self, sub_cmd, param_dict, text):
        if not param_dict or (isinstance(param_dict, dict) and sub_cmd not in param_dict) or not text:
            return None

        return map(lambda y: y + ' ', filter(lambda x: x.startswith(text), param_dict[sub_cmd] if isinstance(param_dict, dict) else param_dict))


    def top_cmd(self, word=None):
        """
        根据word获取匹配的一级指令列表
        :param word:
        :return:
        """
        top_list = icommand.top_cmd_list()

        if not word:
            return top_list.keys()

        match = []
        for k, v in top_list.items():
            if str(k).startswith(word):
                match.append(k)
            else:
                for kw in v:
                    if str(kw).startswith(word):
                        match.append(kw)
                        has = 1
                        break

        match = [ele + ' ' for ele in match]
        match.sort()

        return match


    def sub_cmd(self, sub_list, word=None):
        """
        二级指令
        :type sub_list: list
        :type word: str
        :return:
        """
        if not word:
            return list(sub_list)

        alias = iconfig.read_config('system', 'alias')
        matches = []
        for sub in sub_list:
            if sub.startswith(word):
                matches.append(sub)
            else:
                for al, c in alias.items():
                    if c == sub and str(al).startswith(word):
                        matches.append(al)

        matches = map(lambda x: x + ' ', matches)
        matches.sort()

        return matches


def tab():
    readline.set_completer(Completer().complete)
    readline.parse_and_bind('tab: complete')

