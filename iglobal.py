# coding:utf-8

# 操作系统编码
FROM_ENCODING = 'gb2312'
# 软件基目录
BASE_DIR = None
# 当前项目
PROJECT = 'global'
# 当前迭代
SPRINT = 'none'
# 静音模式
SILENCE = False
# 是否开启tab提示
READLINE = True

"""
Git状态
"""
# 干净
GIT_CLEAN = 1
# 合并或pull冲突
GIT_CONFLICT = 2
# 尚有未staged的内容
GIT_UNSTAGED = 4
# 有待提交内容
GIT_UNCOMMITED = 8
# ahead
GIT_AHEAD = 16
# behind
GIT_BEHIND = 32
# rebasing
GIT_REBASING = 64
# cherry-pick
GIT_CHERRING = 128
# merging
GIT_MERGING = 256
# diverged
GIT_DIVERGED = 512

GIT_STATUS_MAP = {
    1: 'clean',
    2: 'conflict',
    4: 'unstaged',
    8: 'uncommited',
    16: 'ahead',
    32: 'behind',
    64: 'rebasing',
    128: 'cherring',
    256: 'merging',
    512: 'diverged'
}

