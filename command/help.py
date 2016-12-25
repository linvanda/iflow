# coding:utf-8

from command import Command


class Help(Command):
    def __init__(self, args):
        Command.__init__(self, args)
        self.name = 'help'
