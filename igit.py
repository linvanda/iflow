# coding:utf-8

import os


def get_config(key = None):
    config = dict(map(lambda x:x.split('='), os.popen('git config -l').read().splitlines()))
    return config[key] if key and config.has_key(key) else config


def get_current_branch():
    branch = filter(lambda x:x.find('*') != -1, os.popen('git branch').read().splitlines())
    return branch[0].replace('*', '').strip() if branch else None