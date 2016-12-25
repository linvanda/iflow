# coding:utf-8

import abc


class Command(object):
    def __init__(self, args):
        self.args = args
        self.name = ''

    @abc.abstractmethod
    def execute(self):
        pass

    def __str__(self):
        return self.name + ' ' + ' '.join(self.args)
