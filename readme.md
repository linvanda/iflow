project.json文件格式:






















特性分支
	创建：
	合并到测试分支
	合并到生产分支并销毁，并给master分支打标签

hotfix分支
	创建
	合并到测试分支
	合并到生产分支并销毁，并给master分支打标签

特性分支合并到master后，默认会将最新的master分支合并到尚未发布的跨迭代分支





特性分支的创建：
	git checkout master
	git pull --rebase
	
	feature/1612s1/order-manager
	feature/weigao
	

指令：
	特性分支：
		创建：
			feature c vmember:order-manager -m '订单管理'
			feature c vmember:/1612s2/order-manager	
				会给vmember项目创建feature/1612s2/order-manager分支并推到远程
			feature c vmember:/order-manager
				会给vmember创建feature/order-manager分支（跨迭代分支）
			feature c order-manager
				会给当前目录的项目创建1612s2分支（会提示确认，除非用-cf）
			(c可替换成create)
		发布到测试：
			feature t vmember:order-manager
				会将vmember项目的feature/1612s2/order-manager分支合并到sp-dev分支
				t等价于test
		发布到生产(master):
			feature p vmember:order-manager -i 1612s2
				会将vmember项目的feature/1612s2/order-manager分支合并到master分支，然后删除本地和远程的该分支。多个分支用英文逗号隔开
			feature p vmember,member-center -i 12s2
				将vmember,member-center中1612s2版本的所有迭代分支合并到master上（会提示确认）
			feature p -i 12s2 -t [1612s2.00]
				查找所有的项目，检查相应项目中所有本次迭代的分支，全部合并到master上（会提示确认，列出所有分支，且可输入需要排除的）,同时给master分支打上标签（默认按照版本来）
			feature p vmember:/weigao
				合并跨迭代项目分支feature/weigao 到master上，同时
		撤销发布：
			feature p -r vmember:order-manager -i 1612s2
			或
			feature p -r vmember:/1612s2/order-manager
		删除分支：
			feature d vmember:/1612s2/order-manager
			或
			feature d vmember:order-manager，此时会列出最近迭代号的相应分支提示确认（如果只有一个，则只是提示确认删除分支某某某吗？）

	修复分支：
		同特性分支
		创建:
			fix c vmember:order-delivery -m '订单物流bug'
				会给vmember项目创建hotfix/order-delivery分支
			fix c vmember:order-delivery/kfxt-2278
		其他同特性分支

	打标签
			tag 1612s1
				会给master分支打上标签。如果已经存在以v1612s1开头的标签，则会追加自版本号如v1612s1.03，否则打成v1612s1.00
			tag 12s1会被加上年并提示确认
			标签可以在发布时一同打上，且发布fix时会自动打上

	撤销标签：
		tag -d 1612s1.03

	进入项目：
		cd vmember
			进入vmember项目仓库根目录，后面的操作都基于此目录，直到再次cd，此时，上面的:前面的都可省略

	执行原生git操作：
		git ...
			以git开头的指令会原封不动的执行


其他：
	所有的操作都有日志记录
	退出前记录用户当前所在的目录，下次打开自动进入
	重要操作需要给予提示并要使用者确认
