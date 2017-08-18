ifow版本管理与代码发布工具(公司内部使用)
========================================

##环境：
* **开发语言**：python27
* **操作系统**：win10
* **Git版本**：2.7.2.windows.1

##说明：
* 基于git的用于管理和发布代码分支的windows命令行工具。linux和mac系统未经测试。
* 分支规则：
    1. 有四种分支：生产分支master，测试分支sp-dev，特性分支feature/...，修复分支hotfix/...，其中feature和hotfix分支属于开发过程中的临时分支。
    2. 迭代：一个月通常有两个迭代，分别为sp1,sp2，如1701s1。
    3. 特性分支和迭代密切相关，迭代内特性分支命名：feature/迭代号/特性名称。这种分支是在迭代结束后一起发布的。
    4. 修复分支一般是在一两天内完成并发布的，因为比较紧急而不能随迭代版本发布走。命名：hotfix/名称。
    5. 对一个问题或功能的开发，用哪种分支取决于是要什么时候发布（而不是问题本身属于bug还是特性）。

##使用：
1. 从github clone该仓库
2. 拷贝其中的bin目录到你想放的地方，改成想要的名字。这个目录包含你要的全部东西（其他文件都是源文件之类的）
3. 打开bin/config/文件夹，基于project.sample.json创建一个project.json配置文件，用于配置各个项目信息
4. 双击iflow.exe，运行程序
5. 执行sp指令切换到正确的迭代号
6. 执行cd指令进入到某个项目
7. 使用中可按tab键自动补全相关内容（指令、项目、分支等）
8. 如有疑问，键入help查看帮如

## 注意：
> 不要修改config下的system.json文件，如果确实需要修改其中某些配置，则创建custom.json，按照system.json的格式编写你需要覆盖的内容（深度覆盖）

## 常用指令：
#####（一级、二级指令可使用别名，命令行输入alias查看别名信息）
* **切换到迭代：** sprint 01s1
* **进入项目：** cd vmember（项目名在project.json中配置）
* **创建特性分支：** feature create order-manager
* **创建修复分支：** fix create order-bug
* **发布特性分支到测试环境：** feature test order-manager
* **发布修复分支到测试环境：** fix test order-bug
* **发布特性分支到生产环境：** feature product vmember:* membercenter:order-manager
* **发布修复分支到生产环境：** fix product vmember:order-bug
* **提交当前分支：** commit 修复订单bug
* **切换到另一个特性分支** feature checkout activity
* **切换到另一个修复分支** feature checkout activity-bug
* **特性分支转修复分支：** f2h order-manager
* **整理合并本迭代所有sql文件：** sql
* **打tag：** tag -m 修改bug
* **显示tag列表：** tag
* **根据正则模式删除branch：** del feature/17.*
* **仅删除本地分支：** del --no-remote tag_pattern
* **Git原生指令：** git ...
* **清屏：** clear
* **退出程序：** exit
* ...

####更多指令使用说明请命令行输入help查看，另外如输入help feature可查看feature指令的使用说明

## 源码开发：
> windows上基于源码开发的话需安装pyreadline,pyinstall,pywin32,pefile模块，并将python目录下的scripts目录加入到系统环境变量，开发完成后用一下命令打包成可执行文件：
（先进入到项目根目录）
pyinstaller iflow.py --distpath=./bin -i iflow.ico -F

欢迎使用和提bug!