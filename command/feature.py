# coding:utf-8

from command import Command


class Feature(Command):
    def __init__(self, args):
        Command.__init__(self, args)
        self.name = 'feature'

    def execute(self):
        print 'execute here'
