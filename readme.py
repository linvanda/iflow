# coding:utf-8
"""
命令行帮助文档
"""
import collections

help = collections.OrderedDict()

help['feature'] = {
        'title':u'--特性分支-----------------------------------------------------------------------------',
        'desc': u'别名：ft=feature, c=create, t=test, p=product, d=delete, ck=checkout',
        'content': u"""ft c order-manager                在当前项目创建feature/1612s2/order-manager特性分支
ft c /1701s2/order-manager        在当前项目创建feature/1701s2/order-manager分支
ft c /order-manager               在当前项目创建夸迭代feature/order-manager分支
ft t                              将当前项目的当前分支合并到测试分支
ft t order-manager                将当前项目的feature/1612s2/order-manager分支合并到测试分支
ft p                              将所有项目的所有当前迭代的分支合并到生产分支
ft p vmember member-center:*      将vmember和member-center项目的所有特性分支合并到生产分支
ft p vmember:/weigao              将vmember的feature/weigao分支合并到生产分支
ft d --no-push order-manager      删除feature/1612s2/order-manager分支，但不删除对应的远程分支
ft d -y order-manager             删除feature/1612s2/order-manager分支且推送到远程，且不需要确认提示
ft                                等同于ft ck <当前分支>（检查远程仓库有无更新）
ft order-manager                  等同于ft ck order-manager
ft ck order-manager               切换到feature/1612s2/order-manager分支(如果本地没有但远程有则基于远程创建本地分支)
ft ck -r order-manager            同ft ck order-manager，但tab键会提示远程分支名
ft ck                             检查当前分支的远程分支是否有更新
"""
}

help['hotfix'] = {
        'title': u'--修复分支----------------------------------------------------------------------------',
        'desc': u'别名：fix=hotfix, c=create, t=test, p=product, d=delete, ck=checkout',
        'content': u"""fix c order-bug                    在当前项目创建hotfix/order-bug修复分支
fix t                              将当前项目的当前分支合并到测试分支
fix t order-bug                    将当前项目的hotfix/order-bug分支合并到测试分支
fix p                              将所有项目的所有修复分支合并到生产分支
fix p vmember member-center:*      将vmember和member-center项目的所有修复分支合并到生产分支
fix p vmember:order-bug            将vmember的hotfix/order-bug分支合并到生产分支
fix d --no-push order-bug          删除hotfix/order-bug分支，但不删除对应的远程分支
fix d -y order-bug                 删除hotfix/order-bug分支并推送到远程，且不需要确认提示
fix                                等同于fix ck <当前分支>（检查远程仓库有无更新）
fix order-bug                      等同于fix ck order-bug
fix ck order-bug                   切换到hotfix/order-bug分支(如果本地没有但远程有则基于远程创建本地分支)
fix ck -r order-bug                同fix ck order-bug，但tab键会提示远程分支名
fix ck                             检查当前分支的远程分支是否有更新
"""
}

help['transform'] = {
        'title': u'--分支转换----------------------------------------------------------------------------',
        'desc': u'别名：-n=--next, -s=--sprint',
        'content':u"""h2f order-bug               将修复分支hotfix/order-bug转为本迭代的特性分支feature/1612s2/order-bug
h2f order-bug -n            将修复分支hotfix/order-bug转为下个迭代的特性分支feature/1701s1/order-bug
h2f order-bug -s 1702s1     将修复分支hotfix/order-bug转为指定迭代的特性分支feature/1702s1/order-bug
f2h order-mgr               将特性分支feature/1612s2/order-mgr转为修复分支hotfix/order-mgr
f2f order-mgr               将特性分支feature/1612s2/order-mgr转为下个迭代的特性分支feature/1701s1/order-mgr
f2f order-mgr -s 1702s1     将特性分支feature/1612s2/order-mgr转为指定迭代的特性分支feature/1702s1/order-mgr
"""
}

help['h2f'] = 'transform'
help['f2h'] = 'transform'
help['f2f'] = 'transform'

help['org_git'] = {
        'title': u'--Git操作-----------------------------------------------------------------------------',
        'content':u"""git ...                               git原生指令
commit 取消订单的bug修复              提交（会自动add）
commit -p 取消订单的bug修复           提交并推送到远程仓库
tag -a mytagname -m comment          在生产分支打标签(可忽略-a参数，此时系统自动生成tag名称)
del tag_pattern                      删除匹配tag_pattern正则的分支，同时删除远程相应分支
rename hotfix/order-bug hotfix/order-refund
                                      分支重命名（同时更新远程仓库，注意此处需要写分支全名）
"""
}

help['git'] = 'org_git'
help['commit'] = 'org_git'
help['rename'] = 'org_git'

help['extra'] = {
        'title': u'--其他指令----------------------------------------------------------------------------',
        'desc': u'别名：sp=sprint',
        'content': u"""cd vmember              进入vmember项目的git仓库根目录
sp 01s1                 切换到1701s1迭代
sql                     本迭代的sql文件整理和下载（由系统或项目配置项sql_branch指定从哪个分支获取）
pwd                     当前所在目录
exit                    退出程序
alias                   查看所有可用的别名列表（一级、二级）
clear                   清屏
"""
}

help['sprint'] = 'extra'
help['sql'] = 'extra'
help['pwd'] = 'extra'
help['exit'] = 'extra'
help['alias'] = 'extra'
