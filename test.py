# coding:utf-8

import time
import ihelper
import iglobal


def __workspace_match_status(text, status):
    for search_str in iglobal.GIT_STATUS_PATTEN[status]:
        if search_str in text:
            return status

    return 0

__status = 0
out = 'this is'
for s_code, patterns in iglobal.GIT_STATUS_PATTEN.items():
	print patterns


