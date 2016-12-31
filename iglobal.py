# coding:utf-8

# 操作系统编码
FROM_ENCODING = 'gb2312'
# 软件基目录
BASE_DIR = None
# 当前项目
PROJECT = 'global'
# 当前迭代
SPRINT = 'none'

"""
Git状态
"""
# 干净
GIT_CLEAN = (1, 'clean')
# 合并或pull冲突
GIT_CONFLICT = (2, 'conflict')
# 有待提交内容
GIT_UNCOMMITED = (4, 'uncommited')
# 尚有未staged的内容
GIT_UNSTAGED = (8, 'unstaged')

