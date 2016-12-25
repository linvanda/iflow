# coding:utf-8

from command import Command


class HotFix(Command):
    def __init__(self, args):
        Command.__init__(self, args)
        self.name = 'hotfix'
