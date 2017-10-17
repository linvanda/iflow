# coding:utf-8

import command
import iglobal
import os

iglobal.BASE_DIR = os.getcwd().replace('\\', '/')

command.Command.exec_hook('product', 'post', 'vmember')
