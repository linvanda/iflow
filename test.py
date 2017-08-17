# coding:utf-8

import time
import ihelper


input_tag = 'v1708s1.01'
ihelper.execute('git tag -a %s -m "normal publish"' % input_tag, raise_err=True)
# ihelper.execute('git push origin %s' % input_tag, raise_err=True)
