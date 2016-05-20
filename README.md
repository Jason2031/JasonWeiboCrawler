#JasonWeiboCrawler

###提供cookies爬取特定用户或关键词的爬虫
-----------------
author:Jason Wood

email:wujiecheng@bupt.edu.cn

[项目介绍](http://blog.csdn.net/Jason2031/article/details/48698829)

------------------
开发环境：

* Mac OSX 10.11.3
* Python 2.7

依赖库：

* lxml
* urllib
* request

安装方法：
sudo pip install lxml urllib request

-----------------
### 使用方法
	python main.py xxxx@xx.xxx (password) (m/s) [(trycount) (thread control)]
##*特别注意*
该分支的爬虫默认爬取的用户为所提供的账号，顾不需要再提供displayID

参数解释：

1. argv[0]:文件名（必填）
2. argv[1]:新浪微博登录名（通常为邮箱，必填）
3. argv[2]:登录密码（必填）
4. argv[3]:线程模式，m代表多线程，s代表单线程（必填）
5. argv[4]:尝试阈值，同一尝试次数超过该阈值时线程退出，防止程序陷入死循环（选填，默认为20）
6. argv[5]:多线程控制，仅在argv[5]为m时有用，用于指定多线程中单个线程下载的微博页面数（选填，默认为10）

----------------------
本来这个程序不怎么需要输出信息的，但是开发前期觉得不输出点什么感觉程序好像陷入了死循环，所以就每爬取一个页面就显示完成进度。

另外，程序最后会输出两行，一行显示True或者False。True表示爬取过程很顺利，没有丢失页面，否则显示False；第二行是Done！表示程序结束。

解析的结果将存在/Weibo_parsed/文件夹里，以用户displayID为命名的.txt文件；关键词结果存在/keyword/文件夹里，以关键词为命名的.txt文件。而/Weibo_raw/是过渡文件夹，用来存爬取成功但未解析的微博页面文件，程序自动删除，若希望保留，只需注释掉main.py第83行的clean()方法调用即可。

-------------------
写在后面：

使用他人的劳动成果时最好先征得他人的同意，但是如果你觉得我比较帅，就可以不用征得我的同意啦hhh
如果您觉得好用，请给与我鼓励，如果您觉得不好用，或者爬虫已经失效，请发邮件告诉我。
